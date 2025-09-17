from django.contrib.auth.models import User

# 创建超级用户
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print("超级用户创建成功")