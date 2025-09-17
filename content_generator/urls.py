from django.urls import path
from . import views

app_name = 'content_generator'

urlpatterns = [
    # 任务管理
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/toggle/<int:task_id>/', views.toggle_task_completion, name='toggle_task_completion'),
    path('tasks/update-willingness/<int:task_id>/', views.update_willingness, name='update_willingness'),
    path('tasks/advice/<int:task_id>/', views.get_llm_advice, name='get_llm_advice'),
    
    # 事件记录
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    
    # 日总结
    path('summary/', views.daily_summary, name='daily_summary'),
    path('summary/generate/', views.generate_daily_summary, name='generate_daily_summary'),
    
    # 内容生成
    path('generate-content/<int:event_id>/', views.generate_content, name='generate_content'),
]