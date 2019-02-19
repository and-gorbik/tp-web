from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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


class TagManager(models.Manager):

    # возвращает множество самых используемых тегов
    def best(self, limit=10):
        pass


class LikeManager(models.Manager):

    def add(self, author, target, is_positive=True):
        if is_positive == None:
            return
        try:
            like = self.get(author=author, target=target)
            # отмена лайка/дизлайка
            if is_positive == like.is_positive:
                like.is_positive = None
                if is_positive:
                    target.num_likes -= 1
                else:
                    target.num_dislikes -= 1
            else:
                # если дизлайк будет заменен на лайк
                if is_positive and not like.is_positive:
                    target.num_likes += 1
                    target.num_dislikes -= 1
                
                # если лайк будет заменен на дизлайк
                if not is_positive and like.is_positive:
                    target.num_dislikes += 1
                    target.num_likes -= 1
                
                like.is_positive = is_positive
            like.save(update_fields=['is_positive'])
        except ObjectDoesNotExist:
            like = self.create(author=author, target=target, is_positive=is_positive)
            if is_positive:
                target.num_likes += 1
            else:
                target.num_dislikes += 1
        finally:
            target.save()
