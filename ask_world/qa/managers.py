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


class TagManager(models.Manager):

    # возвращает множество самых используемых тегов
    def best(self, limit=10):
        pass


class LikeManager(models.Manager):

    def add(self, author, target, is_positive):
        if is_positive == None:
            return
        like, created = self.get_or_create(author=author, target=target)
        if not created:
            # отмена лайка/дизлайка
            if is_positive == like.is_positive:
                like.is_positive = None
                target.num_likes -= 1 if is_positive else target.num_dislikes -= 1
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
        else:
            target.num_likes += 1 if is_positive else target.num_dislikes += 1
        like.save()
        target.save()

    # def add_like(self, author, positive=True):
    #     if positive == None:
    #         return
    #     try:
    #         like = QuestionLike.objects.get(content=self, author=author)
    #         # отмена лайка/дизлайка
    #         if positive == like.is_positive:
    #             like.is_positive = None
    #             if positive:
    #                 self.num_likes -= 1
    #             else:
    #                 self.num_dislikes -= 1
    #         else:
    #             # если дизлайк будет заменен на лайк
    #             if positive and not like.is_positive:
    #                 self.num_dislikes -= 1
    #                 self.num_likes += 1
            
    #             # если лайк будет заменен на дизлайк
    #             if not positive and like.is_positive:
    #                 self.num_dislikes += 1
    #                 self.num_likes -= 1

    #             like.is_positive = positive
    #     except QuestionLike.DoesNotExist:
    #         like = QuestionLike(content=self, author=author, is_positive=positive)
    #         if positive:
    #             self.num_likes += 1
    #         else:
    #             self.num_dislikes += 1
    #     finally:
    #         like.save()
    #         self.save()