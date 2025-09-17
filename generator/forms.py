from django import forms
from .models import ContentRequest

class ContentGenerationForm(forms.ModelForm):
    class Meta:
        model = ContentRequest
        fields = [
            'image', 
            'event_description', 
            'style', 
            'language', 
            'audience_type', 
            'audience_description', 
            'additional_notes'
        ]
        
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'event_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '描述您想要分享的事件或内容（可选）...'
            }),
            'style': forms.Select(attrs={
                'class': 'form-control',
            }),
            'language': forms.Select(attrs={
                'class': 'form-control',
            }),
            'audience_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：朋友、同事、粉丝、客户...'
            }),
            'audience_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '描述您的目标受众特征，如年龄、兴趣、关系等...'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '其他补充说明（可选）...'
            }),
        }
        
        labels = {
            'image': '朋友圈配图',
            'event_description': '事件描述', 
            'style': '内容风格',
            'language': '语言',
            'audience_type': '受众类型',
            'audience_description': '受众描述',
            'additional_notes': '补充说明',
        }