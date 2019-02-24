from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, Question, Answer, QuestionLike, AnswerLike, Tag, Comment
from . import forms

class LikeTestCase(TestCase):
    """ test likes system """

    def setUp(self):
        User = get_user_model()
        Andrey = Profile.objects.create(
            user=User.objects.create_user("Andrey")
        )
        Peter = Profile.objects.create(
            user=User.objects.create_user("Peter")
        )
        Answer.objects.create(
            question=Question.objects.create(title="question", author=Andrey),
            author=Peter
        )

    def test_profiles_can_like_question(self):
        profiles = Profile.objects.all()
        question = Question.objects.first()
        Andrey, Peter = profiles[0], profiles[1]
        QuestionLike.objects.add(author=Andrey, target=question)
        QuestionLike.objects.add(author=Peter, target=question, is_positive=False)
        self.assertEqual(question.num_likes, 1)
        self.assertEqual(question.num_dislikes, 1)

    def test_profiles_can_like_answer(self):
        profiles = Profile.objects.all()
        answer = Answer.objects.first()
        Andrey, Peter = profiles[0], profiles[1]
        AnswerLike.objects.add(author=Andrey, target=answer)
        AnswerLike.objects.add(author=Peter, target=answer, is_positive=False)
        self.assertEqual(answer.num_likes, 1)
        self.assertEqual(answer.num_dislikes, 1)

    def test_profiles_can_cancel_own_likes(self):
        answer = Answer.objects.first()
        question = Question.objects.first()
        profile = Profile.objects.first()
        QuestionLike.objects.add(author=profile, target=question)
        QuestionLike.objects.add(author=profile, target=question)
        AnswerLike.objects.add(author=profile, target=answer)
        AnswerLike.objects.add(author=profile, target=answer)    
        self.assertEqual(question.num_likes, 0)
        self.assertEqual(answer.num_likes, 0)

    def test_profiles_can_change_own_likes(self):
        answer = Answer.objects.first()
        question = Question.objects.first()
        profile = Profile.objects.first()
        QuestionLike.objects.add(author=profile, target=question)
        QuestionLike.objects.add(author=profile, target=question, is_positive=False)
        AnswerLike.objects.add(author=profile, target=answer, is_positive=False)
        AnswerLike.objects.add(author=profile, target=answer)
        self.assertEqual(question.num_likes, 0)
        self.assertEqual(question.num_dislikes, 1)
        self.assertEqual(answer.num_likes, 1)
        self.assertEqual(answer.num_dislikes, 0)    

    def test_question_and_answer_are_liked(self):
        profile = Profile.objects.first()
        question = Question.objects.first()
        answer = Answer.objects.first()
        QuestionLike.objects.add(author=profile, target=question)
        AnswerLike.objects.add(author=profile, target=answer, is_positive=False)
        self.assertEqual(question.liked(author=profile), True)
        self.assertEqual(answer.liked(author=profile), False)
        QuestionLike.objects.add(author=profile, target=question)
        AnswerLike.objects.add(author=profile, target=answer, is_positive=False)
        self.assertEqual(question.liked(author=profile), None)
        self.assertEqual(answer.liked(author=profile), None)


class ProfileTestCase(TestCase):
    """ test CRUD operations with Profile """

    def setUp(self):
        get_user_model().objects.create_user("Andrey")

    def test_create_profile(self):
        user = get_user_model().objects.first()
        p = Profile.objects.create(user=user)
        self.assertEqual(p.user.username, "Andrey")

    def test_retrieve_profile(self):
        user = get_user_model().objects.first()
        Profile.objects.create(user=user)
        self.assertEqual(Profile.objects.count(), 1)

    def test_update_profile(self):
        user1 = get_user_model().objects.first()
        user2 = get_user_model().objects.create_user("Peter")
        p = Profile.objects.create(user=user1)
        p.user = user2
        p.save(update_fields=['user'])
        self.assertEqual(p.user.username, "Peter")

    def test_delete_profile(self):
        user = get_user_model().objects.first()
        p = Profile.objects.create(user=user)
        p.delete()
        self.assertEqual(Profile.objects.count(), 0)
        self.assertEqual(get_user_model().objects.count(), 1)     

    def test_delete_profile_cascade(self):
        user = get_user_model().objects.first()
        Profile.objects.create(user=user)
        user.delete()
        self.assertEqual(Profile.objects.count(), 0)
        self.assertEqual(get_user_model().objects.count(), 0)


