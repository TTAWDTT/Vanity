from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    """
    主页视图 - 如果用户已登录则重定向到任务列表，否则显示欢迎页面
    """
    if request.user.is_authenticated:
        return redirect('content_generator:task_list')
    else:
        return render(request, 'home.html')

def register(request):
    """
    注册视图 - 用户名必须为"罗臻的仆从"
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # 验证用户名
        if username != '罗臻的仆从':
            messages.error(request, '用户名必须为"罗臻的仆从"')
            return render(request, 'registration/register.html')
        
        # 验证密码
        if not password:
            messages.error(request, '密码不能为空')
            return render(request, 'registration/register.html')
        
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'registration/register.html')
        
        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '该用户已存在')
            return render(request, 'registration/register.html')
        
        # 创建用户
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