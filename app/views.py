import copy
from multiprocessing import Value

from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

QUESTIONS = [
    {
        'title': f'Title {i}',
        'id': i,
        'text': f'This is text for question #{i}'
    } for i in range(100)
]

ANSWERS = [
    {
        'id': i,
        'text': f'This is text for answer #{i}'
    } for i in range(100)
]

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
    page = paginate(QUESTIONS, request)

    return render(request, 'index.html', context={'questions': page.object_list, 'page_obj': page})

def hot(request):
    q = list(reversed(copy.deepcopy(QUESTIONS)))
    page = paginate(q, request)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page_obj': page})

def question(request, question_id):
    page = paginate(ANSWERS, request)
    return render(request, 'single_question.html', context={'question': QUESTIONS[question_id], 'answers': page.object_list, 'page_obj': page})

def tag(request, tag_name):
    page = paginate(QUESTIONS, request)
    return render(request, 'tag.html', context={'questions': page.object_list, 'page_obj': page, 'tag_name': tag_name})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')

def settings(request):
    return render(request, 'settings.html')
