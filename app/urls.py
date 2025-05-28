from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name="index"),
    path('hot', views.hot, name="hot"),
    path('question/<int:question_id>', views.question, name="question"),
    path('tag/<slug:tag_name>', views.tag, name="tag"),
    path('login', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path('ask', views.ask, name="ask"),
    path('profile/edit', views.edit, name="edit"),
    path('logout', views.logout, name="logout"),
    path('answer/<int:answer_id>/like', views.answer_like, name='answer_like'),
    path('question/<int:question_id>/like', views.question_like, name='question_like'),
    path('answer/<int:answer_id>/mark_correct/', views.mark_correct_answer, name='mark_correct'),
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)