# Vanity - 情绪与心情管理网站

Vanity是一个基于Django的Web应用程序，帮助用户管理日常任务、记录生活事件并生成日总结。

## 功能特点

- **任务管理**：创建、编辑、删除任务，设置优先级和意愿度（emoji表示）
- **事件记录**：记录生活中的有趣事件，支持图片上传和心情emoji
- **日总结功能**：自动生成每日工作总结和评估
- **LLM建议**：为任务和事件提供AI生成的建议和分享文案
- **暗黑风格界面**：现代化的暗黑主题设计
- **响应式设计**：支持桌面和移动设备
- **用户认证**：注册和登录功能

## 环境要求

- Python 3.8+
- Django 5.2+
- Pillow（用于图片处理）
- 其他依赖项请参考 `requirements.txt`

## 安装步骤

1. 克隆项目代码：
   ```
   git clone https://github.com/TTAWDTT/Vanity.git
   cd Vanity
   ```

2. 创建虚拟环境（可选但推荐）：
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 创建数据库迁移文件并应用：
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. 创建媒体文件目录：
   ```
   mkdir media
   ```

6. 创建超级用户（可选，用于访问管理后台）：
   ```
   python manage.py createsuperuser
   ```

## 运行项目

1. 启动开发服务器：
   ```
   python manage.py runserver
   ```

2. 在浏览器中访问 `http://127.0.0.1:8000` 查看应用

3. 访问管理后台 `http://127.0.0.1:8000/admin`（需要先创建超级用户）

## 项目结构

```
Vanity/
├── vanity_project/          # Django项目配置
├── content_generator/       # 核心应用
│   ├── models.py           # 数据模型（任务、事件、日总结、LLM建议）
│   ├── views.py            # 视图函数
│   ├── forms.py            # 表单定义
│   ├── urls.py             # URL路由
│   ├── signals.py          # 信号处理器
│   ├── tests.py            # 单元测试
│   ├── admin.py            # 管理后台配置
│   ├── apps.py             # 应用配置
│   └── migrations/         # 数据库迁移文件
├── templates/              # HTML模板
├── media/                  # 上传的媒体文件
├── static/                 # 静态文件（CSS, JS, 图片等）
├── manage.py              # Django管理脚本
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明文件
```

## 使用说明

### 注册与登录
1. 访问首页，点击"注册"创建新账户（用户名必须为"罗臻的仆从"）
2. 登录后进入任务管理页面

### 任务管理
1. 添加任务：点击"添加任务"按钮，填写任务标题、描述、优先级（!!!/!!/!）和意愿度（emoji）
2. 任务操作：可以标记完成/未完成、编辑、删除任务
3. LLM建议：点击"获取建议"按钮为任务获取AI建议

### 事件记录
1. 添加事件：点击"添加事件"按钮，填写事件标题、内容、心情（emoji）和上传图片
2. 生成分享文案：点击"生成分享文案"按钮为事件生成可分享的内容

### 日总结
1. 生成总结：点击"生成总结"按钮，系统会根据当天的任务完成情况生成总结和评估

## 数据模型

### Task（任务）
- title: 任务标题
- description: 任务描述
- priority: 优先级（!!!高/!!中/!低）
- willingness: 意愿度（😭很不情愿/😕不太情愿/😐一般/🙂比较愿意/😄很愿意）
- due_date: 截止时间
- completed: 是否完成

### Event（事件）
- title: 事件标题
- content: 事件内容
- mood: 心情（😄开心/😢悲伤/😠愤怒/😲惊讶/😴困倦/😍兴奋/🤔思考/😎酷）
- image: 图片

### DailySummary（日总结）
- date: 日期
- summary: 总结内容
- work_evaluation: 工作评估

### LLMAdvice（LLM建议）
- content: 建议内容
- advice_type: 建议类型（任务建议/事件分享/总结建议）
- related_id: 关联ID

## 管理后台

Django管理后台提供了对所有数据模型的管理功能。

1. 访问 `http://127.0.0.1:8000/admin`
2. 使用超级用户账号登录
3. 可以查看和管理所有任务、事件、日总结和LLM建议

## 部署到生产环境

### 使用Django自带服务器（不推荐用于生产）

1. 设置 `vanity_project/settings.py` 中的 `DEBUG = False`
2. 配置 `ALLOWED_HOSTS`
3. 配置数据库（推荐使用PostgreSQL或MySQL）
4. 使用 `python manage.py collectstatic` 收集静态文件
5. 配置环境变量保存敏感信息（如SECRET_KEY）

### 使用Nginx + Gunicorn（推荐）

1. 安装Gunicorn：
   ```
   pip install gunicorn
   ```

2. 安装Nginx并配置反向代理

3. 配置Gunicorn启动脚本

4. 配置数据库和静态文件服务

## 安全性说明

1. 用户只能访问自己创建的内容
2. 管理员可以查看所有内容
3. 表单数据有验证和清理
4. 用户认证使用Django内置系统

## 测试

项目包含了单元测试，可以通过以下命令运行：

```
python manage.py test
```

## 注意事项

1. 项目默认使用SQLite数据库，适用于开发和小型部署
2. 在生产环境中，请使用更安全的SECRET_KEY并将其保存在环境变量中
3. 媒体文件和静态文件在生产环境中应配置独立的存储服务
4. 建议定期备份数据库
5. 生产环境中应配置HTTPS
6. 定期更新依赖包以修复安全漏洞