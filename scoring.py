import numpy as np


class Scoring:
    def __init__(self, answers, labels, isregress=False):
        self.givenAnswers = answers
        self.trueAnswers = labels

        self.TP = 0
        self.TN = 0
        self.FP = 0
        self.FN = 0

        self.count = len(answers)
        if isregress:
            self.set_probability_to_class()

        self.set_answer_category()

    def set_probability_to_class(self):
        for i in range(self.count):
            if self.givenAnswers[i] < 0.5:
                self.givenAnswers[i] = 0
            else:
                self.givenAnswers[i] = 1

    def set_category_regress(self):
        for i in range(self.count):
            if self.givenAnswers[i] == self.trueAnswers[i]:
                if self.givenAnswers[i] == 1:
                    self.TP += 1
                else:
                    self.TN += 1
            else:
                if self.givenAnswers[i] == 1:
                    self.FP += 1
                else:
                    self.FN += 1

    def set_answer_category(self):
        for i in range(self.count):
            if self.givenAnswers[i] == self.trueAnswers[i]:
                if self.givenAnswers[i] == 1:
                    self.TP += 1
                else:
                    self.TN += 1
            else:
                if self.givenAnswers[i] == 1:
                    self.FP += 1
                else:
                    self.FN += 1

    def accuracy(self):
        return (self.TP + self.TN) / self.count

    def precision(self):
        if self.TP + self.FP > 0:
            return self.TP / (self.TP + self.FP)
        return 'Undefined'

    def recall(self):
        if self.TP + self.FN > 0:
            return self.TP / (self.TP + self.FN)
        return 'Undefined'

    def f1_score(self):
        recall = self.recall()
        precision = self.precision()

        if (recall != 'Undefined') and (precision != 'Undefined'):
            if recall + precision > 0:
                return (2 * recall * precision) / (recall + precision)
        return 'Undefined'

    def rmse(self):
        mse = np.sum((self.givenAnswers - self.trueAnswers) ** 2) / self.count
        return np.sqrt(mse)
