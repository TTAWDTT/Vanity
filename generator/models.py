from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.

class ContentRequest(models.Model):
    LANGUAGE_CHOICES = [
        ('zh-cn', '中文简体'),
        ('zh-tw', '中文繁體'), 
        ('en', 'English'),
        ('ja', '日本語'),
        ('ko', '한국어'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('de', 'Deutsch'),
        ('pt', 'Português'),
        ('ru', 'Русский'),
    ]
    
    STYLE_CHOICES = [
        ('casual', '轻松随意'),
        ('formal', '正式严肃'),
        ('humorous', '幽默风趣'),
        ('emotional', '深情感人'),
        ('inspirational', '励志向上'),
        ('professional', '专业商务'),
        ('trendy', '时尚潮流'),
        ('literary', '文艺清新'),
        ('minimalist', '简约风格'),
        ('dramatic', '戏剧化'),
    ]
    
    # 上传的配图（可选）
    image = models.ImageField(
        upload_to='uploads/images/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="支持 JPG, JPEG, PNG, GIF 格式"
    )
    
    # 描述的事件（可选）
    event_description = models.TextField(
        blank=True, 
        null=True,
        max_length=1000,
        help_text="描述要陈述的事件内容"
    )
    
    # 想要的风格（重要）
    style = models.CharField(
        max_length=20,
        choices=STYLE_CHOICES,
        help_text="选择想要的内容风格"
    )
    
    # 语言
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='zh-cn',
        help_text="选择生成内容的语言"
    )
    
    # 受众类型
    audience_type = models.CharField(
        max_length=100,
        help_text="目标受众类型，如：朋友、同事、粉丝等"
    )
    
    # 受众描述
    audience_description = models.TextField(
        max_length=500,
        help_text="详细描述你的受众特征"
    )
    
    # 补充说明
    additional_notes = models.TextField(
        blank=True,
        null=True, 
        max_length=500,
        help_text="其他补充说明"
    )
    
    # 生成的内容（JSON 格式存储5条文案）
    generated_content = models.JSONField(
        blank=True,
        null=True,
        help_text="存储生成的5条文案内容"
    )
    
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "内容生成请求"
        verbose_name_plural = "内容生成请求"
    
    def __str__(self):
        return f"内容请求 - {self.get_style_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
