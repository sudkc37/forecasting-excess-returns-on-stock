# -*- coding: utf-8 -*-
"""HyperParameter-tuning-and-forecasting-excess-returns-on-stock .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dheD2PZ5YtfeB-knuhAXOG9xhbfCD750
"""

!wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
!ls
!tar xvzf ta-lib-0.4.0-src.tar.gz
!ls

import os
os.chdir('ta-lib')
!./configure --prefix=/usr
!make
!make install

os.chdir('../')
!ls
!pip install TA-Lib

!pip install TA-Lib

!python --version

!sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV, Lasso, LassoCV, ElasticNet, ElasticNetCV
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures, add_dummy_feature
#import talib
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')
from scipy.stats.stats import pearsonr

from google.colab import drive
drive.mount('/content/drive')

data = pd.read_csv('/content/drive/My Drive/characteristics_anom.csv')
#data = data.set_index(['permno','date'])

data.head()

for datas in data:
  for j in datas:
    data['5m_close_pct'] = data['price'].pct_change(5).values
    data['5m_future_close'] = data['price'].shift(-5).values
    data['5m_future_close_pct'] = data['5m_future_close'].pct_change(5).values
    data['5_ma'] = talib.SMA(data['price'].values, timeperiod= 5) / data['price']
    data['5m_rsi'] = talib.RSI(data['price'].values, timeperiod=5)
    data = data.dropna()

A = data.loc[10006]
print(A.shape)
print(A)

"""Seperting df for train and test based on year"""

data['year'] = data['date'].str[-4:]
data['year'].astype(int)

data_2005 = data[data['year'] >= '2005']
data_2005 = data_2005.set_index(['permno','date', 'year'])
data_2005.head()

data.head()

data = data.set_index(['permno', 'date', 'year'])
data.head()

corr = data.corr()
fig, ax=plt.subplots(figsize=(45,40))
mask = np.triu(np.ones_like(corr, dtype=bool))
cmap = sns.diverging_palette(250, 30, as_cmap=True)
sns.heatmap(corr, annot=True, mask = mask, cmap=cmap)

X = data.drop("re", axis=1)
y = data['re']
X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, random_state=0, test_size=0.2)

X_2005 = data_2005.drop('re', axis=1)
y_2005 = data_2005['re']
X_train_2005, X_test_2005, y_train_2005, y_test_2005 = train_test_split(X_2005, y_2005, shuffle=False, random_state=0, test_size=0.2)

lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)
y_pred = lin_reg.predict(X_test_2005)
print('Predictions: {}'.format(y_pred[:2]))
print('Actual Values: {}'.format(y_test_2005[:2]))

#R_squared_linear = lin_reg(X_test, y_test)
mse = mean_squared_error(y_test_2005, y_pred)
Rmse = mse**0.2
#print("R_squared:{}".format(R_squared_linear))
print("Mean Squared Error:{}".format(mse))
print("Root Mean Squared Error:{}".format(Rmse))



"""Ridge Regression"""

alphas = 10**np.linspace(2,0.1,30)
ridgecv = RidgeCV(alphas=alphas, cv=5, fit_intercept=True)
ridgecv.fit(X_train, y_train)
mean_sq_error = mean_squared_error(y_test_2005, ridgecv.predict(X_test_2005))
R_squared_ridge = ridgecv.score(X_train, y_train)
print('Mean Squared Error:{}' .format(mean_sq_error))
print('Root Mean Squared Error:{}' .format(mean_sq_error**0.5))
print('R_squared:{}'.format(R_squared_ridge))

ridgecv.alpha_

ridge = Ridge(fit_intercept=True)
alphas = 10**np.linspace(9,0.1,100)*0.5
coefs = []

for a in alphas:
  ridge.set_params(alpha=a)
  ridge.fit(X_train, y_train)
  coefs.append(ridge.coef_)

plt.figure(figsize=(16,10))
ax= plt.gca()
ax.plot(alphas, coefs)
ax.set_xscale('log')
plt.axis('tight')
plt.xlabel('alpha')
plt.ylabel('Standard Coefficient')
plt.title('Ridge coefficients as a function of the Regularization ')
plt.legend(X.columns)

"""Lasso Regression

"""

from sklearn.model_selection import GridSearchCV

features = X.columns
features

lasso = Lasso(fit_intercept=True)
las = GridSearchCV(lasso,
                   {'alpha':np.linspace(0.0002, 2, num=10)}, cv=5, scoring='neg_mean_squared_error', verbose=2)
las.fit(X_train,y_train)
las.best_params_

lasso = Lasso(alpha=0.0002)
lasso.fit(X_train, y_train)
mean_sq_error_lasso = mean_squared_error(y_test_2005, lasso.predict(X_test_2005))
R_squared_lasso = lasso.score(X_train, y_train)
print('Mean Squared Error:{}' .format(mean_sq_error_lasso))
print('Root Mean Squared Error:{}'.format(mean_sq_error_lasso**0.5))
print('R_squared:{}'.format(R_squared_lasso))

