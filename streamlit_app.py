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
                st.info("✅ 已创建默认管理员用户: admin / admin123")
        except Exception as e:
            st.error(f"数据库初始化失败: {e}")
            st.stop()
    
    ensure_database()
    
except Exception as e:
    st.error(f"Django 初始化失败: {e}")
    st.stop()

# Page config with dark theme
st.set_page_config(
    page_title='Vanity - 任务管理', 
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS to match original dark theme
st.markdown("""
<style>
    .stApp {
        background: #0f0f23;
        color: #ffffff;
    }
    
    .task-card {
        background: #16213e;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .task-card.completed {
        opacity: 0.7;
        border-left: 4px solid #10b981;
    }
    
    .priority-high { color: #ef4444; }
    .priority-medium { color: #f59e0b; }
    .priority-low { color: #10b981; }
    
    .stat-card {
        background: #16213e;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for user selection and navigation
with st.sidebar:
    st.markdown("### 🎭 Vanity")
    
    # User selection
    try:
        users = User.objects.all()
        if users.exists():
            user_options = [u.username for u in users]
            selected_username = st.selectbox('选择用户', user_options, key='user_select')
            current_user = User.objects.get(username=selected_username)
        else:
            st.error("没有找到用户")
            st.stop()
    except Exception as e:
        st.error(f"用户查询失败: {e}")
        st.stop()
    
    # Navigation
    page = st.radio("页面", ["📋 任务管理", "📖 日记", "📊 统计"])

# Main content area
if page == "📋 任务管理":
    st.title("📋 任务管理")
    
    # Stats display
    tasks = Task.objects.filter(user=current_user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    today = timezone.now().date()
    overdue_tasks = tasks.filter(due_date__lt=timezone.now(), completed=False).count()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="color: #3b82f6; margin: 0;">{total_tasks}</h2>
            <p style="color: #a0a0a0; margin: 0;">总任务</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="color: #10b981; margin: 0;">{completed_tasks}</h2>
            <p style="color: #a0a0a0; margin: 0;">已完成</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="color: #f59e0b; margin: 0;">{pending_tasks}</h2>
            <p style="color: #a0a0a0; margin: 0;">待完成</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="color: #ef4444; margin: 0;">{overdue_tasks}</h2>
            <p style="color: #a0a0a0; margin: 0;">已逾期</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Add new task section
    with st.expander("➕ 添加新任务", expanded=False):
        with st.form("add_task_form"):
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
            
            due_date = st.date_input("📅 截止日期（可选）", value=None)
            due_time = st.time_input("⏰ 截止时间（可选）", value=None)
            
            submitted = st.form_submit_button("✅ 创建任务", use_container_width=True)
            
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
                st.rerun()
    
    # Filter options
    st.markdown("### 🔍 筛选任务")
    filter_option = st.selectbox("显示", ['全部', '待完成', '已完成', '逾期'], key='filter')
    
    # Task list
    st.markdown("### 📋 任务列表")
    
    # Apply filters
    if filter_option == '待完成':
        display_tasks = tasks.filter(completed=False)
    elif filter_option == '已完成':
        display_tasks = tasks.filter(completed=True)
    elif filter_option == '逾期':
        display_tasks = tasks.filter(due_date__lt=timezone.now(), completed=False)
    else:
        display_tasks = tasks
    
    display_tasks = display_tasks.order_by('-created_at')
    
    if display_tasks.exists():
        for task in display_tasks:
            # Priority color mapping
            priority_colors = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
            priority_color = priority_colors.get(task.priority, '#6b7280')
            
            # Task card
            card_class = "task-card completed" if task.completed else "task-card"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0 0 0.5rem 0; color: #ffffff;">{'✅ ' if task.completed else ''}{task.title}</h3>
                        <div style="display: flex; gap: 1rem; align-items: center; font-size: 0.9rem; color: #a0a0a0;">
                            <span style="color: {priority_color};">{task.get_priority_display()}</span>
                            <span style="font-size: 1.2rem;">{task.willingness}</span>
                            {f'<span>📅 {task.due_date.strftime("%m月%d日 %H:%M")}</span>' if task.due_date else ''}
                            <span>⏰ {task.created_at.strftime("%m月%d日")}</span>
                        </div>
                    </div>
                </div>
                {f'<p style="color: #a0a0a0; margin: 1rem 0;">{task.description}</p>' if task.description else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if st.button(f"{'❌ 取消完成' if task.completed else '✅ 完成'}", key=f"toggle_{task.id}"):
                    task.completed = not task.completed
                    task.save()
                    st.rerun()
            
            with col2:
                if st.button(f"🗑️ 删除", key=f"delete_{task.id}"):
                    task.delete()
                    st.success("任务已删除")
                    st.rerun()
            
            with col3:
                if st.button(f"💡 建议", key=f"advice_{task.id}"):
                    st.info("🤖 AI建议功能开发中...")
    
    else:
        st.markdown("""
        <div class="task-card" style="text-align: center; padding: 2rem;">
            <i class="fas fa-tasks" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">📋</i>
            <p style="color: #6b7280;">还没有任务哦，点击"添加新任务"开始吧！</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📖 日记":
    st.title("📖 日记")
    
    # Events display
    events = Event.objects.filter(user=current_user).order_by('-created_at')
    
    with st.expander("✍️ 写新日记", expanded=False):
        with st.form("add_event_form"):
            event_title = st.text_input("📝 标题")
            event_content = st.text_area("📄 内容", height=150)
            mood = st.selectbox("😊 心情", 
                options=['😄', '😢', '😠', '😲', '😴', '😍', '🤔', '😎'],
                format_func=lambda x: {'😄': '😄 开心', '😢': '😢 悲伤', '😠': '😠 愤怒', '😲': '😲 惊讶', '😴': '😴 困倦', '😍': '😍 兴奋', '🤔': '🤔 思考', '😎': '😎 酷'}[x]
            )
            
            if st.form_submit_button("📝 保存日记"):
                Event.objects.create(
                    user=current_user,
                    title=event_title,
                    content=event_content,
                    mood=mood
                )
                st.success("日记已保存")
                st.rerun()
    
    # Display events
    if events.exists():
        for event in events:
            st.markdown(f"""
            <div class="task-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #3b82f6;">{event.title}</h3>
                    <span style="font-size: 1.5rem;">{event.mood}</span>
                </div>
                <p style="color: #a0a0a0; line-height: 1.6;">{event.content}</p>
                <p style="color: #6b7280; font-size: 0.875rem; margin-top: 1rem;">
                    📅 {event.created_at.strftime("%Y年%m月%d日 %H:%M")}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有日记记录，开始记录你的每一天吧！")

elif page == "📊 统计":
    st.title("📊 数据统计")
    
    # Task statistics
    tasks = Task.objects.filter(user=current_user)
    events = Event.objects.filter(user=current_user)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("任务统计")
        
        # Priority distribution
        priority_counts = {
            'high': tasks.filter(priority='high').count(),
            'medium': tasks.filter(priority='medium').count(),
            'low': tasks.filter(priority='low').count()
        }
        
        st.bar_chart(priority_counts)
        
        # Completion rate
        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        if total > 0:
            completion_rate = (completed / total) * 100
            st.metric("完成率", f"{completion_rate:.1f}%")
    
    with col2:
        st.subheader("心情统计")
        
        if events.exists():
            mood_counts = {}
            for event in events:
                mood = event.mood
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            st.bar_chart(mood_counts)
        else:
            st.info("暂无心情数据")

# Footer
st.markdown("---")
st.markdown("💖 **Vanity** - 让生活更有条理 | 当前用户: " + current_user.username)
