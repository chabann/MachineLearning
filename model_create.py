import os
import random
import spacy
from spacy.util import minibatch, compounding


def load_training_data(data_directory='datasets/aclImdb/train', split=0.8, limit=0):
    # Загрузка данных из файлов
    reviews = []
    for label in ["pos", "neg"]:
        labeled_directory = f"{data_directory}/{label}"
        for review in os.listdir(labeled_directory):
            if review.endswith(".txt"):
                with open(f"{labeled_directory}/{review}", encoding="utf8") as f:
                    text = f.read()
                    text = text.replace("<br />", "\n\n")
                    if text.strip():
                        spacy_label = {
                            "cats": {
                                "pos": "pos" == label,
                                "neg": "neg" == label
                            }
                        }
                        reviews.append((text, spacy_label))
    random.shuffle(reviews)

    if limit:
        reviews = reviews[:limit]
    split = int(len(reviews) * split)
    return reviews[:split], reviews[split:]


def train_model(training_data, test_data, iterations=20):
    # Строим конвейер
    nlp = spacy.load("en_core_web_sm")  # Загружаем предобученную модель
    if "textcat" not in nlp.pipe_names:   # Проверка есть ли textcat уже в конвейере
        textcat = nlp.create_pipe(
            "textcat", config={"architecture": "simple_cnn"}
        )
        nlp.add_pipe(textcat, last=True)  # добавление компонента textcat в конвейер
    else:
        textcat = nlp.get_pipe("textcat")

    # Устанавливем метки классов
    textcat.add_label("pos")
    textcat.add_label("neg")

    # Обучаем только textcat
    training_excluded_pipes = [
        pipe for pipe in nlp.pipe_names if pipe != "textcat"
    ]
    with nlp.disable_pipes(training_excluded_pipes):  # Откючает все кроме textcat
        optimizer = nlp.begin_training()  # Начальная функция оптимизатора
        # Итерация обучения
        print("Loss\t\tPrec.\tRec.\tF-score")
        batch_sizes = compounding(4.0, 32.0, 1.001)  # Динамический размер батча (compounding)

        for i in range(iterations):
            loss = {}
            random.shuffle(training_data)
            batches = minibatch(training_data, size=batch_sizes)  # Перемешиваем данные и создаем батчи
            for batch in batches:
                text, labels = zip(*batch)
                nlp.update(text, labels, drop=0.2, sgd=optimizer, losses=loss)  # Запускаем обучение
                # Дропаут исключает часть данных для уменьшения переобучения

            with textcat.model.use_params(optimizer.averages):
                # Оценка прогресса обучения
                evaluation_results = evaluate_model(
                    tokenizer=nlp.tokenizer,
                    textcat=textcat,
                    test_data=test_data
                )
                print(f"{loss['textcat']:9.6f}\t\
            {evaluation_results['precision']:.3f}\t\
            {evaluation_results['recall']:.3f}\t\
            {evaluation_results['f-score']:.3f}")

            # Сохраняем модель
            with nlp.use_params(optimizer.averages):
                nlp.to_disk("model_artifacts")


def evaluate_model(tokenizer, textcat, test_data: list) -> dict:
    reviews, labels = zip(*test_data)
    reviews = (tokenizer(review) for review in reviews)
    # Указываем TP как малое число, чтобы в знаменателе не оказался 0
    TP, FP, TN, FN = 1e-8, 0, 0, 0
    for i, review in enumerate(textcat.pipe(reviews)):
        true_label = labels[i]['cats']
        score_pos = review.cats['pos']
        if true_label['pos']:
            if score_pos >= 0.5:
                TP += 1
            else:
                FN += 1
        else:
            if score_pos >= 0.5:
                FP += 1
            else:
                TN += 1
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f_score = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f-score": f_score}


train, test = load_training_data(limit=5000)
train_model(train, test, iterations=10)