"""Random Forest"""

from sklearn.model_selection import ParameterGrid
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

rfr = RandomForestRegressor()
#n_estimators = np.linspace(20, 100, num=8)
#max_depth = np.linspace(5, 10, num=5)
#max_features = np.linspace(2, 20, num=10)
n_estimators =[10,20]
max_depth = [6,8]
max_features =[6,7,10]

rfr = RandomForestRegressor()
grid = {'n_estimators':n_estimators,
        'max_depth':max_depth,
        'max_features':max_features}
test_score = []
for i in ParameterGrid(grid):
  rfr.set_params(**i)
  rfr.fit(X_train, y_train)
  test_score.append(rfr.score(X_train, y_train))
  best_index = np.argmax(test_score)
ParameterGrid = ParameterGrid(grid)[best_index]
print('R-Squered:{}'.format(test_score[best_index]))
print('Best Paramater including max_depth:{}'.format(ParameterGrid))

rfr = RandomForestRegressor(n_estimators=ParameterGrid['n_estimators'],
                            max_depth=ParameterGrid['max_depth'],
                            max_features=ParameterGrid['max_features'])
rfr.fit(X_train, y_train)
train_pred = rfr.predict(X_train)
test_pred = rfr.predict(X_test_2005)
rfr_mse = mean_squared_error(y_test_2005, rfr.predict(X_test_2005))
rfr_rmse = rfr_mse**0.5
print('mean_squared_error:{}'.format(rfr_mse))
print('Rmse:{}'.format(rfr_rmse))

plt.figure(figsize=(16,10))
x_ax = range(len(X_test_2005))
plt.scatter(x_ax, y_test_2005, s=5, color='blue', label='original')
plt.plot(x_ax, test_pred, lw=0.8, color='red', label='prediction')
plt.legend()
plt.show()

"""Elastic Net

Feature Selection for Elastic Net to Reduce Dimantionality.

The cofficient was very small therefore I had to mannualy reduce the penalty for features selection.
"""

lasso = Lasso(alpha= 0.000002)
lasso.fit(X_train, y_train)
coff = list(zip(lasso.coef_, features))
coff

X_selected = data[['fscore','debtiss','nissa','growth','gmargins','cfp', 'noa', 'invcap', 'sgrowth', 'roea','sp','indmom','valmom', 'valmomprof', 'mom12','mom12', 'valuem', 'roe', 'rome', 'strev', 'season', '5m_rsi']]
y = data['re']
X_selected_2005 = data_2005[['fscore','debtiss','nissa','growth','gmargins','cfp', 'noa', 'invcap', 'sgrowth', 'roea','sp','indmom','valmom', 'valmomprof', 'mom12','mom12', 'valuem', 'roe', 'rome', 'strev', 'season', '5m_rsi']]
y_selected = data_2005['re']

X_train_selected, X_test_selected, y_train_selected, y_test_selected = train_test_split(X_selected, y, shuffle=False, random_state=0, test_size=0.2)
X_train_selected_2005, X_test_selected_2005, y_train_selected_2005, y_test_selected_2005 = train_test_split(X_selected_2005, y_selected, shuffle=False, random_state=0, test_size=0.2)

elastic = ElasticNet(fit_intercept=True)
el = GridSearchCV(elastic,
                   {'alpha':np.linspace(0.0002, 2, num=4),
                    'l1_ratio':np.linspace(0.0002, 1, num=4)}, cv=5, scoring='neg_mean_squared_error', verbose=5)
el.fit(X_train_selected,y_train_selected)
el.best_params_

elasticnet = ElasticNet(alpha=0.0002, l1_ratio=0.33346)
elasticnet.fit(X_train_selected, y_train_selected)
mean_sq_error_elasticnet = mean_squared_error(y_test_selected_2005, elasticnet.predict(X_test_selected_2005))
R_squared_elasticnet = elasticnet.score(X_train_selected, y_train_selected)
print('Mean Squared Error:{}' .format(mean_sq_error_elasticnet))
print('Root Mean Squared Error:{}'.format(mean_sq_error_elasticnet**0.5))
print('R_squared:{}'.format(R_squared_elasticnet))

plt.figure(figsize=(16,10))
f_ax = range(len(X_test_selected_2005))
plt.scatter(f_ax, y_test_selected_2005, s=2, color="blue", label="original")
plt.plot(f_ax, elasticnet.predict(X_test_selected_2005), lw=0.1, color="red", label="predicted")
plt.legend()
plt.show()

"""Neural Network"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, random_state=0, test_size=0.2)
X_train_2005, X_test_2005, y_train_2005, y_test_2005 = train_test_split(X_2005, y_2005, shuffle=False, random_state=0, test_size=0.2)

model = Sequential()
model.add(Dense(20, input_shape=(42,), activation='relu'))
model.add(Dense(20, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(2))

model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=20)
pred = model.predict(X_test_2005)
model.evaluate(X_test_2005, y_test_2005) #mse