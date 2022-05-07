import spacy


def get_prediction(ar_input_data):
    message = ''
    sum_score = 0
    loaded_model = spacy.load('model_artifacts')

    for review in ar_input_data:
        parsed_text = loaded_model(review['text'])
        sum_score += parsed_text.cats['pos']

    aver_score = sum_score / len(ar_input_data) * 10
    if aver_score > 5:
        message += 'Отзывы в среднем положительные, '
    else:
        message += 'Отзывы в среднем отрицательные, '

    message += 'средняя тональность отзывов составляет ' + str(round(aver_score, 1))
    return message
