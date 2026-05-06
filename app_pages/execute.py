import streamlit as st
import datetime
import time

# 🔥 IMPORT MODEL
from models.productivity_model import train_model, predict_productivity, find_best_hour


# -----------------------------
# AUTO PLAN
# -----------------------------
def generate_auto_plan(task):

    if not task.get("due"):
        return {}

    try:
        due_date = datetime.datetime.strptime(task["due"], "%Y-%m-%d").date()
    except:
        return {}

    plan = {}

    if task["type"].lower() == "exam":
        days_before = 4
    elif task["type"].lower() == "assignment":
        days_before = 3
    elif task["type"].lower() == "lab":
        days_before = 2
    else:
        days_before = 2

    for i in range(days_before):
        day = due_date - datetime.timedelta(days=(days_before - i))
        plan[day.strftime("%Y-%m-%d")] = "Work on task"

    return plan


def show():

    st.title("🎯 Execute")

    # 🔥 LOAD MODEL ONCE
    if "model" not in st.session_state:
        model, le = train_model()
        st.session_state.model = model
        st.session_state.le = le

    # 🔥 ADD HISTORY (NEW — SAFE)
    if "history" not in st.session_state:
        st.session_state.history = []

    # -----------------------------
    # STATE
    # -----------------------------
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    if "execute_day" not in st.session_state:
        st.session_state.execute_day = datetime.date.today()

    if "task_status" not in st.session_state:
        st.session_state.task_status = {}

    if "task_timer" not in st.session_state:
        st.session_state.task_timer = {}

    if "selected_task" not in st.session_state:
        st.session_state.selected_task = None

    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None

    if "is_running" not in st.session_state:
        st.session_state.is_running = False

    if "view_task" not in st.session_state:
        st.session_state.view_task = None

    # -----------------------------
    # DATE NAVIGATION
    # -----------------------------
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️"):
            st.session_state.execute_day -= datetime.timedelta(days=1)

    with col3:
        if st.button("➡️"):
            st.session_state.execute_day += datetime.timedelta(days=1)

    selected_day = st.session_state.execute_day
    selected_day_str = selected_day.strftime("%Y-%m-%d")

    st.subheader(selected_day.strftime("%A, %B %d"))

    # -----------------------------
    # GET TODAY TASKS
    # -----------------------------
    today_tasks = []

    for task in st.session_state.tasks:

        task_name = task["task_name"]
        step = None

        if "study_plan" in task and selected_day_str in task["study_plan"]:
            step = task["study_plan"][selected_day_str]
        else:
            auto_plan = generate_auto_plan(task)
            if selected_day_str in auto_plan:
                step = auto_plan[selected_day_str]

        if step:
            today_tasks.append((task_name, step))

    # -----------------------------
    # TASK LIST
    # -----------------------------
    st.markdown("### 📌 Today’s Tasks")

    if len(today_tasks) == 0:
        st.success("🎉 You're free today!")
        return

    model = st.session_state.model

    for task_name, step in today_tasks:

        task_id = f"{task_name}_{selected_day_str}"
        status = st.session_state.task_status.get(task_id)

        # 🔥 ORIGINAL ML LOGIC (UNCHANGED)
        task_type = ""
        for t in st.session_state.tasks:
            if t["task_name"] == task_name:
                task_type = t.get("type", "").lower()
                break

        if "exam" in task_type:
            base_hour = 20
        elif "quiz" in task_type:
            base_hour = 18
        elif "lab" in task_type:
            base_hour = 16
        else:
            base_hour = 17

        variation = abs(hash(task_name)) % 3

        input_data = [
            base_hour + variation,
            selected_day.weekday(),
            60 + variation * 10,
            variation,
            1,
            1,
            0,
            30
        ]

        model_hour = find_best_hour(model, input_data)

        # 🔥 FINAL DECISION (LEARNING ADDED HERE ONLY)
        if len(st.session_state.history) >= 3:
            base_best = max(set(st.session_state.history), key=st.session_state.history.count)

            # 🔥 STABLE variation (based on task name letters)
            variation = (sum(ord(c) for c in task_name) % 3) - 1

            best_hour = base_best + variation

            # keep within valid range
            best_hour = max(0, min(23, best_hour))
        else:
            best_hour = int((base_hour + model_hour) / 2)

        # FORMAT TIME
        period = "AM" if best_hour < 12 else "PM"
        hour_display = best_hour % 12
        if hour_display == 0:
            hour_display = 12

        col1, col2 = st.columns([3, 2])

        with col1:
            if status == "done":
                st.markdown(f"• ~~{task_name}~~ ✅ accomplished")
            elif status == "in_progress":
                st.markdown(f"• {task_name} 🟡 in progress")
            else:
                st.markdown(f"• {task_name} 🔥 Best at {hour_display} {period}")

        with col2:
            if st.button(f"View {task_name}", key=f"view_{task_name}"):
                st.session_state.view_task = (task_name, step)

    # -----------------------------
    # DETAILS (UNCHANGED)
    # -----------------------------
    if st.session_state.view_task is not None:

        task_name, step = st.session_state.view_task

        st.divider()
        st.markdown(f"### 📄 {task_name} details")
        st.write(step)

        if st.button("Close details"):
            st.session_state.view_task = None
            st.rerun()

    # -----------------------------
    # SELECT TASK
    # -----------------------------
    st.divider()
    st.markdown("### ▶ Start working on")

    selected = st.selectbox(
        "Choose a task",
        ["Select a task"] + [t[0] for t in today_tasks]
    )

    if selected != "Select a task":
        st.session_state.selected_task = selected

    # -----------------------------
    # START BUTTON
    # -----------------------------
    if st.session_state.selected_task and st.session_state.timer_start is None:

        st.markdown(f"### 🔥 {st.session_state.selected_task}")

        if st.button("Start"):
            st.session_state.timer_start = time.time()
            st.session_state.is_running = True

            task_id = f"{st.session_state.selected_task}_{selected_day_str}"
            st.session_state.task_status[task_id] = "in_progress"

            st.rerun()

    # -----------------------------
    # WORKING SECTION
    # -----------------------------
    if st.session_state.selected_task and st.session_state.timer_start is not None:

        task_id = f"{st.session_state.selected_task}_{selected_day_str}"

        st.divider()
        st.markdown(f"### 🔥 Working on: {st.session_state.selected_task}")

        stored_time = st.session_state.task_timer.get(task_id, 0)

        if st.session_state.is_running:
            elapsed = int(time.time() - st.session_state.timer_start + stored_time)
        else:
            elapsed = int(stored_time)

        mins, secs = divmod(elapsed, 60)
        st.markdown(f"## ⏱ {mins:02d}:{secs:02d}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Pause" if st.session_state.is_running else "Resume"):
                if st.session_state.is_running:
                    st.session_state.task_timer[task_id] = elapsed
                    st.session_state.is_running = False
                else:
                    st.session_state.timer_start = time.time()
                    st.session_state.is_running = True

        with col2:
            if st.button("Continue Later"):
                st.session_state.task_timer[task_id] = elapsed
                st.session_state.selected_task = None
                st.session_state.timer_start = None
                st.session_state.is_running = False
                st.rerun()

        with col3:
            if st.button("Finish"):

                # 🔥 SAVE USER BEHAVIOR (ONLY ADDITION)
                start_hour = datetime.datetime.fromtimestamp(
                    st.session_state.timer_start
                ).hour

                st.session_state.history.append(start_hour)

                st.session_state.task_status[task_id] = "done"
                st.session_state.task_timer[task_id] = elapsed

                st.session_state.selected_task = None
                st.session_state.timer_start = None
                st.session_state.is_running = False

                st.rerun()

        time.sleep(1)
        st.rerun()
