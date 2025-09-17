"""
内容生成器信号处理器
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import DailySummary

# 创建用户时自动创建日总结记录
@receiver(post_save, sender=User)
def create_daily_summary(sender, instance, created, **kwargs):
    """
    当创建新用户时，自动创建对应的日总结记录
    """
    if created:
        # 这里可以添加一些初始化逻辑
        pass