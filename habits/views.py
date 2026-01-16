from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Habit, HabitLog
from .forms import HabitForm

# Create your views here.
@login_required
def home(request):
    if request.user.is_authenticated:
        habits = Habit.objects.filter(user=request.user).prefetch_related('habitlog_set')
    else:
        habits = Habit.objects.filter(user__isnull=True).prefetch_related('habitlog_set')

    habit_data = []
    form = HabitForm(user=request.user)

    for habit in habits:
        habit_data.append({
            'habit': habit,
            'streak': habit.get_current_streak(),
            'done_today': habit.is_done_on(timezone.now().date())
        })

    if request.method == 'POST':
        form = HabitForm(request.POST, user=request.user)
        if form.is_valid():
            habit = form.save(commit=False)
            if request.user.is_authenticated:
                habit.user = request.user
            habit.save()
            return redirect('home')

    return render(request, 'habits/home.html', {
        'habit_data': habit_data,
        'form': form
    })

def get_user_habit(request, habit_id):
    if request.user.is_authenticated:
        return get_object_or_404(Habit, id=habit_id, user=request.user)
    return get_object_or_404(Habit, id=habit_id, user__isnull=True)

@login_required
@require_POST
def toggle_habit(request, habit_id):
    habit = get_user_habit(request, habit_id)

    date_str = request.POST.get('date')
    if not date_str:
        return redirect('home')
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return redirect('home')

    today = timezone.now().date()

    if selected_date > today:
        return redirect('home')

    log, created = HabitLog.objects.get_or_create(
        habit=habit,
        date=selected_date,
    )
    if not created:
        log.delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def habit_status(request, habit_id):
    habit = get_user_habit(request, habit_id)

    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'done': False})
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'done': False})

    today = timezone.now().date()
    if selected_date > today:
        return JsonResponse({'done': False})
    return JsonResponse({
        'done': habit.is_done_on(selected_date)
    })

@login_required
def habit_detail(request, habit_id):
    habit = get_user_habit(request, habit_id)
    today = timezone.now().date()

    days = []
    for i in range(14):
        date = today - timedelta(days=i)
        days.append({
            'date': date,
            'done': habit.is_done_on(date)
        })

    start_of_week = today - timedelta(days=today.weekday())
    week = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        week.append({
            'date': date,
            'done': habit.is_done_on(date)
        })
    return render(request, 'habits/habit_detail.html', {
        'habit': habit,
        'streak': habit.get_current_streak(),
        'days': days,
        'week': week
    })

def confirm_delete_habit(request, habit_id):
    habit = get_user_habit(request, habit_id)
    return render(request, 'habits/confirm_delete.html',{
        'habit': habit
    })

@login_required
@require_POST
def delete_habit(request, habit_id):
    habit = get_user_habit(request, habit_id)
    habit.delete()
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html',{
        'form': form
    })

@login_required
def habit_insights(request, habit_id):
    habit = get_user_habit(request, habit_id)
    return render(request, 'habits/habit_insights.html', {
        'habit': habit,
        'current_streak': habit.get_current_streak(),
        'longest_streak': habit.longest_streak(),
        'total_completions': habit.total_completions(),
        'weekly_consistency': habit.weekly_consistency_percentage(),
    })

