from felsen_analysis.toolkit.process import AnalysisObject
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def predictSaccadeMetrics(trialsToAnalyze, z, sacMetrics):
    """
    This function uses linear regression to predict trial-by-trial saccade metrics based on activity of a given population
    You give it a list of trials (for example, all contralateral saccades in a session) and arrays with firing rate (from your population) and saccade metric info
    It returns an array with the predicted values for each trial based on the population activity, as well as a score for prediction accuracy
    """
    idxs = np.random.permutation(range(0, len(trialsToAnalyze)))
    train_half = idxs[:len(trialsToAnalyze)//2]
    test_half = idxs[len(trialsToAnalyze)//2:]
    sacMetrics[np.isnan(sacMetrics)] = 0
    model = LinearRegression()
    model.fit(z[:, train_half].T, sacMetrics[train_half, :])
    predicted = model.predict(z[:, test_half].T)
    scoreTrain = model.score(z[:, train_half].T, sacMetrics[train_half, :])
    scoreTest = model.score(z[:, test_half].T, sacMetrics[test_half, :])
    return predicted, scoreTrain, scoreTest, test_half

def plotPredictedVSActual(predicted, actual, metric, color, min, max, fig=None, ax=None):
    """
    This makes a scatter plot of predicted vs actual values to visually evaluate prediction results
    """
    params = {'legend.fontsize': 15,
         'axes.labelsize': 20,
         'axes.titlesize':15,
         'xtick.labelsize':15,
         'ytick.labelsize':15}
    plt.rcParams.update(params)
    if fig is None:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    if metric == 'amplitude':
        index = 0
    elif metric == 'start':
        index = 1
    elif metric == 'end':
        index = 2
    else:
        print("enter a real metric u silly person. check generateSaccadeMetric function if confused")
    ax.scatter(np.array(actual), predicted[:, index], color=color, alpha=0.5, s=7)
    ax.plot([min, max], [min, max], color='k')
    return fig, ax
    
