'''
'''

import time
import pandas as pd
from sklearn import linear_model
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from linxgb import linxgb, make_polynomial_features
from metrics import *
from test_func import *
from test_plot import *

def compute(train_X,train_Y,test_X,test_Y):
    # CV parameters
    cv_sets = KFold(n_splits=3, shuffle=True, random_state=1)

    # least-square fit
    reg = linear_model.LinearRegression()
    reg.fit(train_X,train_Y)
    lsf_pred_Y = reg.predict(test_X)

    # CV for XGBoost
    param_grid = { "n_estimators": np.arange(170,226,5), # 48
                   "learning_rate": [0.1,0.15,0.2], # 0.2
                   "min_child_weight": np.arange(2,4), # 5
                   "max_depth": np.arange(4,13,2), # 2
                   "subsample": np.linspace(0.7,0.9,3), # 0.6
                   "gamma": [ 0.03, 0.1, 0.3 ] # 0.1
                  }
    grid_cv = GridSearchCV(xgb.XGBRegressor(objective='reg:squarederror', reg_lambda=0., nthread=1), param_grid, scoring='neg_mean_squared_error', cv=cv_sets, iid=True, n_jobs=-1)
    grid_cv.fit(train_X, train_Y)
    #reg = grid_cv.best_estimator_
    #reg.fit(train_X, train_Y)
    xgb_pred_Y = grid_cv.predict(test_X)

    # CV for LinXGBoost
    param_grid = { #"learning_rate": [0.8,0.9],
                   "gamma": [ 1, 100, 10000, 1e6 ],
                   #"lbda": np.logspace(-11,-4,num=2),
                   "min_samples_leaf": [32,48],
                  }
    grid_cv = GridSearchCV(linxgb(max_depth=200,n_estimators=4,learning_rate=1.0,lbda=1e-11), param_grid, scoring='neg_mean_squared_error', cv=cv_sets, iid=True, n_jobs=-1)
    grid_cv.fit(train_X, train_Y)
    #reg = grid_cv.best_estimator_
    #reg.fit(train_X, train_Y)
    lin_pred_Y = grid_cv.predict(test_X)

    # CV for Random Forest
    param_grid = { "n_estimators": np.arange(110,151,5), # 69 or 78
                   "min_samples_leaf": np.arange(1,3), # 1
                   "min_samples_split": np.arange(2,5), # 4 or 3
                   "max_depth": np.arange(16,29,2), # 24
                  }
    grid_cv = GridSearchCV(RandomForestRegressor(random_state=1), param_grid, scoring='neg_mean_squared_error', cv=cv_sets, iid=True, n_jobs=-1)
    grid_cv.fit(train_X, train_Y)
    #reg = grid_cv.best_estimator_
    #reg.fit(train_X, train_Y)
    rf_pred_Y = grid_cv.predict(test_X)

    return nmse(test_Y,lsf_pred_Y), nmse(test_Y,xgb_pred_Y), nmse(test_Y,lin_pred_Y), nmse(test_Y,rf_pred_Y)


if __name__ == '__main__':

    # Read Excel sheets
    df = pd.read_excel('ccpp.xlsx')
    multivariate_outliers1 = df[ (df["V"]<30) | (df["PE"]<424) ].index.tolist()
    multivariate_outliers2 = df[ (df["V"]>70) & (df["V"]<73) & (df["PE"]>450) & (df["PE"]<480) ].index.tolist()
    multivariate_outliers = multivariate_outliers1 + multivariate_outliers2
    new_df = df.drop(df.index[multivariate_outliers]).reset_index(drop = True)
    data = new_df.values
    print(data.shape)
    features = data[:,:-1]
    features = features - np.mean(features,axis=0)
    target = data[:,-1]

    # predictions

    lsf_perf = []
    xgb_perf = []
    lin_perf = []
    rf_perf = []

    for k in range(0,20):
        print("starting {}-th iteration".format(k+1))

        np.random.seed(k)

        # Training & testing sets
        train_X, test_X, train_Y, test_Y = train_test_split(features, target, test_size=0.3, random_state=k)

        # predictions
        lsf_nmse, xgb_nmse, lin_nmse, rf_nmse = compute(train_X,train_Y,test_X,test_Y)

        # bookkeeping
        lsf_perf.append(lsf_nmse)
        xgb_perf.append(xgb_nmse)
        lin_perf.append(lin_nmse)
        rf_perf.append(rf_nmse)

        # print perf
        print("NMSE: LSF {:12.5f} XGBoost {:12.5f} LinXGBoost {:12.5f} Random Forests {:12.5f}". \
               format(lsf_nmse,xgb_nmse,lin_nmse,rf_nmse) )

    # Print stats
    print("LSF           : {:12.5f} +/- {:12.5f}".format(np.mean(lsf_perf),np.std(lsf_perf,ddof=1)) )
    print("XGBoost       : {:12.5f} +/- {:12.5f}".format(np.mean(xgb_perf),np.std(xgb_perf,ddof=1)) )
    print("LinXGBoost    : {:12.5f} +/- {:12.5f}".format(np.mean(lin_perf),np.std(lin_perf,ddof=1)) )
    print("Random Forests: {:12.5f} +/- {:12.5f}".format(np.mean(rf_perf),np.std(rf_perf,ddof=1)) )
