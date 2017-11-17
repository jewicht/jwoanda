from __future__ import print_function
import inspect
import logging

from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn import svm
from sklearn.neural_network import MLPRegressor
import sklearn.metrics as metrics

import matplotlib.pyplot as plt
import numpy as np


def mysplitter(X, y, splitbyweek=False, times=None):
    seed = 42
    test_size = 0.4
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

    if not splitbyweek:
        X_train = X[0:int((1. - test_size) * len(X))]
        y_train = y[0:int((1. - test_size) * len(X))]
        X_test = X[-int(test_size * len(X)):]
        y_test = y[-int(test_size * len(X)):]
        #indices = [i < (1.- test.size)*len(X) for i in range(len(X))]
        return X_train, X_test, y_train, y_test
    else:
        #separate by even / odd week
        indices = [datetime.fromtimestamp(_time).isocalendar()[1] % 2 == 0 for _time in times]
        
        X_train = X[indices]
        y_train = y[indices]
        X_test = X[np.logical_not(indices)]
        y_test = y[np.logical_not(indices)]
        return X_train, X_test, y_train, y_test


def mypred(model, X, scaler=None):
    if scaler is not None:
        y_pred = model.predict(scaler.transform(X))
    else:
        y_pred = model.predict(X)

    if inspect.isgenerator(y_pred):
        y_pred = list(y_pred)
    return y_pred


def calcAccuracy_regression2(model, d, scaler=None, plot=True):
    for datatype in ['train', 'test']:
        logging.info("Analyzing datatype = %s ", datatype)
        y_pred = mypred(model, d[datatype]['X'], scaler)

        predictions = [np.sign(value) for value in y_pred]
        # evaluate predictions
        try:
            accuracy = metrics.accuracy_score(d[datatype]['y'], predictions)
            logging.info("   accuracy = %.2f%%", accuracy * 100.)
        except:
            pass
        logging.info("   r2 = %.2f", metrics.r2_score(d[datatype]['y'], y_pred))
        try:
            score = model.score(d[datatype]['X'], d[datatype]['y'])
            logging.info("   score = %.2f", score)
        except:
            pass

    if not plot:
        return

    fig, ax = plt.subplots(2)

    y_test_pred = mypred(model, d['test']['X'], scaler)
    y_train_pred = mypred(model, d['train']['X'], scaler)

    y_test = d['test']['y']
    y_train = d['train']['y']

    #a0 = y_test_pred[y_test == +1]
    #b0 = y_test_pred[y_test == -1]
    ax[1].set_title("test data")
    ax[1].scatter(y_test, y_test-y_test_pred)
    #ax[1].hist(a0, 100, range=[-1.5, 1.5], normed=1, facecolor='green', alpha=0.75)
    #ax[1].hist(b0, 100, range=[-1.5, 1.5], normed=1, facecolor='red', alpha=0.75)

    #a1 = y_train_pred[y_train == +1]
    #b1 = y_train_pred[y_train == -1]
    ax[0].set_title("train data")
    ax[0].scatter(y_train, y_train-y_train_pred)
    #ax[0].hist(a1, 100, range=[-1.5, 1.5], normed=1, facecolor='green', alpha=0.75)
    #ax[0].hist(b1, 100, range=[-1.5, 1.5], normed=1, facecolor='red', alpha=0.75)

    plt.show()


def calcAccuracy_regression(model, d, scaler=None, plot=True):
    for datatype in ['train', 'test']:
        logging.info("Analyzing datatype = %s ", datatype)
        y_pred = mypred(model, d[datatype]['X'], scaler)

        predictions = [np.sign(value) for value in y_pred]
        # evaluate predictions
        try:
            accuracy = metrics.accuracy_score(d[datatype]['y'], predictions)
            logging.info("   accuracy = %.2f%%", accuracy * 100.)
        except:
            pass
        logging.info("   r2 = %.2f", metrics.r2_score(d[datatype]['y'], y_pred))
        try:
            score = model.score(d[datatype]['X'], d[datatype]['y'])
            logging.info("   score = %.2f", score)
        except:
            pass

    if not plot:
        return

    fig, ax = plt.subplots(2, 2)

    y_test_pred = mypred(model, d['test']['X'], scaler)
    y_train_pred = mypred(model, d['train']['X'], scaler)

    y_test = d['test']['y']
    y_train = d['train']['y']

    hlist = []
    ax[0, 0].set_title("train data")
    n, bins, patches = ax[0, 0].hist(y_train_pred[y_train > 0.], 100, range=[-1.5, 1.5], normed=1, facecolor='green', alpha=0.5, label='+1')
    hlist.append(patches[0])
    n, bins, patches = ax[0, 0].hist(y_train_pred[y_train < 0.], 100, range=[-1.5, 1.5], normed=1, facecolor='red', alpha=0.5, label='-1')
    hlist.append(patches[0])
    ax[0, 0].legend(handles=hlist)

    hlist = []
    ax[0, 1].set_title("test data")
    n, bins, patches = ax[0, 1].hist(y_test_pred[y_test > 0.], 100, range=[-1.5, 1.5], normed=1, facecolor='green', alpha=0.5, label='+1')
    hlist.append(patches[0])
    n, bins, patches = ax[0, 1].hist(y_test_pred[y_test < 0.], 100, range=[-1.5, 1.5], normed=1, facecolor='red', alpha=0.5, label='-1')
    hlist.append(patches[0])
    ax[0, 1].legend(handles=hlist)
    
    #ax[1, 1].set_title("test data")
    ax[1, 1].scatter(y_test, y_test-y_test_pred)

    #ax[1, 0].set_title("train data")
    ax[1, 0].scatter(y_train, y_train-y_train_pred)

    plt.show()


def calcAccuracy_classification(model, d, scaler=None, plot=True):
    for datatype in ['test', 'train']:
        logging.info("Analyzing datatype = %s ", datatype)

        y_pred = mypred(model, d[datatype]['X'], scaler)

        predictions = [np.sign(value) for value in y_pred]
        # evaluate predictions
        accuracy = metrics.accuracy_score(d[datatype]['y'], predictions)
        logging.info("   accuracy = %.2f%%", accuracy*100.)
        logging.info("   f1 = %.2f", metrics.f1_score(d[datatype]['y'], y_pred, average=None))
        logging.info("   confusion matrix = \n {}".format(metrics.confusion_matrix(d[datatype]['y'], y_pred)))
        try:
            score = model.score(d[datatype]['X'], d[datatype]['y'])
            logging.info("   score = %.2f", score)
        except:
            pass


def trainSKAdaBoost(X, y):
    dt = DecisionTreeRegressor(max_depth=4)#,
                               #min_samples_leaf=0.05*len(X))
    clf = AdaBoostRegressor(dt,
                            #algorithm='SAMME',
                            n_estimators=400,
                            learning_rate=0.5)

    clf.fit(X, y)
    print(clf.feature_importances_)

    return clf


def trainSKMLP(X, y):
    a, b = X.shape
    clf = MLPRegressor(activation='tanh', alpha=1e-5, hidden_layer_sizes=(b, int(b/2)), random_state=1)
    clf.fit(X, y)
    return clf


def trainSKSVM(X, y):
    clf = svm.SVR()
    clf.fit(X, y)
    return clf
