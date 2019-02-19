from django.db import models
from django.db.models.signals import pre_save
# from django.utils.text import slugify
# from django.contrib.postgres.indexes import BrinIndex
from django.contrib.auth.models import User
from .managers import QuestionManager, AnswerManager, CommentManager
from .managers import TagManager

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="qa/avatars/img_{}.jpg".format(user), blank=True, default="qa/avatars/default.jpg")
    
    def url(self):
        return "/profiles/{}/".format(self.pk)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)
    objects = TagManager()

    def str(self):
        return " ".join(name.split('_'))

    def url(self):
        return "/tags/{}/".format(self.name)

    @staticmethod
    def replace_spaces(tagname):
        return "_".join(tagname.strip().split())



class Question(models.Model):
    title = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    objects = QuestionManager()

    class Meta:
        ordering = ['-added_at']
        # indexes = (
        #     BrinIndex(fields=['added_at']),
        # )

    def url(self):
        return "/questions/{}/".format(self.pk)

    def add_like(self, author, positive=True):
        if positive == None:
            return
        try:
            like = QuestionLike.objects.get(content=self, author=author)
            # отмена лайка/дизлайка
            if positive == like.is_positive:
                like.is_positive = None
                if positive:
                    self.num_likes -= 1
                else:
                    self.num_dislikes -= 1
            else:
                # если дизлайк будет заменен на лайк
                if positive and not like.is_positive:
                    self.num_dislikes -= 1
                    self.num_likes += 1
            
                # если лайк будет заменен на дизлайк
                if not positive and like.is_positive:
                    self.num_dislikes += 1
                    self.num_likes -= 1

                like.is_positive = positive
        except QuestionLike.DoesNotExist:
            like = QuestionLike(content=self, author=author, is_positive=positive)
            if positive:
                self.num_likes += 1
            else:
                self.num_dislikes += 1
        finally:
            like.save()
            self.save()
    
    def liked(self, author):
        return QuestionLike.objects.filter(content=self, author=author).first().is_positive


class Answer(models.Model):
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    num_comments = models.PositiveIntegerField(default=0)
    is_marked = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    objects = AnswerManager()

    def url(self):
        return "/answers/{}/".format(self.pk)

    def add_like(self, author, positive=True):
        try:
            like = AnswerLike.objects.get(content=self, author=author)
            
            # если дизлайк будет заменен на лайк
            if positive and not like.is_positive:
                self.num_dislikes -= 1
                self.num_likes += 1
            
            # если лайк будет заменен на дизлайк
            if not positive and like.is_positive:
                self.num_dislikes += 1
                self.num_likes -= 1
            
            like.is_positive = positive
        except AnswerLike.DoesNotExist:
            like = AnswerLike(content=self, author=author, is_positive=positive)
            if positive:
                self.num_likes += 1
            else:
                self.num_dislikes += 1
        like.save()
        self.save()


class Like(models.Model):
    content = None
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_positive = models.BooleanField(default=None)

    class Meta:
        abstract = True


class QuestionLike(Like):
    content = models.ForeignKey(Question, on_delete=models.CASCADE)

class AnswerLike(Like):
    content = models.ForeignKey(Answer, on_delete=models.CASCADE)

class Comment(models.Model):
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    objects = CommentManager()

    class Meta:
        ordering = ['-added_at']


def ensure_correct_tag_name(sender, instance, *args, **kwargs):
    instance.name = sender.replace_spaces(instance.name)

pre_save.connect(ensure_correct_tag_name, sender=Tag)