import spacy


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
