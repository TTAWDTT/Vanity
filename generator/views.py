from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from .models import ContentRequest
from .forms import ContentGenerationForm
import json
import random

# Create your views here.

class ContentGeneratorView(FormView):
    template_name = 'generator/index.html'
    form_class = ContentGenerationForm
    success_url = '/results/'
    
    def form_valid(self, form):
        # 保存表单数据
        content_request = form.save(commit=False)
        
        # 生成5条文案内容（这里使用模拟数据，实际应用中应该调用AI模型）
        generated_texts = self.generate_content(content_request)
        content_request.generated_content = generated_texts
        content_request.save()
        
        # 将ID存储到session中，以便在结果页面显示
        self.request.session['content_request_id'] = content_request.id
        
        messages.success(self.request, '内容生成成功！')
        return super().form_valid(form)
    
    def generate_content(self, content_request):
        """
        生成5条社交媒体文案
        在实际应用中，这里应该调用大模型API
        """
        # 基础文案模板，根据不同风格生成不同内容
        style_templates = {
            'casual': [
                "今天{event}，心情超级好！{emoji} {description}",
                "分享一下{event}的快乐时光～ {description} 😊",
                "生活就是要这样轻松愉快！{event} {description}",
                "记录美好的一天！{event} {description} ✨",
                "简单的快乐就是这样～{event} {description} 🌟"
            ],
            'formal': [
                "很荣幸能够{event}，{description}。感谢大家的支持与信任。",
                "今日{event}，{description}。希望能够继续为大家提供更好的服务。",
                "通过{event}，{description}。期待与大家有更多的合作机会。",
                "在{event}的过程中，{description}。非常感谢各位的参与和支持。",
                "此次{event}让我深有感触，{description}。愿与大家共同进步。"
            ],
            'humorous': [
                "哈哈哈，{event}简直笑死我了！{description} 😂",
                "今天{event}，我的表情包又要更新了！{description} 🤣",
                "论{event}的正确打开方式：{description} 哈哈哈哈",
                "警告：{event}有剧毒，{description}，笑得停不下来！😄",
                "今日份的沙雕时刻：{event}，{description} 🤪"
            ],
            'emotional': [
                "今天{event}，让我想起了很多往事。{description}，愿我们都能珍惜当下。💕",
                "每一次{event}都是成长的印记。{description}，感恩遇见的每一个人。🙏",
                "在{event}的这一刻，{description}。愿时光不老，友谊长存。❤️",
                "人生就是这样，{event}让我明白{description}。感谢生活给予的所有经历。🌹",
                "今天{event}，心中满怀感动。{description}。愿爱与美好一直陪伴着我们。💖"
            ],
            'inspirational': [
                "通过{event}，我更加坚信{description}。让我们一起努力，创造更美好的明天！💪",
                "每一次{event}都是新的开始。{description}，相信自己，永远不要放弃！🌟",
                "今天{event}让我深深体会到{description}。路虽远，行则必至！🚀",
                "在{event}中收获满满，{description}。记住，你比想象中更强大！⭐",
                "生命中的每一次{event}都有其意义。{description}，让我们勇敢追梦！🎯"
            ],
            'professional': [
                "今日{event}圆满结束，{description}。期待与更多优秀的合作伙伴携手共进。",
                "通过{event}，{description}。我们将继续秉承专业精神，为客户提供优质服务。",
                "在{event}中，{description}。感谢团队的辛勤付出和客户的信任支持。",
                "此次{event}收获颇丰，{description}。我们将持续创新，追求卓越。",
                "参与{event}让我们{description}。期待未来有更多机会为行业发展贡献力量。"
            ],
            'trendy': [
                "{event}简直太amazing了！{description} ✨ #今日份的美好 #生活记录",
                "今天{event}，vibe拉满！{description} 🔥 #mood #lifestyle",
                "OMG！{event}让我{description}，太绝了！💫 #daily #share",
                "今日{event}，氛围感满分！{description} 🌈 #moment #life",
                "Wow！{event}的体验感{description}，爱了爱了！💕 #experience #happy"
            ],
            'literary': [
                "春有百花秋有月，今日{event}，{description}。愿岁月不扰，时光静好。🌸",
                "时光荏苒，{event}如期而至。{description}，如诗如画，如梦如幻。📖",
                "今日{event}，恰如春风拂面，{description}。愿所有美好都如约而至。🍃",
                "人生若只如初见，{event}时{description}。愿我们都能在平凡中找到诗意。🌙",
                "今天{event}，仿佛置身于画卷之中。{description}，美好如斯。🎨"
            ],
            'minimalist': [
                "{event}。{description}。",
                "今日：{event}。{description}。",
                "{event}。感受：{description}。",
                "记录：{event}。{description}。",
                "{event}，{description}。简单美好。"
            ],
            'dramatic': [
                "天哪！{event}的那一刻，{description}！整个世界都安静了！😱",
                "不敢相信！{event}竟然{description}！这简直是命运的安排！✨",
                "震惊！今天{event}，{description}！我的内心久久不能平静！💥",
                "奇迹发生了！{event}让我{description}！这一刻值得铭记一生！🎭",
                "太不可思议了！{event}的时候{description}！人生就是这么戏剧化！🎪"
            ]
        }
        
        # 获取对应风格的模板
        templates = style_templates.get(content_request.style, style_templates['casual'])
        
        # 生成内容变量
        event = content_request.event_description or "参与这个活动"
        description = content_request.additional_notes or "收获了很多美好的回忆"
        
        # 根据风格添加表情符号
        emoji_map = {
            'casual': ['😊', '😄', '🌟', '✨', '💫'],
            'formal': ['🙏', '💼', '🤝', '📈', '⭐'],
            'humorous': ['😂', '🤣', '😄', '🤪', '😜'],
            'emotional': ['💕', '❤️', '🌹', '💖', '🙏'],
            'inspirational': ['💪', '🌟', '🚀', '⭐', '🎯'],
            'professional': ['💼', '📊', '🤝', '📈', '⚡'],
            'trendy': ['🔥', '✨', '💫', '🌈', '💕'],
            'literary': ['🌸', '📖', '🍃', '🌙', '🎨'],
            'minimalist': ['。', '·', '-', '|', ''],
            'dramatic': ['😱', '✨', '💥', '🎭', '🎪']
        }
        
        emojis = emoji_map.get(content_request.style, ['😊', '🌟', '✨'])
        
        # 生成5条不同的文案
        generated_texts = []
        for i in range(5):
            template = templates[i % len(templates)]
            emoji = emojis[i % len(emojis)]
            
            text = template.format(
                event=event,
                description=description,
                emoji=emoji
            )
            generated_texts.append({
                'id': i + 1,
                'content': text,
                'style': content_request.get_style_display()
            })
        
        return generated_texts


def results_view(request):
    """显示生成结果的页面"""
    content_request_id = request.session.get('content_request_id')
    
    if not content_request_id:
        messages.error(request, '没有找到生成的内容，请重新提交表单。')
        return redirect('/')
    
    try:
        content_request = ContentRequest.objects.get(id=content_request_id)
    except ContentRequest.DoesNotExist:
        messages.error(request, '内容不存在或已被删除。')
        return redirect('/')
    
    context = {
        'content_request': content_request,
        'generated_texts': content_request.generated_content or []
    }
    
    return render(request, 'generator/results.html', context)


def index_view(request):
    """首页视图"""
    return ContentGeneratorView.as_view()(request)
