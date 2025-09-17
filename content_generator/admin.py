from django.contrib import admin
from .models import Task, Event, DailySummary, LLMAdvice

# 任务管理器
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'priority', 'willingness', 
        'completed', 'due_date', 'created_at'
    ]
    list_filter = [
        'priority', 'completed', 'willingness', 
        'created_at', 'due_date'
    ]
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

# 事件记录管理器
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'mood', 'created_at'
    ]
    list_filter = [
        'mood', 'created_at'
    ]
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['created_at']

# 日总结管理器
@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'date', 'created_at'
    ]
    list_filter = [
        'date', 'created_at'
    ]
    search_fields = ['summary', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'

# LLM建议管理器
@admin.register(LLMAdvice)
class LLMAdviceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'advice_type', 'related_id', 'created_at'
    ]
    list_filter = [
        'advice_type', 'created_at'
    ]
    search_fields = ['content', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'