"""
通用工具函数模块
"""

def is_mobile_device(request):
    """
    检测是否为移动端设备
    
    Args:
        request: Django请求对象
        
    Returns:
        bool: 如果是移动设备返回True，否则返回False
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipod', 'blackberry', 
        'windows phone', 'iemobile', 'opera mini', 'mobile safari'
    ]
    return any(keyword in user_agent for keyword in mobile_keywords)