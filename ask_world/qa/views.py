from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import Profile, Tag, Question, Answer, Comment
from .models import QuestionLike, AnswerLike

def test(request, *args, **kwargs):
    return render(request, 'qa/question.html', {})

class ProfileDetail(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name= 'qa/profile.html'

class QuestionDetail(ModelFormMixin, DetailView):
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = Answer.objects.get_by_question(pk)
        context['answer_form'] = self.get_form(form_class=AnswerForm)
        context['comment_form'] = self.get_form(form_class=CommentForm)
        return context

class QuestionList(ListView):
    model = Question
    context_object_name = 'question_list'
    template_name= 'qa/questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_answers'] = None # продумать
        return context

class LastQuestionList(QuestionList):
    template_name= 'qa/index.html'
    def get_queryset(self):
        return Question.objects.last()


class BestQuestionList(QuestionList):
    template_name = 'qa/index.html'
    def get_queryset(self):
        return Question.objects.best()

class TagList(ListView):
    model = Tag
    context_object_name = 'tag_list'
    template_name = 'qa/base.html'

    def get_queryset(self):
        return Tag.objects.best()

class TagDetail(DetailView):
    model = Tag
    context_object_name = 'tag'
    template_name = 'qa/tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = Question.objects.get_by_tagname(name)
        return context

@method_decorator(login_required, name='dispatch')
class QuestionCreate(CreateView):
    model = Question
    fields = ['title', 'description', 'tags']
    success_message = 'Question is created!'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(author=self.request.user)
        return super().form_valid(form)

# class ProfileCreate(CreateView):
#     model = Profile
#     fields = ['user', 'avatar']
#     success_message = 'Profile is created!'
#     success_url = reverse_lazy('index')
