"""
URL configuration for vanity_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render
from . import views
import os

def manifest_view(request):
    """返回PWA manifest.json"""
    with open(os.path.join(settings.BASE_DIR, 'static', 'manifest.json'), 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/json')

def sw_view(request):
    """返回Service Worker"""
    with open(os.path.join(settings.BASE_DIR, 'static', 'sw.js'), 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('content/', include('content_generator.urls')),
    path('accounts/logout/', views.custom_logout, name='logout'),  # 必须在auth.urls之前
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    # PWA相关路由
    path('manifest.json', manifest_view, name='manifest'),
    path('sw.js', sw_view, name='service_worker'),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)