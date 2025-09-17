from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task, Event, DailySummary, LLMAdvice
from .forms import TaskForm, EventForm
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def task_list(request):
    """
    任务列表页面
    """
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    now = timezone.now()
    
    # 计算统计信息
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = tasks.filter(due_date__lt=now, completed=False).count()
    completion_rate = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # 计算优先级分布
    high_priority_count = tasks.filter(priority='high').count()
    medium_priority_count = tasks.filter(priority='medium').count()
    low_priority_count = tasks.filter(priority='low').count()
    
    # 计算图表百分比（以最大值为100%）
    max_count = max(high_priority_count, medium_priority_count, low_priority_count)
    high_priority_percent = round((high_priority_count / max_count * 100)) if max_count > 0 else 0
    medium_priority_percent = round((medium_priority_count / max_count * 100)) if max_count > 0 else 0
    low_priority_percent = round((low_priority_count / max_count * 100)) if max_count > 0 else 0
    
    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': completion_rate,
        'high_priority_count': high_priority_count,
        'medium_priority_count': medium_priority_count,
        'low_priority_count': low_priority_count,
        'high_priority_percent': high_priority_percent,
        'medium_priority_percent': medium_priority_percent,
        'low_priority_percent': low_priority_percent,
        'now': now,
    }
    
    return render(request, 'content_generator/task_list.html', context)

@login_required
def add_task(request):
    """
    添加任务
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            # 生成LLM建议
            advice_content = generate_task_advice_with_llm(task)
            LLMAdvice.objects.create(
                user=request.user,
                content=advice_content,
                advice_type='task',
                related_id=task.id
            )
            
            messages.success(request, '任务已添加')
            return redirect('content_generator:task_list')
    else:
        form = TaskForm()
    
    return render(request, 'content_generator/add_task.html', {'form': form})

@login_required
def edit_task(request, task_id):
    """
    编辑任务
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, '任务已更新')
            return redirect('content_generator:task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'content_generator/edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    """
    删除任务
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, '任务已删除')
    return redirect('content_generator:task_list')

@login_required
def toggle_task_completion(request, task_id):
    """
    切换任务完成状态
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    
    status = '完成' if task.completed else '未完成'
    messages.success(request, f'任务状态已更新为{status}')
    
    return redirect('content_generator:task_list')

@login_required
def event_list(request):
    """
    事件记录列表页面（日记）
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    events = Event.objects.filter(user=request.user).order_by('-created_at')
    
    # 计算统计信息
    now = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    total_events = events.count()
    today_events = events.filter(created_at__date=today).count()
    this_week_events = events.filter(created_at__date__gte=week_start).count()
    this_month_events = events.filter(created_at__date__gte=month_start).count()
    events_with_images = events.exclude(image='').count()
    happy_events = events.filter(mood='😄').count()
    
    context = {
        'events': events,
        'total_events': total_events,
        'today_events': today_events,
        'this_week_events': this_week_events,
        'this_month_events': this_month_events,
        'events_with_images': events_with_images,
        'happy_events': happy_events
    }
    
    return render(request, 'content_generator/event_list.html', context)

@login_required
def add_event(request):
    """
    添加事件记录
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, '事件已记录')
            return redirect('content_generator:event_list')
    else:
        form = EventForm()
    
    return render(request, 'content_generator/add_event.html', {'form': form})

@login_required
def daily_summary(request):
    """
    日总结页面
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    from django.db.models import Q
    
    if request.method == 'POST':
        # 处理新的总结提交
        date_str = request.POST.get('date')
        summary_text = request.POST.get('summary')
        work_evaluation = request.POST.get('work_evaluation', '')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            summary, created = DailySummary.objects.update_or_create(
                user=request.user,
                date=date,
                defaults={
                    'summary': summary_text,
                    'work_evaluation': work_evaluation
                }
            )
            messages.success(request, '总结已保存')
        except ValueError:
            messages.error(request, '日期格式错误')
        
        return redirect('content_generator:daily_summary')
    
    # 获取数据
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # 获取所有总结
    all_summaries = DailySummary.objects.filter(user=request.user).order_by('-date')
    summaries = all_summaries[:10]  # 最近10条
    
    # 计算统计数据
    total_summaries = all_summaries.count()
    this_week_summaries = all_summaries.filter(date__gte=week_start).count()
    this_month_summaries = all_summaries.filter(date__gte=month_start).count()
    
    # 计算连续天数
    streak_days = 0
    current_date = today
    while True:
        if all_summaries.filter(date=current_date).exists():
            streak_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # 计算完成度
    days_in_month = (today.replace(month=today.month+1, day=1) - timedelta(days=1)).day if today.month < 12 else 31
    days_in_week = 7
    
    month_progress = int((this_month_summaries / days_in_month) * 100) if days_in_month > 0 else 0
    week_progress = int((this_week_summaries / days_in_week) * 100) if days_in_week > 0 else 0
    
    context = {
        'summaries': summaries,
        'today': today,
        'total_summaries': total_summaries,
        'this_week_summaries': this_week_summaries,
        'this_month_summaries': this_month_summaries,
        'streak_days': streak_days,
        'month_progress': min(month_progress, 100),
        'week_progress': min(week_progress, 100),
    }
    
    return render(request, 'content_generator/daily_summary.html', context)

@login_required
def generate_daily_summary(request):
    """
    生成日总结
    """
    today = timezone.now().date()
    
    # 获取今天的任务完成情况
    today_tasks = Task.objects.filter(
        user=request.user,
        created_at__date=today
    )
    
    completed_tasks = today_tasks.filter(completed=True)
    
    # 生成LLM总结
    summary_content = generate_summary_with_llm(today_tasks, completed_tasks)
    
    # 生成工作评估
    work_evaluation = generate_work_evaluation_with_llm(today_tasks, completed_tasks)
    
    # 保存总结
    summary, created = DailySummary.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={
            'summary': summary_content,
            'work_evaluation': work_evaluation
        }
    )
    
    if not created:
        summary.summary = summary_content
        summary.work_evaluation = work_evaluation
        summary.save()
    
    messages.success(request, '日总结已生成')
    return redirect('content_generator:daily_summary')

@login_required
def generate_content(request, event_id):
    """
    为事件生成分享文案
    """
    event = get_object_or_404(Event, id=event_id, user=request.user)
    
    # 生成LLM内容
    generated_content = generate_content_with_llm(event)
    
    # 保存生成的建议
    advice = LLMAdvice.objects.create(
        user=request.user,
        content=generated_content,
        advice_type='event',
        related_id=event.id
    )
    
    return JsonResponse({
        'success': True,
        'content': generated_content,
        'advice_id': advice.id
    })

@login_required
def get_llm_advice(request, task_id):
    """
    获取任务的LLM建议
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # 查找现有的建议
    try:
        advice = LLMAdvice.objects.get(
            user=request.user,
            advice_type='task',
            related_id=task.id
        )
    except LLMAdvice.DoesNotExist:
        # 生成新的建议
        advice_content = generate_task_advice_with_llm(task)
        advice = LLMAdvice.objects.create(
            user=request.user,
            content=advice_content,
            advice_type='task',
            related_id=task.id
        )
    
    return JsonResponse({
        'success': True,
        'advice': advice.content
    })