class TagTestCase(TestCase):
    """ test slugify """

    def setUp(self):
        Tag.objects.create(name='Andrey can swim')

    def test_tag_slug(self):
        self.assertEqual(Tag.objects.first().slug, 'andrey-can-swim')


class QuestionTestCase(TestCase):
    """ test CRUD operations with Question """

    def setUp(self):
        u = get_user_model().objects.create_user("Andrey")
        Profile.objects.create(user=u)
        for i in range(3):
            Tag.objects.create(name="tag_{}".format(i + 1))

    def _create(self):
        q = Question.objects.create(
            title="Question",
            description="some text",
            author=Profile.objects.first(),
        )
        q.tags.add(*Tag.objects.all())
        return q

    def test_create_question(self):
        q = self._create()
        self.assertEqual(q, Question.objects.get(title='Question'))

    def test_update_question(self):
        q = self._create()
        q.title = 'New question'
        q.save(update_fields=['title'])
        self.assertEqual(Question.objects.filter(title='New question').count(), 1)

    def test_delete_question(self):
        q = self._create()
        q.delete()
        self.assertEqual(Question.objects.filter(title='Question').count(), 0)


class AnswerTestCase(TestCase):
    """ test CRUD operations with Answer """

    def setUp(self):
        u = get_user_model().objects.create_user("Andrey")
        Profile.objects.create(user=u)
        for i in range(3):
            Tag.objects.create(name="tag_{}".format(i + 1))
        q = Question.objects.create(
            title="Question",
            description="some text",
            author=Profile.objects.first(),
        )
        q.tags.add(*Tag.objects.all())

    def _create(self):
        a = Answer.objects.create(
            description='some answer',
            question=Question.objects.get(title='Question'),
            author=Profile.objects.first(),
        )
        return a

    def test_create_answer(self):
        a = self._create()
        self.assertEqual(a, Answer.objects.first())

    def test_update_answer(self):
        a = self._create()
        a.description = 'other answer'
        a.save(update_fields=['description'])
        self.assertEqual(Answer.objects.filter(description='other answer').count(), 1)

    def test_delete_answer(self):
        a = self._create()
        a.delete()
        self.assertEqual(Answer.objects.filter(description='some answer').count(), 0)


class CommentTestCase(TestCase):

    def setUp(self):
        p = Profile.objects.create(
            user=get_user_model().objects.create_user("Andrey")
        )
        q = Question.objects.create(author=p)
        Answer.objects.create(author=p, question=q)

    def test_comment_create(self):
        Comment.objects.create(
            description='some comment',
            author=Profile.objects.first(),
            answer=Answer.objects.first(),
        )
        self.assertEqual(Comment.objects.first().description, 'some comment')

    def test_comment_delete_cascade(self):
        Answer.objects.first().delete()
        self.assertEqual(Comment.objects.count(), 0)


# class QuestionManagerTestCase(TestCase):

#     def setUp(self):
#         for i in range(3):
#             tags = [Tag.objects.create(name=str(i)) for i in range(5)]
#         for i in range(10):
#             q = Question.objects.create(title=str(i), num_likes=i)
#             q.tags.add(*tags)

#     def test_best_questions(self):
#         qs = Question.objects.best()
#         self.assertEqual(qs.count(), 9)
#         for i in range(10):
#             self.assertEqual(qs[i], 9 - i)


class QuestionFormTestCase(TestCase):

    def test_valid_form(self):
        data = {
            'title': 'A new question',
            'description': 'Text',
            'tags': "good  , bad, Angry    ",
        }
        form = forms.QuestionForm(data=data) # QuestionForm(request.POST)
        self.assertTrue(form.is_valid())
        tags = form.cleaned_data.get('tags')
        for t in tags:
            self.assertIn(t, ['good', 'bad', 'angry'])

    def test_invalid_form(self):
        data = {
            'tags': "good",
        }
        form = forms.QuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)


class UserLoginFormTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('Andrey', password='12345')
        Profile.objects.create(user=user)

    def test_valid_form(self):
        data = {
            'username': 'Andrey',
            'password': '12345',
        }
        form = forms.UserLoginForm(data=data)
        self.assertTrue(form.is_valid())

class UserCreationFormTestCase(TestCase):
    def test_not_equal_passwords(self):
        data = {
            'username': 'Andrey',
            'password1': '12345',
            'password2': '',
        }
        form = forms.UserCreationForm(data=data)
        self.assertFalse(form.is_valid())



