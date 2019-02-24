from . import views
from django.urls import path

urlpatterns = [
    path('', views.profile_detail, name='profile'),
]

# urlpatterns = [
#     path('', LastQuestionList.as_view(), name='index'),
#     path('top/', BestQuestionList.as_view(), name='top'),
#     path('questions/', QuestionList.as_view(), name='questions'),
#     path('questions/<int:id>', QuestionDetail.as_view(), name='question'),
#     path('tags/', TagList.as_view(), name='tags'),
#     path('tags/<str:name>', TagDetail.as_view(), name='tag'),
#     path('profile/', views.ProfileDetail.as_view(), name='profile'),
#     # формы-страницы
#     path('ask/', QuestionCreate.as_view(), name='ask'),
#     path('signup/', test, name='signup'),
#     # формы-оверлеи
#     path('signin/', test, name='signin'),
#     path('signout/', test, name='signout'),
#     формы на странице
#     path('answer/', AnswerCreate.as_view(), name='answer'),
#     path('comment/', CommentCreate.as_view(), name='comment'),
# ]