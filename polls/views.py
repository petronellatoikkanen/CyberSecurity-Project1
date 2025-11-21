from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:10]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

################################# FLAW 1 - - - SQL Injection #################################
#
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choice_id = request.POST.get('choice')
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE polls_choice SET votes = votes + 1 WHERE id = {choice_id}")
    return redirect('polls:results', pk=question.id)

#Fix
#def vote(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    try:
#        selected_choice = question.choice_set.get(pk=request.POST['choice'])
#    except (KeyError, Choice.DoesNotExist):
#        return render(request, 'polls/detail.html', {
#            'question': question,
#            'error_message': "You didn't select a choice.",
#        })
#    else:
#        selected_choice.votes += 1
#        selected_choice.save()
#        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        
################################# FAULT 2 - - - Broken Authentication ##########################
#
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
            if user.password == password:
                request.session['user_id'] = user.id
                return redirect('polls:index')
        except User.DoesNotExist:
            pass  # No user found

        return render(request, 'polls/login.html', {
            'error_message': "Invalid login",
        })
    return render(request, 'polls/login.html')

# Fix
#def login_view(request):
#    if request.method == 'POST':
#        form = AuthenticationForm(request, data=request.POST)
#        if form.is_valid():
#            user = form.get_user()
#            login(request, user)
#            return redirect('polls:index') 
#    else:
#        form = AuthenticationForm()
#    return render(request, 'polls/login.html', {'form': form})

################################# FAULT 4 Broken Access Control ################################
def logout_view(request):
    logout(request)
    return redirect('polls:index')  

# Fix
#@login_required
#def logout_view(request):
#    logout(request)
#    return redirect('polls:index')  

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("polls:login") 
    else:
        form = UserCreationForm()
    return render(request, "polls/register.html", {"form": form})