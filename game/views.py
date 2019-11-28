from random import sample
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm, AnswerForm
from .models import Question, Statistic, Topic, Answer, Best_score

# Create your views here.

def index(request):
    """Redirect to index page."""
    return HttpResponseRedirect(reverse("game:index"))

def form_page(request):
    """Redirect to Add Question Form page."""
    form = QuestionForm()
    context = {'form': form}
    return render(request, 'game/form.html', context)

def page404(request, exception):
    """Redirect to 404 page."""
    return render(request, 'game/404.html')

def views_logout(request):
    """User logout and redirect to homepage."""
    logout(request)
    return redirect("game:home")

def home_page(request):
    """Redirect to homepage."""
    return render(request, 'game/home.html')


def statistic_page(request):
    """Redirect to Stat page."""
    statistic = Statistic.objects.all()
    return render(request, 'game/statistic.html', {'stat':statistic})


def topic_page(request):
    """Redirect to Select Topic page."""
    topic = Topic.objects.all()
    return render(request, 'game/topic.html', {'topic':topic})

def question_difficulty(value: Question, topic_id: int, difficulty: str):
    """Return list of Question with filtered topic_id and difficulty."""
    return [q for q in value.objects.filter(topic_id=topic_id, difficulty=difficulty)]

def sample_question(value: Question, topic_id: int, diff: str, no_of_question: int):
    """
        Return a list of shuffled 'no_of_question' Question(s)
        with filtered topic_id and difficulty.
    """
    each_question_diff = question_difficulty(value, topic_id, diff)
    try:
        shuffle = sample(each_question_diff, no_of_question)
    except ValueError:
        shuffle = sample(each_question_diff, len(each_question_diff))
    return shuffle


def random_question_list(value, topic_id: int):
    """
        Return a list of all 10 (or less) shuffled Question(s)
        with filtered topic_id.
    """
    question_list = []
    for diff in ['easy', 'normal', 'hard']:
        shuffle = sample_question(value, topic_id, diff, 3)
        question_list += shuffle
    question_list += sample_question(value, topic_id, 'extreme', 1)
    return question_list


def question_page(request, topic_id):
    """Redirect to the Game page."""
    questions = random_question_list(Question, topic_id)
    q_title = [q.question_title for q in questions]
    q_text = [q.question_text for q in questions]
    q_diff = [q.difficulty for q in questions]
    ans, hint = [], []
    for question in questions:
        answer_set = list(Answer.objects.filter(question_id=question.id, topic_id=topic_id))
        ans.append([a.answer_text for a in answer_set])
        hint.append([a.hint_text for a in answer_set])
    get_best_score(request, topic_id)
    return render(request, 'game/game.html', {
        'q_title':q_title, 'q_text':q_text, 'answer':ans, 'hint':hint, 'q_diff':q_diff, 'topic_id':topic_id})

def create_answer_box(value: str):
    """Replace '[[__|__]]' with input tag.
    Return the formatted value."""
    while ']]' in value:
        start = value.find('[[')
        mid = value.find('|')
        end = value.find(']]')
        ans_length = mid - start - 2
        box_length = ans_length
        if box_length < 1:
            box_length = 1
        hint = value[mid+1:end]
        replacement = str(AnswerForm(ans_length=ans_length,
                                     box_length=str(box_length)+"ch", hint=hint))
        value = value[:start] + replacement + value[end+2:]
    return value


def assign_answer(value, question_id, topic_id):
    """From 'value', Save string inside '[[__|__]]' as Answer."""
    last_box_mark = 0
    while ']]' in value:
        start = value.find('[[', last_box_mark)
        if start < last_box_mark:
            break
        mid = value.find('|', last_box_mark)
        end = value.find(']]', last_box_mark)
        answer = Answer(question_id=question_id, topic_id=topic_id,
                        answer_text=value[start+2:mid], hint_text=value[mid+1:end])
        answer.save()
        last_box_mark = end + 1

@login_required
def get_stat(request):
    """Create statistic for each player include score"""
    user_id = request.user.id
    status = True
    check_id = Statistic.objects.filter(user_id=user_id)
    if check_id:
        status = False
    if User.is_authenticated and status:
        user = User.objects.get(pk=user_id)
        stat = Statistic(user=user)
        stat.save()
    return redirect('game:home')

def preview_form(request):
    """Reidrect to Form Preview page."""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            topic = Topic.objects.get(topic_name=form.data.get('topic'))
            title = form.data.get('title')
            raw_question = form.data.get('question')
            boxed_question = create_answer_box(raw_question)
            difficulty = form.data.get('difficulty')
            question = Question(topic_id=topic.id,
                                question_title=title,
                                question_text=boxed_question,
                                difficulty=difficulty)
            question.save()
            assign_answer(raw_question, question.id, topic.id)
            return render(request, "game/preview_form.html", {'question': question})

def discard_form(request, question_id):
    """Discard the Question Form."""
    check = Question.objects.filter(pk=question_id)
    if check:
        question = Question.objects.get(pk=question_id)
        question.delete()
        return redirect("game:form")
    return preview_form(request.POST)

def receive_score(request, topic_id):
    """Save highscore to User profile when the game finished."""
    user_id = request.user.id
    topic = get_object_or_404(Topic, pk=topic_id)
    profile = Best_score.objects.get(user=user_id, key=topic.topic_name)
    try:
        score = request.GET.get('result_score')
        if int(profile.value) < int(score):
            profile.value = int(score)
            profile.save()
    except:
        pass

def get_best_score(request, topic_id):
    user_id = request.user.id
    topic = get_object_or_404(Topic, pk=topic_id)
    get_user = User.objects.get(pk=user_id)
    score_id = Statistic()
    check_key = Best_score.objects.filter(key=topic.topic_name, user=user_id)
    if check_key:
        receive_score(request, topic_id)
    else:
        s = Best_score(user=get_user, key=topic.topic_name, value=0)
        s.save()