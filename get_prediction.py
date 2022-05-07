from sklearn import preprocessing
import pickle
import pandas as pd


def prepare_score(scores):
    for i in range(len(scores)):
        scores[i] = scores[i] / 4 * 10
    return scores


def get_mood(ar_texts):
    filename = 'finalized_model.sav'
    model = pickle.load(open(filename, 'rb'))

    predicted = model.predict(pd.Series(ar_texts))

    pr_val = []
    for x in predicted:
        if x < 0:
            x = 0
        if x > 1:
            x = 1
        pr_val.append(x)

    return pr_val


print(get_mood(['So beautiful!!', 'terrible movie, just disgusting ((', 'I cant believe it was shown in a movie',
                'this movie is a piece of shit']))
