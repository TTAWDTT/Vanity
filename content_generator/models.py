from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator

# 任务模型
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', '♛♛♛'),
        ('medium', '♛♛'),
        ('low', '♛'),
    ]
    
    WILLINGNESS_CHOICES = [
        ('😭', '很不情愿'),
        ('😕', '不太情愿'),
        ('😐', '一般'),
        ('🙂', '比较愿意'),
        ('😄', '很愿意'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='任务标题')
    description = models.TextField(blank=True, null=True, verbose_name='任务描述')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    willingness = models.CharField(max_length=2, choices=WILLINGNESS_CHOICES, default='😐', verbose_name='意愿度')
    due_date = models.DateTimeField(blank=True, null=True, verbose_name='截止时间')
    completed = models.BooleanField(default=False, verbose_name='已完成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# 事件记录模型
class Event(models.Model):
    MOOD_CHOICES = [
        ('😄', '开心'),
        ('😢', '悲伤'),
        ('😠', '愤怒'),
        ('😲', '惊讶'),
        ('😴', '困倦'),
        ('😍', '兴奋'),
        ('🤔', '思考'),
        ('😎', '酷'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='事件标题')
    content = models.TextField(verbose_name='事件内容')
    mood = models.CharField(max_length=2, choices=MOOD_CHOICES, default='😄', verbose_name='心情')
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '事件记录'
        verbose_name_plural = '事件记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# 日总结模型
class DailySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    date = models.DateField(verbose_name='日期')
    summary = models.TextField(verbose_name='总结内容')
    work_evaluation = models.TextField(blank=True, null=True, verbose_name='工作评估')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '日总结'
        verbose_name_plural = '日总结'
        unique_together = ('user', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

# LLM建议模型
class LLMAdvice(models.Model):
    ADVICE_TYPE_CHOICES = [
        ('task', '任务建议'),
        ('event', '事件分享'),
        ('summary', '总结建议'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    content = models.TextField(verbose_name='建议内容')
    advice_type = models.CharField(max_length=10, choices=ADVICE_TYPE_CHOICES, verbose_name='建议类型')
    related_id = models.IntegerField(verbose_name='关联ID')  # 关联的任务或事件ID
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = 'LLM建议'
        verbose_name_plural = 'LLM建议'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_advice_type_display()} - {self.created_at}"