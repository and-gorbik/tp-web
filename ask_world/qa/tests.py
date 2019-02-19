from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, Question, Answer, QuestionLike, AnswerLike

class LikeTestCase(TestCase):
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

    def test_question_is_liked(self):
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
