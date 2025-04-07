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
    } for i in range(50)
]

ANSWERS = [
    {
        'id': i,
        'text': f'This is text for answer #{i}'
    } for i in range(50)
]

def get_page(request, array):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(array, 5)
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
    page = get_page(request, QUESTIONS)

    return render(request, 'index.html', context={'questions': page.object_list, 'page_obj': page})

def hot(request):
    q = list(reversed(copy.deepcopy(QUESTIONS)))
    page = get_page(request, q)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page_obj': page})

def question(request, question_id):
    page = get_page(request, ANSWERS)
    return render(request, 'single_question.html', context={'question': QUESTIONS[question_id], 'answers': page.object_list, 'page_obj': page})

def tag(request, tag_name):
    page = get_page(request, QUESTIONS)
    return render(request, 'tag.html', context={'questions': page.object_list, 'page_obj': page, 'tag_name': tag_name})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')

def settings(request):
    return render(request, 'settings.html')
