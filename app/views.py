import copy
from multiprocessing import Value

from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.forms import AnswerForm, AskForm, LoginForm, UserEditForm, UserForm
from app.models import Answer, Question, Tag
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required


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
    questions = Question.objects.hot()
    q = list(reversed(copy.deepcopy(questions)))
    page = paginate(q, request)
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
    answers = question.answer_set.all()
    page = paginate(answers, request)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            return redirect(f"{question.get_url()}?page={page.paginator.num_pages}#answer-{answer.id}")
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
        raise Http404("Тег не найден")

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
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('edit'))
    return render(request, 'signup.html', context={'form':form})

def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))

@login_required(login_url=reverse_lazy('login'))
def edit(request):
    form = UserEditForm(instance=request.user)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    return render(request, 'edit.html', context={'form':form})
