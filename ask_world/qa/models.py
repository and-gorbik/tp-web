from django.db import models
from django.db.models.signals import pre_save
# from django.contrib.postgres.indexes import BrinIndex
from django.contrib.auth.models import User
from .managers import QuestionManager, AnswerManager, CommentManager

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="qa/avatars/img_{}".format(user), blank=True, default="qa/avatars/default")

    class Meta:
        db_table = 'profile'
    
    def url(self):
        return "/profiles/{}/".format(self.pk)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)

    def url(self):
        return "/tags/{}/".format(self.name)

    @staticmethod
    def replace_spaces(tagname):
        return "_".join(tagname.strip().split())
    
    class Meta:
        db_table = 'tag'


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
        db_table = 'question'
        # indexes = (
        #     BrinIndex(fields=['added_at']),
        # )

    def url(self):
        return "/questions/{}/".format(self.pk)

    def add_like(self, author, positive=True):
        try:
            like = QuestionLike.objects.get(content=self, author=author)
            
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
        like.save()
        self.save()


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

    class Meta:
        db_table = 'answer'

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

    class Meta:
        db_table = 'question_like'

class AnswerLike(Like):
    content = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        db_table = 'answer_like'

class Comment(models.Model):
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    objects = CommentManager()

    class Meta:
        db_table = 'comment'
        ordering = ['-added_at']


def ensure_correct_tag_name(sender, instance, *args, **kwargs):
    instance.name = sender.replace_spaces(instance.name)

pre_save.connect(ensure_correct_tag_name, sender=Tag)