from django.test import TestCase, Client
from django.urls import reverse
from .models import ContentRequest

# Create your tests here.

class ContentGeneratorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_index_page_loads(self):
        """测试首页是否正常加载"""
        response = self.client.get(reverse('generator:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vanity')
        self.assertContains(response, '开始生成文案')
    
    def test_content_request_creation(self):
        """测试内容请求模型创建"""
        content_request = ContentRequest.objects.create(
            style='casual',
            language='zh-cn',
            audience_type='朋友',
            audience_description='年轻人群体',
            event_description='测试事件',
            additional_notes='测试备注'
        )
        self.assertEqual(content_request.style, 'casual')
        self.assertEqual(content_request.language, 'zh-cn')
        self.assertEqual(content_request.audience_type, '朋友')
    
    def test_form_submission(self):
        """测试表单提交"""
        form_data = {
            'style': 'casual',
            'language': 'zh-cn',
            'audience_type': '朋友和同学',
            'audience_description': '年轻人群体，喜欢时尚',
            'event_description': '今天去了咖啡厅',
            'additional_notes': '希望轻松一些'
        }
        response = self.client.post(reverse('generator:index'), form_data)
        self.assertEqual(response.status_code, 302)  # 重定向到结果页面
        
        # 验证数据库中创建了记录
        self.assertEqual(ContentRequest.objects.count(), 1)
        
        # 验证记录内容
        content_request = ContentRequest.objects.first()
        self.assertEqual(content_request.style, 'casual')
        self.assertEqual(content_request.audience_type, '朋友和同学')
    
    def test_results_page_with_session(self):
        """测试结果页面（有session数据）"""
        # 先创建一个内容请求
        content_request = ContentRequest.objects.create(
            style='casual',
            language='zh-cn',
            audience_type='朋友',
            audience_description='年轻人群体',
            generated_content=[
                {'id': 1, 'content': '测试文案1', 'style': '轻松随意'},
                {'id': 2, 'content': '测试文案2', 'style': '轻松随意'}
            ]
        )
        
        # 设置session
        session = self.client.session
        session['content_request_id'] = content_request.id
        session.save()
        
        # 访问结果页面
        response = self.client.get(reverse('generator:results'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '生成完成')
        self.assertContains(response, '测试文案1')
    
    def test_results_page_without_session(self):
        """测试结果页面（无session数据）"""
        response = self.client.get(reverse('generator:results'))
        self.assertEqual(response.status_code, 302)  # 重定向到首页
