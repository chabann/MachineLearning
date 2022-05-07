import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import GradientBoostingRegressor
import pickle


def preprocess_text(text):
    text = text.lower().replace('ё', 'е')
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text)
    text = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = re.sub(' +', ' ', text)
    return text.strip()


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


names = ['score', 'id', 'date', 'query', 'user', 'text']
n_estimators = 100

df = pd.read_csv('datasets/training.csv', encoding='latin-1', sep=',', error_bad_lines=False, names=names,
                 usecols=['score', 'text'])

df['text'] = df.apply(lambda row: preprocess_text(row['text']), axis=1)

# смещение оценки от 0 до 1
df['score'] = df.apply(lambda row: preprocess_score(row['score']), axis=1)

x_train, x_test, y_train, y_test = train_test_split(df['text'], df['score'], test_size=0.1, random_state=1)

pipeline_models = Pipeline([('count_vect', CountVectorizer()),
                            ('tfidf', TfidfTransformer()),
                            # ('GBR', GradientBoostingRegressor(n_estimators=n_estimators)),
                            ('ETR', ExtraTreesRegressor(n_estimators=n_estimators)),
                            ])

x_tr, x_valid, y_tr, y_valid = train_test_split(x_train, y_train,
                                                test_size=0.33,
                                                random_state=42)

print('start fit')
val_pipeline = pipeline_models.fit(x_tr, y_tr)
predicted_tr = val_pipeline.predict(x_tr)
predicted_val = val_pipeline.predict(x_valid)

pr_tr = []
for x in predicted_tr:
    if x < 0:
        x = 0
    if x > 1:
        x = 1
    pr_tr.append(x)

pr_val = []
for x in predicted_val:
    if x < 0:
        x = 0
    if x > 1:
        x = 1
    pr_val.append(x)

print('RMSE для тренировочных данных ', round(rmse_error(y_tr, pr_tr), 2))
print('RMSE для валидационных данных ', round(rmse_error(y_valid, pr_val), 2))

model = pipeline_models.fit(x_train, y_train)

# сохраняем модель
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))
