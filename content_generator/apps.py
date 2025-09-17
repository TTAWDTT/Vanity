"""
内容生成器应用配置
"""
from django.apps import AppConfig

class ContentGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content_generator'
    verbose_name = '内容生成器'
    
    def ready(self):
        """
        应用启动时执行的初始化代码
        """
        # 导入信号处理器
        import content_generator.signals