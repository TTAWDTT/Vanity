from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import ContentGenerationRequest, GeneratedContent, UserPreference
from .forms import ContentGenerationRequestForm
import json

class ContentGenerationRequestModelTest(TestCase):
    """
    内容生成请求模型测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.content_request = ContentGenerationRequest.objects.create(
            user=self.user,
            event_description='测试活动',
            style_preference='casual',
            language='zh',
            audience_type='general',
            audience_description='测试受众',
            additional_notes='测试备注',
            target_platform='wechat',
            content_length='medium',
            need_hashtags=True,
            need_emojis=True,
            status='completed'
        )
    
    def test_content_request_creation(self):
        """
        测试内容生成请求创建
        """
        self.assertEqual(self.content_request.style_preference, 'casual')
        self.assertEqual(self.content_request.language, 'zh')
        self.assertEqual(self.content_request.status, 'completed')
        self.assertIsNotNone(self.content_request.created_at)
    
    def test_content_request_str_representation(self):
        """
        测试内容生成请求的字符串表示
        """
        expected_str = f"ContentRequest-{self.content_request.id} (休闲)"
        self.assertEqual(str(self.content_request), expected_str)
    
    def test_generated_content_creation(self):
        """
        测试生成内容创建
        """
        generated_content = GeneratedContent.objects.create(
            request=self.content_request,
            content='这是测试生成的内容',
            content_type='text',
            quality_score=85,
            is_favorite=True
        )
        
        self.assertEqual(generated_content.content, '这是测试生成的内容')
        self.assertEqual(generated_content.quality_score, 85)
        self.assertTrue(generated_content.is_favorite)
        self.assertEqual(generated_content.request, self.content_request)
    
    def test_user_preference_creation(self):
        """
        测试用户偏好设置创建
        """
        preference = UserPreference.objects.create(
            user=self.user,
            default_style='formal',
            default_language='en',
            default_audience='professionals',
            default_length='long',
            default_need_hashtags=False,
            default_need_emojis=False
        )
        
        self.assertEqual(preference.default_style, 'formal')
        self.assertEqual(preference.default_language, 'en')
        self.assertFalse(preference.default_need_hashtags)
        self.assertFalse(preference.default_need_emojis)

class ContentGenerationRequestFormTest(TestCase):
    """
    内容生成请求表单测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.valid_data = {
            'event_description': '测试活动',
            'style_preference': 'casual',
            'language': 'zh',
            'audience_type': 'general',
            'audience_description': '测试受众',
            'additional_notes': '测试备注',
            'target_platform': 'wechat',
            'content_length': 'medium',
            'need_hashtags': True,
            'need_emojis': True
        }
    
    def test_form_valid_data(self):
        """
        测试表单验证有效数据
        """
        form = ContentGenerationRequestForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_missing_required_field(self):
        """
        测试表单缺少必填字段
        """
        data = self.valid_data.copy()
        data.pop('style_preference')  # 移除必填字段
        
        form = ContentGenerationRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('style_preference', form.errors)
    
    def test_form_invalid_image_size(self):
        """
        测试表单验证无效图片大小
        """
        # 创建一个大于5MB的文件
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            b"a" * (5 * 1024 * 1024 + 1),  # 5MB + 1字节
            content_type="image/jpeg"
        )
        
        data = self.valid_data.copy()
        form = ContentGenerationRequestForm(
            data=data,
            files={'image': large_file}
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
    
    def test_form_invalid_image_type(self):
        """
        测试表单验证无效图片类型
        """
        # 创建一个无效类型的文件
        invalid_file = SimpleUploadedFile(
            "invalid_file.txt",
            b"file content",
            content_type="text/plain"
        )
        
        data = self.valid_data.copy()
        form = ContentGenerationRequestForm(
            data=data,
            files={'image': invalid_file}
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

class ViewsTest(TestCase):
    """
    视图测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.content_request = ContentGenerationRequest.objects.create(
            user=self.user,
            event_description='测试活动',
            style_preference='casual',
            language='zh',
            audience_type='general',
            status='completed'
        )
        
        self.generated_content = GeneratedContent.objects.create(
            request=self.content_request,
            content='这是测试生成的内容',
            quality_score=85
        )
    
    def test_content_form_view(self):
        """
        测试内容表单页面视图
        """
        response = self.client.get(reverse('content_generator:content_form'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '社交媒体内容生成器')
    
    def test_generate_content_view_get(self):
        """
        测试生成内容页面GET请求（应该不允许）
        """
        response = self.client.get(reverse('content_generator:generate_content'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_result_page_view(self):
        """
        测试结果页面视图
        """
        url = reverse('content_generator:result_page', args=[self.content_request.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '生成的内容建议')
    
    def test_result_page_view_invalid_id(self):
        """
        测试结果页面视图（无效ID）
        """
        url = reverse('content_generator:result_page', args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_history_page_view_anonymous_user(self):
        """
        测试历史记录页面视图（匿名用户）
        """
        response = self.client.get(reverse('content_generator:history_page'))
        self.assertEqual(response.status_code, 200)
        # 匿名用户应该看到空的历史记录
        self.assertContains(response, '暂无历史记录')
    
    def test_history_page_view_authenticated_user(self):
        """
        测试历史记录页面视图（已认证用户）
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('content_generator:history_page'))
        self.assertEqual(response.status_code, 200)
        # 已认证用户应该看到他们的历史记录
        self.assertContains(response, '测试活动')

class APIViewsTest(TestCase):
    """
    API视图测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.content_request = ContentGenerationRequest.objects.create(
            user=self.user,
            event_description='测试活动',
            style_preference='casual',
            language='zh',
            audience_type='general',
            status='completed'
        )
        
        self.generated_content = GeneratedContent.objects.create(
            request=self.content_request,
            content='这是测试生成的内容',
            quality_score=85
        )
    
    def test_api_get_result(self):
        """
        测试API获取结果
        """
        url = reverse('content_generator:api_result_page', args=[self.content_request.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.content_request.id)
        self.assertEqual(len(data['data']['contents']), 1)
    
    def test_api_get_result_invalid_id(self):
        """
        测试API获取结果（无效ID）
        """
        url = reverse('content_generator:api_result_page', args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_api_create_content_request(self):
        """
        测试API创建内容请求
        """
        url = reverse('content_generator:api_generate_content')
        
        # 测试JSON数据
        data = {
            'event_description': 'API测试活动',
            'style_preference': 'formal',
            'language': 'zh',
            'audience_type': 'professionals'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('request_id', response_data)
    
    def test_api_create_content_request_invalid_data(self):
        """
        测试API创建内容请求（无效数据）
        """
        url = reverse('content_generator:api_generate_content')
        
        # 测试无效数据（缺少必填字段）
        data = {
            'event_description': 'API测试活动',
            'language': 'zh',
            'audience_type': 'professionals'
            # 缺少必填字段 style_preference
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
    
    def test_api_toggle_favorite(self):
        """
        测试API切换收藏状态
        """
        url = reverse('content_generator:api_toggle_favorite', args=[self.generated_content.id])
        
        # 初始状态应该是未收藏
        self.assertFalse(self.generated_content.is_favorite)
        
        # 切换为收藏
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['is_favorite'])
        
        # 再次切换为取消收藏
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertFalse(response_data['is_favorite'])

# 性能测试
class PerformanceTest(TestCase):
    """
    性能测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_multiple_content_requests(self):
        """
        测试创建多个内容请求的性能
        """
        import time
        
        start_time = time.time()
        
        # 创建100个内容请求
        for i in range(100):
            ContentGenerationRequest.objects.create(
                user=self.user,
                event_description=f'测试活动 {i}',
                style_preference='casual',
                language='zh',
                audience_type='general',
                status='completed'
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 确保100个请求都已创建
        self.assertEqual(ContentGenerationRequest.objects.count(), 100)
        
        # 性能检查（应该在合理时间内完成）
        self.assertLess(execution_time, 10.0)  # 10秒内完成