def generate_summary_with_llm(today_tasks, completed_tasks):
    """
    使用LLM生成日总结（模拟实现）
    """
    total_tasks = today_tasks.count()
    completed_count = completed_tasks.count()
    
    if total_tasks == 0:
        return "今天没有安排任务，可以适当放松一下。"
    
    completion_rate = completed_count / total_tasks * 100
    
    templates = [
        f"今天完成了{completed_count}个任务，完成率{completion_rate:.1f}%。继续保持良好的工作状态！",
        f"今日任务完成情况：{completed_count}/{total_tasks}，完成率{completion_rate:.1f}%。做得很好！",
        f"今天完成了{completed_count}项任务，完成率{completion_rate:.1f}%。继续努力！"
    ]
    
    import random
    return random.choice(templates)

def generate_work_evaluation_with_llm(today_tasks, completed_tasks):
    """
    使用LLM生成工作评估（模拟实现）
    """
    total_tasks = today_tasks.count()
    completed_count = completed_tasks.count()
    
    if total_tasks == 0:
        return "今日无任务安排。"
    
    completion_rate = completed_count / total_tasks * 100
    
    if completion_rate >= 80:
        evaluation = "工作效率很高，任务完成度优秀。"
    elif completion_rate >= 60:
        evaluation = "工作效率良好，任务完成度较好。"
    elif completion_rate >= 40:
        evaluation = "工作效率一般，还有提升空间。"
    else:
        evaluation = "工作效率较低，需要加强时间管理。"
    
    # 添加具体建议
    if completed_tasks.filter(priority='high').count() < today_tasks.filter(priority='high').count():
        evaluation += "建议优先处理高优先级任务。"
    
    return evaluation

def generate_content_with_llm(event):
    """
    使用LLM生成内容（模拟实现）
    """
    # 这里应该调用实际的LLM API
    # 目前使用模拟数据
    templates = [
        f"今天发生了件有趣的事：{event.title}。{event.content} {event.get_mood_display()}",
        f"分享一个生活片段：{event.title}。{event.content} 感觉{event.get_mood_display()}",
        f"今日心情记录：{event.title}。{event.content} {event.get_mood_display()}",
    ]
    
    import random
    return random.choice(templates)

def generate_task_advice_with_llm(task):
    """
    使用LLM为任务生成建议（模拟实现）
    """
    # 根据任务优先级和意愿度生成建议
    if task.priority == 'high' and task.willingness in ['😭', '😕']:
        advice = "这是一个高优先级但你不太愿意做的任务。建议将其分解成小步骤，逐步完成。"
    elif task.priority == 'high' and task.willingness in ['🙂', '😄']:
        advice = "这是一个高优先级且你愿意做的任务。建议安排专门的时间块来高效完成。"
    elif task.priority == 'low' and task.willingness in ['😭', '😕']:
        advice = "这是一个低优先级且你不太愿意做的任务。可以考虑委托给他人或延后处理。"
    else:
        advice = "这是一个常规任务。建议合理安排时间，平衡工作与休息。"
    
    # 添加时间管理建议
    if task.due_date:
        advice += f" 任务截止时间是{task.due_date.strftime('%Y-%m-%d %H:%M')}，请合理安排时间。"
    
    return advice

@login_required
@require_http_methods(["POST"])
def update_willingness(request, task_id):
    """
    更新任务的意愿度
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        data = json.loads(request.body)
        willingness = data.get('willingness')
        
        # 验证意愿度值
        valid_choices = [choice[0] for choice in Task.WILLINGNESS_CHOICES]
        if willingness in valid_choices:
            task.willingness = willingness
            task.save()
            return JsonResponse({'success': True, 'willingness': willingness})
        else:
            return JsonResponse({'success': False, 'error': '无效的意愿度值'})
    except Exception as e:
        logger.error(f"更新意愿度失败: {str(e)}")
        return JsonResponse({'success': False, 'error': '更新失败'})