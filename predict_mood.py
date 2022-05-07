import spacy


def get_prediction(ar_input_data):
    message = ''
    sum_score = 0
    user_scores = 0
    loaded_model = spacy.load('model_artifacts')

    for review in ar_input_data:
        parsed_text = loaded_model(review['text'])
        sum_score += parsed_text.cats['pos']
        user_scores += float(review['score'])

    aver_score = sum_score / len(ar_input_data) * 10
    if aver_score > 5:
        message += 'Отзывы в среднем положительные, '
    else:
        message += 'Отзывы в среднем отрицательные, '

    message += 'средняя тональность отзывов составляет ' + str(round(aver_score, 1))

    aver_user_scores = user_scores / len(ar_input_data)
    message += ', средняя оценка по отзывам: ' + str(round(aver_user_scores, 1))
    return message
