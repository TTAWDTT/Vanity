from django.contrib import admin
from .models import ContentRequest

# Register your models here.

@admin.register(ContentRequest)
class ContentRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'get_style_display', 
        'get_language_display', 
        'audience_type', 
        'created_at'
    ]
    list_filter = [
        'style', 
        'language', 
        'created_at'
    ]
    search_fields = [
        'audience_type', 
        'event_description', 
        'audience_description'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('style', 'language', 'audience_type')
        }),
        ('内容描述', {
            'fields': ('image', 'event_description', 'audience_description', 'additional_notes')
        }),
        ('生成结果', {
            'fields': ('generated_content',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_add_permission(self, request):
        return False  # 不允许从后台添加，只能通过前端表单
