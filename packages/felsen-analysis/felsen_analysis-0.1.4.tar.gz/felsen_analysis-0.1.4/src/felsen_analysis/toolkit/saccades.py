import numpy as np
from felsen_analysis.toolkit.process import AnalysisObject
import math
from scipy import stats


def parseSaccadeType(h5file):
    """
    This function determines which saccades are spontaneous and which are driven
    and returns both arrays
    """
    session = AnalysisObject(h5file)
    start = session.load('stimuli/dg/grating/timestamps')
    stop = session.load('stimuli/dg/iti/timestamps')
    saccades = session.load('saccades/predicted/left/timestamps')[:, 0]
    spontaneous = list()
    driven = list()
    for i, stopTime in enumerate(stop):
        try:
            startTime = start[i + 1]
        except:
            continue
        mask = np.logical_and(saccades > stopTime, saccades < startTime)
        masked = saccades[mask]
        if masked.any():
            masked = list(masked)
            for element in masked:
                spontaneous.append(element)

    spontaneous = np.array(spontaneous)
    driven = list()
    for sac in saccades:
        if sac not in spontaneous:
            driven.append(sac)
    driven = np.array(driven)
    return driven, spontaneous

def calculateSaccadeAmplitudes(h5file, saccades):
    """
    Input either driven or spontaneous saccades and calculate their amplitudes
    """
    session = AnalysisObject(h5file)
    pose = session.load('pose/filtered')
    frameTimes = session.load('frames/left/timestamps')
    totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        subsetIndices.append(np.where(totalSaccadeTimes == time)[0])
    amplitudes = list()
    for sac in subsetIndices:
        startIndex = sac
        endTime = session.load('saccades/predicted/left/timestamps')[sac, 1]
        if endTime.size != 1:
            amplitudes.append(0)
            continue
        relativeEnd = abs(frameTimes - endTime)
        endShape = np.where(relativeEnd == np.min(relativeEnd))[0].shape[0]
        if endShape == 2:
            endIndex = np.where(relativeEnd == np.min(relativeEnd))[0][0]
        else:
            endIndex = int(np.where(relativeEnd == np.min(relativeEnd))[0])
        startPoint = pose[startIndex, 0]
        endPoint = pose[endIndex, 0]
        amplitude = abs(endPoint - startPoint)
        amplitudes.append(float(amplitude))
    return amplitudes

def calculateSaccadeStartPoint(h5file, saccades):
    """
    Input either driven or spontaneous saccades and calculate their start point
    """
    session = AnalysisObject(h5file)
    pose = session.load('pose/filtered')
    frameTimes = session.load('frames/left/timestamps')
    totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        subsetIndices.append(np.where(totalSaccadeTimes == time)[0])
    startPoints = list()
    for sac in subsetIndices:
        startIndex = sac
        startPoint = pose[startIndex, 0]
        if startPoint.size != 1:
            startPoints.append(0)
        else:
            startPoints.append(float(startPoint))
    return startPoints

def calculateSaccadeEndPoint(h5file, saccades):
    """
    Input either driven or spontaneous saccades and calculate their end point
    """
    session = AnalysisObject(h5file)
    pose = session.load('pose/filtered')
    frameTimes = session.load('frames/left/timestamps')
    totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        subsetIndices.append(np.where(totalSaccadeTimes == time)[0])
    endPoints = list()
    for sac in subsetIndices:
        endTime = session.load('saccades/predicted/left/timestamps')[sac, 1]
        if endTime.size != 1:
            endPoints.append(0)
            continue
        relativeEnd = abs(frameTimes - endTime)
        endShape = np.where(relativeEnd == np.min(relativeEnd))[0].shape[0]
        if endShape == 2:
            endIndex = np.where(relativeEnd == np.min(relativeEnd))[0][0]
        else:
            endIndex = int(np.where(relativeEnd == np.min(relativeEnd))[0])
        endPoint = pose[endIndex, 0]
        endPoints.append(float(endPoint))
    return endPoints

def computeNormalizedFiringRate(h5file, unitsToAnalyze, events, window):
    """
    Compute & Z-score the firing rate of all neurons for all saccades
    """
    session = AnalysisObject(h5file)
    population = session._population()
    FRlist = np.zeros((len(unitsToAnalyze), len(events)))
    for i, event in enumerate(events):
        j = 0
        for unit in population:
            if unit.cluster not in unitsToAnalyze:
                continue
            spikeTimes = unit.timestamps
            start = events[i] + window[0]
            end = events[i] + window[1]
            mask = np.logical_and(spikeTimes > start, spikeTimes < end)
            activity = len(spikeTimes[mask])/0.3
            FRlist[j, i] = activity
            j = j+1
    z = stats.zscore(FRlist, axis=1, nan_policy='omit')
    return z

def binFiringRatesbyMetric(z, ampList, startList, endList, unit):
    """
    Puts firing rates for all saccades for a given unit into bins, split up by metrics
    Preps data to plot a single unit example of firing rate by saccade metric
    But we bin it so we can actually see stuff or else it looks gross and incomprehensible
    Yes I know returning 6 things is a crime
    """
    ampAvg = list()
    startAvg = list()
    endAvg = list()
    a = sorted(ampList)
    s = sorted(startList)
    e = sorted(endList)
    lists = [ampList, startList, endList]
    binStartA = list()
    binStartS = list()
    binStartE = list()
    for i, feature in enumerate([a, s, e]):
        bins = np.arange(0, len(feature), len(feature)/50)
        for k in bins:
            j = int(k)
            values = feature[j:int(j+len(feature)/50)]
            inds = list()
            for value in values:
                ind = np.where(lists[i] == value)[0]
                if ind.shape != (0,):
                    inds.append(ind)
            data = z[unit, inds]
            avg = np.nanmean(data)
            if i == 0:
                ampAvg.append(avg)
                binStartA.append(np.min(values))
            elif i == 1:
                startAvg.append(avg)
                binStartS.append(np.min(values))
            elif i == 2:
                endAvg.append(avg)
                binStartE.append(np.min(values))
    return ampAvg, startAvg, endAvg, binStartA, binStartS, binStartE

def generateSaccadeMetricArray(h5file, ampList, startList, endList):
    """
    Assemble all saccade metrics into 1 array for ease of use
    Required for using the prediction module
    """
    session = AnalysisObject(h5file)
    sacMetrics = np.zeros((len(ampList), 3))
    sacMetrics[:, 0] = ampList
    sacMetrics[:, 1] = startList
    sacMetrics[:, 2] = endList
    return sacMetrics
