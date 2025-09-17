from django import forms
from django.core.exceptions import ValidationError
from .models import Task, Event

class TaskForm(forms.ModelForm):
    """
    任务表单
    """
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'willingness', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '输入任务标题'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '任务详细描述（可选）'
            }),
            'priority': forms.HiddenInput(),  # 使用自定义选择器
            'willingness': forms.HiddenInput(),  # 使用自定义选择器
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

class EventForm(forms.ModelForm):
    """
    事件记录表单
    """
    
    class Meta:
        model = Event
        fields = ['title', 'content', 'mood', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '事件标题'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '记录事件的详细内容...'
            }),
            'mood': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }