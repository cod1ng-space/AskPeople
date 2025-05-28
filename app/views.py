import copy
from multiprocessing import Value
from profile import Profile

from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app import models
from app.context import setRightAnswerResponse
from app.forms import AnswerForm, AskForm, LoginForm, UserEditForm, UserForm
from app.models import Answer, AnswerLike, Question, QuestionLike, Tag
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_POST

def paginate(object_list, request, per_page=10):
    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError: # Если не не число
        page_num = 1 
    
    paginator = Paginator(object_list, per_page)
    if page_num < 1:
        page_num = 1
    elif page_num > paginator.num_pages:
        page_num = paginator.num_pages

    try:
        page = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger): # Если paginator.num_pages == 0
        page = paginator.page(1)
    return page


# Create your views here.
def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)

    return render(request, 'index.html', context={'questions': page.object_list, 'page_obj': page})

def hot(request):
    questions = Question.objects.with_ratings().order_by('-rating', '-created_at')
    page = paginate(questions, request)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page_obj': page})

def ask(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?continue={reverse("ask")}')

    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            tag_names = form.cleaned_data['tags']
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)

            return redirect(question.get_url())
    else:
        form = AskForm()

    return render(request, 'ask.html', {'form': form})

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.with_ratings().filter(question=question).order_by('-rating', '-created_at')
    page = paginate(answers, request)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            all_answers = Answer.objects.with_ratings().filter(question=question).order_by('-rating', '-created_at')
            answer_ids = list(all_answers.values_list('id', flat=True))
            
            try:
                answer_position = answer_ids.index(answer.id)
                page_num = (answer_position // page.paginator.per_page) + 1
                return redirect(f"{question.get_url()}?page={page_num}#answer-{answer.id}")
            except ValueError:
                # Если ошибка, то редирект на первую страницу
                return redirect(f"{question.get_url()}#answer-{answer.id}")
    else:
        form = AnswerForm()

    return render(request, 'single_question.html', context={
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'form': form
    })


def tag(request, tag_name):
    try:
        tag = Tag.objects.get(name=tag_name)
        questions = Question.objects.by_tag(tag_name)
        page = paginate(questions, request)
        return render(request, 'tag.html', {
            'questions': page.object_list,
            'page_obj': page,
            'tag': tag
        })
    except Tag.DoesNotExist:
        raise Http404("Tag not found")

def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('edit'))
    
    form = LoginForm()
    continue_url = request.GET.get('continue', reverse('edit'))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(continue_url)
            else:
                form.add_error(field=None, error="User not found")
    return render(request, 'login.html', context={'form':form})

def signup(request):
    if request.user.is_authenticated:
        return redirect(reverse('edit'))
    
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password'])
            if user is not None:
                auth.login(request, user) 
                return redirect(reverse('index'))
            else:
                form.add_error(None, "Ошибка аутентификации после регистрации")
    return render(request, 'signup.html', context={'form':form})

def logout(request):
    auth.logout(request)
    prev_url = request.META.get('HTTP_REFERER') # Получаем URL предыдущей страницы

    return redirect(prev_url)

@login_required(login_url=reverse_lazy('login'))
def edit(request):
    form = UserEditForm(instance=request.user)
    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    return render(request, 'edit.html', context={'form':form})

@require_POST
@login_required
def question_like(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    value = 1 if request.POST.get('action') == 'like' else -1
    
    like, created = QuestionLike.objects.get_or_create(
        question=question,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
        else:
            like.value = value
            like.save()
    
    likes_count = QuestionLike.objects.filter(question=question, value=1).count()
    dislikes_count = QuestionLike.objects.filter(question=question, value=-1).count()
    
    return JsonResponse({
        'likes_count': likes_count,
        'dislikes_count': dislikes_count
    })

# AJAX

@require_POST
@login_required
def answer_like(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    value = 1 if request.POST.get('action') == 'like' else -1
    
    like, created = AnswerLike.objects.get_or_create(
        answer=answer,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
        else:
            like.value = value
            like.save()
    
    likes_count = AnswerLike.objects.filter(answer=answer, value=1).count()
    dislikes_count = AnswerLike.objects.filter(answer=answer, value=-1).count()
    
    return JsonResponse({
        'likes_count': likes_count,
        'dislikes_count': dislikes_count
    })

@require_POST
@login_required
def mark_correct_answer(request):
    return setRightAnswerResponse(request)

