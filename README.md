# Vanity - AI Social Media Content Generator

🎨 **Vanity** 是一个基于 Django 的 AI 驱动的社交媒体文案生成器，帮助用户快速生成专业的朋友圈和社交媒体内容。

## ✨ 功能特点

- 🎭 **多样化风格**：支持10种不同的内容风格（轻松随意、正式严肃、幽默风趣等）
- 🌍 **多语言支持**：支持中文、英文、日语、韩语等10种语言
- 🎯 **精准定位**：根据受众类型和描述生成针对性内容
- 📸 **图片上传**：支持配图上传（可选）
- 📋 **一键复制**：生成的文案可一键复制到剪贴板
- 📱 **响应式设计**：适配手机和电脑端使用

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Django 5.2+
- Pillow（图片处理）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Vanity
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **启动开发服务器**
```bash
python manage.py runserver
```

5. **访问应用**
打开浏览器访问 `http://localhost:8000`

## 📖 使用说明

### 基本流程

1. **填写表单**：
   - 📸 上传配图（可选）
   - 📝 描述事件内容（可选）
   - 🎭 选择内容风格（必需）
   - 🌍 选择语言
   - 👥 填写受众类型（必需）
   - 🎯 描述受众特征（必需）
   - 💡 添加补充说明（可选）

2. **生成内容**：
   - 点击"开始生成文案"按钮
   - 系统将生成5条不同的文案选项

3. **使用文案**：
   - 查看生成的文案
   - 一键复制喜欢的文案
   - 可复制全部文案进行选择

### 风格说明

| 风格 | 适用场景 | 示例特点 |
|------|----------|----------|
| 轻松随意 | 日常分享 | 语言轻松，表情丰富 |
| 正式严肃 | 商务场合 | 措辞正式，内容严谨 |
| 幽默风趣 | 搞笑内容 | 语言诙谐，氛围轻松 |
| 深情感人 | 情感表达 | 情感丰富，触动人心 |
| 励志向上 | 正能量 | 积极向上，激励人心 |
| 专业商务 | 职场分享 | 专业术语，商务风格 |
| 时尚潮流 | 年轻化表达 | 时尚用词，潮流元素 |
| 文艺清新 | 文学色彩 | 文艺气息，诗意表达 |
| 简约风格 | 简洁明了 | 言简意赅，干净利落 |
| 戏剧化 | 夸张表达 | 情感强烈，戏剧效果 |

## 🛠️ 技术架构

### 后端技术
- **Django 5.2**：Web 框架
- **SQLite**：数据库（可配置其他数据库）
- **Pillow**：图片处理

### 前端技术
- **HTML5 + CSS3**：页面结构和样式
- **Bootstrap 5**：响应式框架
- **JavaScript**：交互功能

### 项目结构
```
Vanity/
├── vanity_project/          # Django 项目配置
│   ├── settings.py         # 项目设置
│   ├── urls.py            # 主路由配置
│   └── ...
├── generator/              # 核心应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图逻辑
│   ├── forms.py           # 表单定义
│   ├── urls.py            # 应用路由
│   ├── admin.py           # 后台管理
│   └── templates/         # 模板文件
├── static/                # 静态文件
├── media/                 # 上传文件
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明
```

## 🔧 配置说明

### 数据库配置

默认使用 SQLite，生产环境建议使用 PostgreSQL 或 MySQL：

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vanity_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 媒体文件配置

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 静态文件配置

```python
# settings.py
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 🚀 部署指南

### 生产环境部署

1. **设置环境变量**
```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export ALLOWED_HOSTS='your-domain.com'
```

2. **收集静态文件**
```bash
python manage.py collectstatic
```

3. **使用生产服务器**
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn vanity_project.wsgi:application

# 或使用 uWSGI
pip install uwsgi
uwsgi --http :8000 --module vanity_project.wsgi
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "vanity_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔮 未来规划

- [ ] 集成真实的大语言模型 API（OpenAI GPT、百度文心等）
- [ ] 添加用户账号系统
- [ ] 支持文案历史记录
- [ ] 添加文案评分和优化建议
- [ ] 支持批量生成
- [ ] 添加更多社交平台适配
- [ ] 支持文案模板自定义
- [ ] 添加数据统计和分析

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[your-email@example.com]

---

<div align="center">
  <b>🎨 Vanity - 让每一条文案都闪闪发光</b>
</div>