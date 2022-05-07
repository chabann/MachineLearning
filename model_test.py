import spacy
import numpy as np
import os


def get_score_model(data_directory='datasets/aclImdb/test'):
    loaded_model = spacy.load('model_artifacts')
    count_test = 0
    score_sum = 0

    for label in ['pos', 'neg']:
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
    rmse = np.sqrt(score_sum / count_test)
    print('Ошибка RMSE для тестовой выборки ', rmse)


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

    for text in texts:
        get_prediction(text)

    get_score_model()
