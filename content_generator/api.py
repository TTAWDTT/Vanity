from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ContentGenerationRequest, GeneratedContent
from .forms import ContentGenerationRequestForm
from .views import check_rate_limit, get_client_ip
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ContentGenerationAPI(View):
    """
    内容生成API接口
    """
    
    def get(self, request, request_id=None):
        """
        获取内容生成结果
        
        Args:
            request: HTTP请求对象
            request_id (int, optional): 内容生成请求的ID
            
        Returns:
            JsonResponse: 内容生成结果或请求列表
        """
        try:
            # 检查API访问权限（这里简化处理，实际应用中可能需要API密钥等）
            if not self.check_api_access(request):
                return JsonResponse({
                    'success': False,
                    'error': 'API访问权限不足'
                }, status=403)
            
            if request_id:
                # 获取特定内容生成请求的结果
                content_request = ContentGenerationRequest.objects.get(id=request_id)
                
                # 检查权限：只有创建者或管理员可以查看
                if request.user.is_authenticated:
                    if content_request.user != request.user and not request.user.is_staff:
                        return JsonResponse({
                            'success': False,
                            'error': '您没有权限查看此内容'
                        }, status=403)
                else:
                    # 匿名用户只能查看自己的请求（通过会话或其他方式识别）
                    # 这里简化处理，实际应用中可能需要更复杂的逻辑
                    pass
                
                generated_contents = content_request.generated_contents.all()
                
                # 序列化数据
                data = {
                    'id': content_request.id,
                    'style_preference': content_request.style_preference,
                    'language': content_request.language,
                    'audience_type': content_request.audience_type,
                    'status': content_request.status,
                    'created_at': content_request.created_at.isoformat(),
                    'contents': [
                        {
                            'id': content.id,
                            'content': content.content,
                            'quality_score': content.quality_score,
                            'is_favorite': content.is_favorite,
                            'created_at': content.created_at.isoformat()
                        }
                        for content in generated_contents
                    ]
                }
                
                return JsonResponse({
                    'success': True,
                    'data': data
                })
            else:
                # 获取内容生成请求列表（分页）
                # 只允许管理员查看所有请求，普通用户只能查看自己的请求
                if request.user.is_authenticated and request.user.is_staff:
                    content_requests = ContentGenerationRequest.objects.all().order_by('-created_at')
                elif request.user.is_authenticated:
                    content_requests = ContentGenerationRequest.objects.filter(user=request.user).order_by('-created_at')
                else:
                    # 匿名用户无法查看请求列表
                    return JsonResponse({
                        'success': False,
                        'error': '您需要登录才能查看历史记录'
                    }, status=403)
                
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                
                # 分页处理
                paginator = Paginator(content_requests, page_size)
                page_obj = paginator.get_page(page)
                
                # 序列化数据
                data = {
                    'requests': [
                        {
                            'id': content_request.id,
                            'style_preference': content_request.style_preference,
                            'language': content_request.language,
                            'audience_type': content_request.audience_type,
                            'status': content_request.status,
                            'created_at': content_request.created_at.isoformat()
                        }
                        for content_request in page_obj
                    ],
                    'pagination': {
                        'current_page': page_obj.number,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous()
                    }
                }
                
                return JsonResponse({
                    'success': True,
                    'data': data
                })
                
        except ContentGenerationRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '未找到请求的内容'
            }, status=404)
        except Exception as e:
            logger.error(f"获取内容生成结果时出错: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误'
            }, status=500)
    
    def post(self, request, request_id=None):
        """
        创建新的内容生成请求或重新生成内容
        
        Args:
            request: HTTP请求对象
            request_id (int, optional): 内容生成请求的ID（用于重新生成）
            
        Returns:
            JsonResponse: 操作结果
        """
        try:
            # 检查API访问权限
            if not self.check_api_access(request):
                return JsonResponse({
                    'success': False,
                    'error': 'API访问权限不足'
                }, status=403)
            
            # 检查请求频率限制
            if not check_rate_limit(request):
                return JsonResponse({
                    'success': False,
                    'error': '请求过于频繁，请稍后再试'
                }, status=429)
            
            if request_id:
                # 重新生成内容
                content_request = ContentGenerationRequest.objects.get(id=request_id)
                
                # 检查权限：只有创建者可以重新生成
                if request.user.is_authenticated:
                    if content_request.user != request.user:
                        return JsonResponse({
                            'success': False,
                            'error': '您没有权限重新生成此内容'
                        }, status=403)
                else:
                    # 匿名用户无法重新生成内容
                    return JsonResponse({
                        'success': False,
                        'error': '您需要登录才能重新生成内容'
                    }, status=403)
                
                # 更新请求状态为处理中
                content_request.status = 'processing'
                content_request.save()
                
                # 删除之前生成的内容
                content_request.generated_contents.all().delete()
                
                # 重新生成内容（这里使用模拟数据，实际应调用AI模型）
                from .views import generate_content_with_ai
                generated_contents = generate_content_with_ai(content_request)
                
                # 保存生成的内容
                from .models import GeneratedContent
                content_objects = [
                    GeneratedContent(
                        request=content_request,
                        content=content_text,
                        quality_score=80 + i if i < 20 else 100
                    )
                    for i, content_text in enumerate(generated_contents)
                ]
                
                # 批量创建内容对象
                GeneratedContent.objects.bulk_create(content_objects)
                
                # 更新请求状态为已完成
                content_request.status = 'completed'
                content_request.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '内容重新生成成功',
                    'request_id': content_request.id
                })
            else:
                # 创建新的内容生成请求
                # 解析JSON数据
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，返回错误
                    return JsonResponse({
                        'success': False,
                        'error': '请求数据格式错误，应为JSON格式'
                    }, status=400)
                
                # 创建表单实例并验证数据
                form = ContentGenerationRequestForm(data, request.FILES)
                
                if form.is_valid():
                    # 创建内容生成请求记录
                    content_request = form.save(commit=False)
                    
                    # 如果用户已登录，关联用户
                    if request.user.is_authenticated:
                        content_request.user = request.user
                    
                    # 设置请求状态为处理中
                    content_request.status = 'processing'
                    content_request.save()
                    
                    # 生成内容（这里使用模拟数据，实际应调用AI模型）
                    from .views import generate_content_with_ai
                    generated_contents = generate_content_with_ai(content_request)
                    
                    # 保存生成的内容
                    from .models import GeneratedContent
                    content_objects = [
                        GeneratedContent(
                            request=content_request,
                            content=content_text,
                            quality_score=80 + i if i < 20 else 100
                        )
                        for i, content_text in enumerate(generated_contents)
                    ]
                    
                    # 批量创建内容对象
                    GeneratedContent.objects.bulk_create(content_objects)
                    
                    # 更新请求状态为已完成
                    content_request.status = 'completed'
                    content_request.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': '内容生成成功',
                        'request_id': content_request.id
                    })
                else:
                    # 表单验证失败，返回错误信息
                    errors = form.errors.as_json()
                    logger.warning(f"API表单验证失败: {errors}")
                    return JsonResponse({
                        'success': False,
                        'error': '表单数据验证失败',
                        'details': errors
                    }, status=400)
                    
        except ContentGenerationRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '未找到请求的内容'
            }, status=404)
        except Exception as e:
            # 记录错误日志
            logger.error(f"创建内容生成请求时出错: {str(e)}", exc_info=True)
            
            # 如果内容请求已创建，更新其状态为失败
            if 'content_request' in locals():
                content_request.status = 'failed'
                content_request.save()
            
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误'
            }, status=500)
    
    def check_api_access(self, request):
        """
        检查API访问权限
        
        Args:
            request: HTTP请求对象
            
        Returns:
            bool: 是否有访问权限
        """
        # 这里简化处理，实际应用中可能需要检查API密钥、OAuth令牌等
        # 例如检查Authorization头或自定义的API密钥头
        return True

@require_http_methods(["POST"])
def toggle_favorite_api(request, content_id):
    """
    切换内容的收藏状态（API版本）
    
    Args:
        request: HTTP请求对象
        content_id (int): 生成内容的ID
        
    Returns:
        JsonResponse: 操作结果
    """
    try:
        # 检查API访问权限
        # 这里简化处理，实际应用中可能需要检查API密钥、OAuth令牌等
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '您需要登录才能执行此操作'
            }, status=403)
        
        # 获取生成的内容对象
        content = GeneratedContent.objects.get(id=content_id)
        
        # 检查权限：只有内容请求的创建者可以收藏
        if content.request.user != request.user:
            return JsonResponse({
                'success': False,
                'error': '您没有权限操作此内容'
            }, status=403)
        
        # 切换收藏状态
        content.is_favorite = not content.is_favorite
        content.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': content.is_favorite,
            'message': '已添加到收藏' if content.is_favorite else '已取消收藏'
        })
    except GeneratedContent.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '未找到内容'
        }, status=404)
    except Exception as e:
        # 记录错误日志
        logger.error(f"切换收藏状态时出错: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '操作失败'
        }, status=500)