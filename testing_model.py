import pickle
import pandas as pd
import numpy as np


def preprocess_score(val):
    if val == 4:
        return 1
    elif val == 2:
        return 0.5
    else:
        return 0


def rmse_error(y_pred, y_actual):
    mse = np.sum((y_pred - y_actual) ** 2) / np.size(y_pred)
    return np.sqrt(mse)


def r2_error(y_pred, y_actual):
    ssr = np.sum((y_pred - y_actual) ** 2)
    sst = np.sum((y_actual - np.mean(y_actual)) ** 2)
    r2_score = 1 - (ssr / sst)

    return r2_score


filename = 'finalized_model.sav'
model = pickle.load(open(filename, 'rb'))

names = ['score', 'id', 'date', 'query', 'user', 'text']
df = pd.read_csv('datasets/testdata.csv', encoding='latin-1', sep=',', error_bad_lines=False,
                 names=names, usecols=['score', 'text'])

df['score'] = df.apply(lambda row: preprocess_score(row['score']), axis=1)

X_test = df['text'].tolist()
y_test = df['score'].tolist()

predicted = model.predict(X_test)

pr_val = []
for x in predicted:
    if x < 0:
        x = 0
    if x > 1:
        x = 1
    pr_val.append(x)

print('RMSE для тестовых данных ', round(rmse_error(df['score'], pr_val), 2))
