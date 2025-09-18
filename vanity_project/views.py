from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from utils import is_mobile_device
import re

def home(request):
    """
    主页视图 - 检测设备类型并返回适当的模板
    """
    # 检测是否为移动设备
    is_mobile = is_mobile_device(request)
    
    # 如果用户已登录且不是移动设备，重定向到任务列表
    if request.user.is_authenticated and not is_mobile:
        return redirect('content_generator:task_list')
    
    # 根据设备类型选择模板
    template = 'mobile_home.html' if is_mobile else 'home.html'
    return render(request, template)

def register(request):
    """
    注册视图 - 用户名必须为"罗臻的仆从"，密码可以为任意内容
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # 验证用户名 - 必须为"罗臻的仆从"
        if username != '罗臻的仆从':
            messages.error(request, '用户名必须为"罗臻的仆从"')
            return render(request, 'registration/register.html')
        
        # 验证密码 - 只检查是否为空和确认密码是否一致
        if not password:
            messages.error(request, '密码不能为空')
            return render(request, 'registration/register.html')
        
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'registration/register.html')
        
        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '该用户已存在，请直接登录')
            return render(request, 'registration/register.html')
        
        # 创建用户 - 密码可以为任意内容
        try:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)  # 自动登录
            messages.success(request, '注册成功！欢迎您，罗臻的仆从！')
            return redirect('content_generator:task_list')
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
            
    return render(request, 'registration/register.html')

@login_required
def custom_logout(request):
    """
    自定义退出登录视图 - 支持GET和POST请求
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, '您已成功退出登录')
        return redirect('home')
    else:
        # GET请求显示确认页面
        return render(request, 'registration/logout.html')
    
    return render(request, 'registration/register.html')