from django.db import models

class QuestionManager(models.Manager):

    def best(self, limit=10):
        return self.order_by('-like_counter')[:limit]


    def last(self, limit=10):
        return self.order_by('-added_at')[:limit]


    def get_by_tagname(self, tagname):
        return self.filter(tags__name=Tag.replace_spaces(tagname))


class AnswerManager(models.Manager):

    def get_by_question(self, question, limit=10):
        return self.filter(question=question).order_by('-like_counter')[:limit]


class CommentManager(models.Manager):

    def get_by_answer(self, answer, limit=10):
        return self.filter(answer=answer).order_by('-added_at')[:limit]