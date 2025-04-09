import copy
from multiprocessing import Value

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import Question, Tag

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

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = question.answer_set.all()
    page = paginate(answers, request)
    return render(request, 'single_question.html', context={'question': question, 'answers': page.object_list, 'page_obj': page})

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
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')

def settings(request):
    return render(request, 'settings.html')
