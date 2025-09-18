import os
import django
import streamlit as st
from datetime import datetime

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vanity_project.settings')
django.setup()

from django.contrib.auth.models import User
from content_generator.models import Task
from django.utils import timezone

st.set_page_config(page_title='Vanity - Streamlit', layout='wide')

st.title('Vanity - 任务管理（Streamlit）')

# Simple authentication selector (developer convenience)
users = User.objects.all()
user_map = {u.username: u for u in users}
selected_user = st.selectbox('以哪个用户查看/操作', ['-- 请选择用户 --'] + [u.username for u in users])

if selected_user and selected_user != '-- 请选择用户 --':
    user = user_map[selected_user]

    st.subheader('创建新任务')
    with st.form('create_task'):
        title = st.text_input('任务标题')
        description = st.text_area('任务描述')
        priority = st.selectbox('优先级', ['high', 'medium', 'low'], index=1)
        willingness = st.selectbox('意愿度', ['😭','😕','😐','🙂','😄'], index=2)
        due_date = st.datetime_input('截止时间（可选）', value=None)
        submitted = st.form_submit_button('创建')
        if submitted:
            t = Task.objects.create(
                user=user,
                title=title,
                description=description,
                priority=priority,
                willingness=willingness,
                due_date=due_date if due_date else None,
            )
            st.success(f'已创建任务：{t.title}')

    st.subheader('任务列表')
    tasks = Task.objects.filter(user=user).order_by('-created_at')
    for task in tasks:
        cols = st.columns([6, 1, 1, 2])
        cols[0].markdown(f"**{task.title}**  \n  {task.description or ''}")
        cols[1].markdown(f"优先级: {task.get_priority_display()}")
        cols[2].markdown(f"意愿: {task.willingness}")
        if cols[3].button('切换完成', key=f"toggle-{task.id}"):
            task.completed = not task.completed
            task.save()
            st.experimental_rerun()

else:
    st.info('请选择一个用户来查看其任务')
