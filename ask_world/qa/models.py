from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils.text import slugify
# from django.contrib.postgres.indexes import BrinIndex
from django.contrib.auth import get_user_model
from . import managers

class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="qa/avatars/img_{}.jpg".format(user), blank=True, default="qa/avatars/default.jpg")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)
    slug = models.SlugField(max_length=150, default="", allow_unicode=True, editable=False)
    objects = managers.TagManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', kwargs={'slug': self.slug})


class Question(models.Model):
    title = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    objects = managers.QuestionManager()

    class Meta:
        ordering = ['-added_at']
        # indexes = (
        #     BrinIndex(fields=['added_at']),
        # )

    def __str__(self):
        return self.title[:100] + "..."

    def get_absolute_url(self):
        return reverse('question', kwargs={'pk': self.pk})
    
    def liked(self, author):
        return QuestionLike.objects.filter(target=self, author=author).first().is_positive


class Answer(models.Model):
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    num_comments = models.PositiveIntegerField(default=0)
    is_marked = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    objects = managers.AnswerManager()

    def __str__(self):
        return self.description[:100] + "..."

    def liked(self, author):
        return AnswerLike.objects.filter(target=self, author=author).first().is_positive

class Like(models.Model):
    target = None
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_positive = models.NullBooleanField(default=None)
    objects = None

    class Meta:
        abstract = True

class QuestionLike(Like):
    target = models.ForeignKey(Question, on_delete=models.CASCADE)
    objects = managers.LikeManager()

class AnswerLike(Like):
    target = models.ForeignKey(Answer, on_delete=models.CASCADE)
    objects = managers.LikeManager()

class Comment(models.Model):
    description = models.TextField(default="")
    added_at = models.DateField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    objects = managers.CommentManager()

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return self.description[:100] + "..."


# Signals

@receiver(pre_save, sender=Tag)
def ensure_correct_tag_name(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name)