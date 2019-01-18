from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned

class Profile(models.Model):
    avatar = models.ImageField("Avatar", upload_to="qa/avatars/img_{}".format(id), blank=True, default=None)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def url(self):
        return "/tags/{}/".format(self.name)

    @staticmethod
    def replace_spaces(tagname):
        return "_".join(tagname.split())



# интерфейс
class LikedContent(models.Model):
    NAME_CHOICES = (
        ('0', 'answer'),
        ('1', 'question'),
    )

    name = models.CharField(max_length=1, choices=NAME_CHOICES)
    likes = models.ManyToManyField(Profile, through='Like')



class QuestionManager(models.Manager):

    def best(self, limit=10):
        return self.order_by('-like_counter')[:limit]


    def last(self, limit=10):
        return self.order_by('-added_at')[:limit]


    def get_by_tagname(self, tagname):
        return self.filter(tags__name=Tag.replace_spaces(tagname))




class Question(models.Model):
    title = models.CharField("Title", max_length=200, default="")
    description = models.TextField("Description", default="", blank=True)
    added_at = models.DateField("Added at", auto_now_add=True)
    like_counter = models.PositiveIntegerField("Like's counter", default=0)
    dislike_counter = models.PositiveIntegerField("Dislike's counter", default=0)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.OneToOneField(LikedContent, on_delete=models.CASCADE)
    objects = QuestionManager()

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return self.title

    def url(self):
        return "/questions/{}/".format(self.pk)

    def like(self, profile, positive=True):
        # можно использовать get_or_create(), но я с ним запутался
        try:
            like = Like.objects.get(content=self.content, profile=profile)
            
            # если дизлайк будет заменен на лайк
            if positive and not like.is_positive:
                self.dislike_counter -= 1
                self.like_counter += 1
            
            # если лайк будет заменен на дизлайк
            if not positive and like.is_positive:
                self.dislike_counter += 1
                self.like_counter -= 1
            
            like.is_positive = positive
        
        except Like.DoesNotExist:
            like = Like(content=self.content, profile=profile, is_positive=positive)
            if positive:
                self.like_counter += 1
            else:
                self.dislike_counter += 1

        like.save()
    
    def add_tag(self, tagname):
        tagname = Tag.replace_spaces(tagname)
        tag, _ = Question.objects.get_or_create(name=tagname)
        self.tags.add(tag)


class AnswerManager(models.Manager):

    def get_by_question(self, question, limit=10):
        return self.filter(question=question).order_by('-like_counter')[:limit]


class Answer(models.Model):
    description = models.TextField(default="", blank=True)
    added_at = models.DateField(auto_now_add=True)
    like_counter = models.PositiveIntegerField(default=0)
    dislike_counter = models.PositiveIntegerField(default=0)
    is_marked = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.OneToOneField(LikedContent, on_delete=models.CASCADE)
    objects = AnswerManager()


    def __str__(self):
        return "Answer" + str(self.pk)

    def url(self):
        return "/answers/{}/".format(self.pk)

    def like(self, profile, positive=True):
        try:
            like = Like.objects.get(content=self.content, profile=profile)
            
            # если дизлайк будет заменен на лайк
            if positive and not like.is_positive:
                self.dislike_counter -= 1
                self.like_counter += 1
            
            # если лайк будет заменен на дизлайк
            if not positive and like.is_positive:
                self.dislike_counter += 1
                self.like_counter -= 1
            
            like.is_positive = positive
        
        except Like.DoesNotExist:
            like = Like(content=self.content, profile=profile, is_positive=positive)
            if positive:
                self.like_counter += 1
            else:
                self.dislike_counter += 1

        like.save()

    def mark(self):
        self.is_marked = True


# промежуточная таблица связи многие-ко-многим 
# "LikedContent" - "Person"
class Like(models.Model):
    content = models.ForeignKey(LikedContent, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=None)  # True if like else dislike

    class Meta:
        unique_together = ("content", "profile")

