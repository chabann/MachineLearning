import spacy
import numpy as np
import os
from scoring import Scoring
from sklearn.metrics import roc_auc_score


def get_score_model(data_directory='datasets/aclImdb/test'):
    loaded_model = spacy.load('model_artifacts')
    count_test = 0
    score_sum = 0

    labels = []
    given_answers = []

    for label in ['pos', 'neg']:
        label_class = 1
        if label == 'neg':
            label_class = 0

        labeled_directory = f"{data_directory}/{label}"
        for review in os.listdir(labeled_directory):
            if review.endswith('.txt'):
                with open(f"{labeled_directory}/{review}", encoding="utf8") as f:
                    review_text = f.read()
                    review_text = review_text.replace('<br />', '\n\n').strip()
                    parsed_text = loaded_model(review_text)

                    if ((parsed_text.cats['pos'] <= parsed_text.cats['neg']) and (label == 'pos')) or \
                            ((parsed_text.cats['pos'] > parsed_text.cats['neg']) and (label == 'neg')):
                        score_sum += 1
                    count_test += 1
                    labels.append(label_class)
                    given_answers.append(parsed_text.cats['pos'])

    rmse = np.sqrt(score_sum / count_test)
    print('Ошибка RMSE для тестовой выборки ', rmse)

    scoring = Scoring(given_answers, labels, True)

    print('Precision', scoring.precision())
    print('Accuracy', scoring.accuracy())
    print('Recall', scoring.recall())
    print('F1-score', scoring.f1_score())
    print('AUC-score', roc_auc_score(given_answers, labels))


def get_prediction(input_data):
    # Загружаем сохраненную модель
    loaded_model = spacy.load("model_artifacts")
    parsed_text = loaded_model(input_data)
    # Определяем возвращаемое предсказание
    if parsed_text.cats["pos"] > parsed_text.cats["neg"]:
        prediction = "Положительный отзыв"
    else:
        prediction = "Негативный отзыв"

    score = parsed_text.cats["pos"]
    print(f"Текст обзора: {input_data}\n\
Предсказание: {prediction}\n\
Score: {score:.3f}")


if __name__ == "__main__":
    texts = ['So beautiful!!', 'terrible movie, just disgusting ((', 'I cant believe it was shown in a movie',
             'this movie is a piece of shit', 'I think it can be interesting, but im not sure..']

    # for text in texts:
        # get_prediction(text)

    get_score_model()

    """Ошибка RMSE для тестовой выборки 0.4374014174645528
    Precision 0.8200729322061993
    Accuracy 0.80896
    Recall 0.7916
    F1 - score 0.8055849548155987"""

    """
    Ошибка RMSE для тестовой выборки  0.4374014174645528
    Precision 0.8200729322061993
    Accuracy 0.80896
    Recall 0.7916
    F1-score 0.8055849548155987
    AUC-score 0.8093328941222739
    """
