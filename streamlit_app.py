import os
import django
import streamlit as st
from datetime import datetime, timedelta
import sys

# Initialize Django with error handling
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vanity_project.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from content_generator.models import Task, Event, DailySummary
    from django.core.management import call_command
    from django.db import connection
    from django.utils import timezone
    
    # Ensure database is migrated and has at least one user
    def ensure_database():
        try:
            # Try to run migrations
            call_command('migrate', verbosity=0, interactive=False)
            
            # Create a default user if none exists
            if not User.objects.exists():
                User.objects.create_user(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    is_staff=True,
                    is_superuser=True
                )
        except Exception as e:
            st.error(f"数据库初始化失败: {e}")
            st.stop()
    
    ensure_database()
    
except Exception as e:
    st.error(f"Django 初始化失败: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title='Vanity - 任务管理', 
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Complete CSS replication of original design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    :root {
        /* 深色主题 */
        --bg-primary: #0f0f23;
        --bg-secondary: #1a1a2e;
        --bg-card: #16213e;
        --bg-sidebar: #0f0f23;
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --text-muted: #6b7280;
        --accent: #3b82f6;
        --accent-light: #60a5fa;
        --border: #334155;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --shadow: rgba(0, 0, 0, 0.3);
        --blur-bg: rgba(22, 33, 62, 0.8);
    }

    [data-theme="light"] {
        /* 浅色主题 */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-card: #ffffff;
        --bg-sidebar: #f1f5f9;
        --text-primary: #1f2937;
        --text-secondary: #4b5563;
        --text-muted: #9ca3af;
        --accent: #3b82f6;
        --accent-light: #60a5fa;
        --border: #e2e8f0;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --shadow: rgba(0, 0, 0, 0.1);
        --blur-bg: rgba(248, 250, 252, 0.9);
    }

    /* Override Streamlit default styles */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 0;
        max-width: none;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Theme Toggle */
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 50px;
        padding: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px var(--shadow);
    }

    .theme-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px var(--shadow);
    }

    .theme-toggle i {
        font-size: 1.2rem;
        padding: 8px;
        border-radius: 50%;
        transition: all 0.3s ease;
    }

    /* Sidebar */
    .custom-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        width: 280px;
        height: 100vh;
        background: var(--bg-sidebar);
        border-right: 1px solid var(--border);
        z-index: 100;
        overflow-y: auto;
        transition: all 0.3s ease;
    }

    .sidebar-header {
        padding: 2rem 1.5rem 1.5rem;
        border-bottom: 1px solid var(--border);
    }

    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .nav-menu {
        padding: 1.5rem 0;
    }

    .nav-item {
        margin: 0.5rem 1rem;
    }

    .nav-link {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        color: var(--text-secondary);
        text-decoration: none;
        border-radius: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }

    .nav-link:hover, .nav-link.active {
        background: var(--accent);
        color: white;
        transform: translateX(8px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }

    .nav-link::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: 0.6s;
    }

    .nav-link:hover::before {
        left: 100%;
    }

    /* Main Content */
    .main-content {
        margin-left: 280px;
        min-height: 100vh;
        background: var(--bg-secondary);
    }

    .header {
        background: var(--blur-bg);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border);
        padding: 1.5rem 2rem;
        position: sticky;
        top: 0;
        z-index: 50;
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: var(--text-secondary);
    }

    .content-area {
        padding: 2rem;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px var(--shadow);
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px var(--shadow);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }

    /* Action Bar */
    .action-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        gap: 1rem;
    }

    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 12px;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        font-family: inherit;
    }

    .btn-primary {
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        color: white;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }

    .btn-outline {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text-primary);
    }

    .btn-outline:hover {
        background: var(--bg-card);
        transform: translateY(-2px);
    }

    .btn-success {
        background: var(--success);
        color: white;
    }

    .btn-warning {
        background: var(--warning);
        color: white;
    }

    .btn-danger {
        background: var(--danger);
        color: white;
    }

    .btn-sm {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
    }

    /* Filter Bar */
    .filter-bar {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    .filter-btn {
        padding: 0.5rem 1rem;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--bg-card);
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
    }

    .filter-btn:hover, .filter-btn.active {
        background: var(--accent);
        color: white;
        border-color: var(--accent);
    }

    /* Task Grid */
    .task-grid {
        display: grid;
        gap: 1.5rem;
    }

    .task-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px var(--shadow);
        position: relative;
        overflow: hidden;
    }

    .task-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px var(--shadow);
    }

    .task-card.completed {
        opacity: 0.7;
        border-left: 4px solid var(--success);
    }

    .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }

    .task-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        line-height: 1.4;
        color: var(--text-primary);
    }

    .task-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
    }

    .priority-indicator {
        font-size: 1.2rem;
        filter: drop-shadow(0 2px 4px var(--shadow));
    }

    .willingness-indicator {
        font-size: 1.5rem;
        cursor: pointer;
        filter: drop-shadow(0 2px 4px var(--shadow));
        transition: transform 0.2s ease;
    }

    .willingness-indicator:hover {
        transform: scale(1.2);
    }

    .task-description {
        color: var(--text-secondary);
        margin: 1rem 0;
        line-height: 1.6;
    }

    .task-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }

    .task-date {
        font-size: 0.875rem;
        color: var(--text-muted);
    }

    /* Form Card */
    .form-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px var(--shadow);
        transition: all 0.3s ease;
        margin-bottom: 2rem;
    }

    .form-card:hover {
        box-shadow: 0 8px 30px var(--shadow);
    }

    .form-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
    }

    /* Override Streamlit input styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in-out;
    }

    .slide-up {
        animation: slideUp 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .custom-sidebar {
            transform: translateX(-100%);
        }

        .main-content {
            margin-left: 0;
        }

        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .action-bar {
            flex-direction: column;
            gap: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'task_list'
if 'current_user' not in st.session_state:
    users = User.objects.all()
    if users.exists():
        st.session_state.current_user = users.first()
    else:
        st.error("没有找到用户")
        st.stop()
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = 'all'

# Get current user
current_user = st.session_state.current_user

# Page layout with exact original structure
st.markdown(f"""
<div class="theme-toggle" onclick="toggleTheme()">
    <i class="fas fa-sun"></i>
    <i class="fas fa-moon"></i>
</div>

<!-- Sidebar -->
<nav class="custom-sidebar">
    <div class="sidebar-header">
        <div class="logo">Vanity</div>
    </div>
    <div class="nav-menu">
        <div class="nav-item">
            <div class="nav-link {'active' if st.session_state.current_page == 'task_list' else ''}" 
                 onclick="setPage('task_list')">
                <i class="fas fa-tasks"></i>
                <span>任务管理</span>
            </div>
        </div>
        <div class="nav-item">
            <div class="nav-link {'active' if st.session_state.current_page == 'event_list' else ''}" 
                 onclick="setPage('event_list')">
                <i class="fas fa-book"></i>
                <span>日记</span>
            </div>
        </div>
        <div class="nav-item">
            <div class="nav-link {'active' if st.session_state.current_page == 'daily_summary' else ''}" 
                 onclick="setPage('daily_summary')">
                <i class="fas fa-chart-line"></i>
                <span>日总结</span>
            </div>
        </div>
        <div class="nav-item">
            <div class="nav-link">
                <i class="fas fa-sign-out-alt"></i>
                <span>退出登录</span>
            </div>
        </div>
    </div>
</nav>

<!-- Main Content -->
<main class="main-content">
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1 class="page-title">任务管理</h1>
            <div class="user-info">
                <i class="fas fa-user"></i>
                <span>{current_user.username}</span>
            </div>
        </div>
    </header>

    <!-- Content Area -->
    <div class="content-area">
""", unsafe_allow_html=True)

# Stats display - exactly like original
tasks = Task.objects.filter(user=current_user)
total_tasks = tasks.count()
completed_tasks = tasks.filter(completed=True).count()
pending_tasks = total_tasks - completed_tasks
today = timezone.now().date()
overdue_tasks = tasks.filter(due_date__lt=timezone.now(), completed=False).count()

st.markdown(f"""
        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" style="color: var(--accent);">{total_tasks}</div>
                <div class="stat-label">总任务</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--success);">{completed_tasks}</div>
                <div class="stat-label">已完成</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--warning);">{pending_tasks}</div>
                <div class="stat-label">待完成</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--danger);">{overdue_tasks}</div>
                <div class="stat-label">已逾期</div>
            </div>
        </div>
""", unsafe_allow_html=True)

# Action Bar
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("➕ 添加任务", key="add_task_btn"):
        st.session_state.show_add_form = not st.session_state.get('show_add_form', False)

with col2:
    filter_options = ['全部', '待完成', '已完成', '逾期']
    filter_mapping = {'全部': 'all', '待完成': 'pending', '已完成': 'completed', '逾期': 'overdue'}
    
    filter_selection = st.selectbox("筛选", filter_options, 
                                  index=filter_options.index([k for k, v in filter_mapping.items() if v == st.session_state.filter_status][0]),
                                  key="filter_select")
    st.session_state.filter_status = filter_mapping[filter_selection]

# Add Task Form (when button is clicked)
if st.session_state.get('show_add_form', False):
    st.markdown("""
    <div class="form-card">
        <h2 class="form-title">
            <i class="fas fa-plus-circle"></i>
            添加新任务
        </h2>
    """, unsafe_allow_html=True)
    
    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("📝 任务标题", placeholder="输入任务标题...")
        task_description = st.text_area("📄 任务描述", placeholder="描述任务详情（可选）...")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("🏆 优先级", 
                options=['high', 'medium', 'low'],
                format_func=lambda x: {'high': '♛♛♛ 高', 'medium': '♛♛ 中', 'low': '♛ 低'}[x],
                index=1
            )
        
        with col2:
            willingness = st.selectbox("😊 意愿度",
                options=['😭', '😕', '😐', '🙂', '😄'],
                format_func=lambda x: {'😭': '😭 很不情愿', '😕': '😕 不太情愿', '😐': '😐 一般', '🙂': '🙂 比较愿意', '😄': '😄 很愿意'}[x],
                index=2
            )
        
        col3, col4 = st.columns(2)
        with col3:
            due_date = st.date_input("📅 截止日期（可选）", value=None)
        with col4:
            due_time = st.time_input("⏰ 截止时间（可选）", value=None)
        
        submitted = st.form_submit_button("✅ 创建任务")
        
        if submitted and task_title:
            due_datetime = None
            if due_date and due_time:
                due_datetime = timezone.make_aware(datetime.combine(due_date, due_time))
            elif due_date:
                due_datetime = timezone.make_aware(datetime.combine(due_date, datetime.min.time()))
            
            Task.objects.create(
                user=current_user,
                title=task_title,
                description=task_description,
                priority=priority,
                willingness=willingness,
                due_date=due_datetime
            )
            st.success(f"✅ 已创建任务：{task_title}")
            st.session_state.show_add_form = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Task List
st.markdown("### 📋 任务列表")

# Apply filters - exactly like original
if st.session_state.filter_status == 'pending':
    display_tasks = tasks.filter(completed=False)
elif st.session_state.filter_status == 'completed':
    display_tasks = tasks.filter(completed=True)
elif st.session_state.filter_status == 'overdue':
    display_tasks = tasks.filter(due_date__lt=timezone.now(), completed=False)
else:
    display_tasks = tasks

display_tasks = display_tasks.order_by('-created_at')

if display_tasks.exists():
    for task in display_tasks:
        # Priority display mapping - exactly like original
        priority_display = {'high': '♛♛♛', 'medium': '♛♛', 'low': '♛'}[task.priority]
        priority_colors = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
        priority_color = priority_colors.get(task.priority, '#6b7280')
        
        # Task card - exact replica
        card_class = "task-card completed" if task.completed else "task-card"
        
        st.markdown(f"""
        <div class="{card_class} slide-up">
            <div class="task-header">
                <div>
                    <h3 class="task-title">{'✅ ' if task.completed else ''}{task.title}</h3>
                    <div class="task-meta">
                        <span class="priority-indicator" style="color: {priority_color};" title="优先级">{priority_display}</span>
                        <span class="willingness-indicator" title="意愿度">{task.willingness}</span>
                        {f'<span class="task-date"><i class="fas fa-calendar"></i> {task.due_date.strftime("%m月%d日 %H:%M")}</span>' if task.due_date else ''}
                        <span class="task-date"><i class="fas fa-clock"></i> {task.created_at.strftime("%m月%d日")}</span>
                    </div>
                </div>
            </div>
            {f'<div class="task-description">{task.description[:100]}{"..." if len(task.description) > 100 else ""}</div>' if task.description else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons - exact replica
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            if st.button(f"{'❌ 取消完成' if task.completed else '✅ 完成'}", 
                        key=f"toggle_{task.id}", 
                        help="切换任务完成状态"):
                task.completed = not task.completed
                task.save()
                st.rerun()
        
        with col2:
            if st.button("✏️ 编辑", key=f"edit_{task.id}", help="编辑任务"):
                st.info("编辑功能：请在原Django应用中编辑任务")
        
        with col3:
            if st.button("💡 建议", key=f"advice_{task.id}", help="获取AI建议"):
                st.info("🤖 AI建议功能开发中...")
        
        with col4:
            if st.button("🗑️ 删除", key=f"delete_{task.id}", help="删除任务"):
                task.delete()
                st.success("任务已删除")
                st.rerun()

else:
    # Empty state - exact replica
    st.markdown("""
    <div class="task-card">
        <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
            <i class="fas fa-tasks" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
            <p>还没有任务哦，点击"添加任务"开始吧！</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Close main content
st.markdown("""
    </div>
</main>

<script>
    // Theme toggle functionality
    function toggleTheme() {
        const root = document.documentElement;
        const currentTheme = root.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }
    
    // Load saved theme
    document.addEventListener('DOMContentLoaded', function() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    });
    
    // Add slide-up animation to task cards
    document.addEventListener('DOMContentLoaded', function() {
        const cards = document.querySelectorAll('.task-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('slide-up');
            }, index * 100);
        });
    });
</script>
""", unsafe_allow_html=True)
