import streamlit as st
import calendar
import datetime
from services.ai_service import generate_assignment_plan, distribute_steps


def show(client):

    st.title("📅 Organize")
    st.write("Click a date to see your tasks.")

    # -----------------------------
    # STATE
    # -----------------------------
    today = datetime.date.today()

    if "current_year" not in st.session_state:
        st.session_state.current_year = today.year

    if "current_month" not in st.session_state:
        st.session_state.current_month = today.month

    if "selected_day" not in st.session_state:
        st.session_state.selected_day = None

    if "manage_mode" not in st.session_state:
        st.session_state.manage_mode = None

    if "creating_plan" not in st.session_state:
        st.session_state.creating_plan = False

    if "plan_success" not in st.session_state:
        st.session_state.plan_success = False

    # -----------------------------
    # SUCCESS MESSAGE
    # -----------------------------
    if st.session_state.plan_success:
        st.success("Plan created successfully! Check Execute page.")
        st.session_state.plan_success = False

    # -----------------------------
    # MONTH NAVIGATION
    # -----------------------------
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️"):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1

    with col3:
        if st.button("➡️"):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1

    # -----------------------------
    # MONTH TITLE
    # -----------------------------
    month_name = calendar.month_name[st.session_state.current_month]
    st.header(f"{month_name} {st.session_state.current_year}")

    # -----------------------------
    # CALENDAR GRID
    # -----------------------------
    month_calendar = calendar.monthcalendar(
        st.session_state.current_year,
        st.session_state.current_month
    )

    for week in month_calendar:
        cols = st.columns(7)

        for i, day in enumerate(week):
            if day == 0:
                continue

            full_date = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{day:02d}"

            has_task = any(task["due"] == full_date for task in st.session_state.tasks)

            label = str(day)
            if has_task:
                label += " 🔴"

            if cols[i].button(label, key=f"{day}_{st.session_state.current_month}"):
                st.session_state.selected_day = day

    # -----------------------------
    # SHOW TASKS
    # -----------------------------
    if st.session_state.selected_day:

        selected_date = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{st.session_state.selected_day:02d}"

        st.divider()
        st.subheader(f"📌 Tasks on {selected_date}")

        tasks_found = False

        for i, task in enumerate(st.session_state.tasks):

            if task["due"] == selected_date:

                tasks_found = True

                col1, col2 = st.columns([3, 2])

                with col1:
                    st.markdown(f"• **{task['task_name']} ({task['type']})**")

                with col2:
                    button_text = "Edit Plan" if "study_plan" in task else "Create Plan"

                    if st.button(button_text, key=f"plan_{i}"):
                        st.session_state.plan_task_index = i
                        st.session_state.creating_plan = True

        if not tasks_found:
            st.info("No tasks on this day.")

    # -----------------------------
    # PLAN PANEL (WITH SAVED INPUT)
    # -----------------------------
    if st.session_state.creating_plan:

        task = st.session_state.tasks[st.session_state.plan_task_index]

        st.divider()
        st.markdown(f"### 🧠 Plan for {task['task_name']}")

        requirements = st.text_area(
            "Paste assignment or exam requirements",
            value=task.get("requirements", "")
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Plan"):

                steps = generate_assignment_plan(client, requirements)
                plan = distribute_steps(steps, task["due"])

                task["study_plan"] = plan
                task["requirements"] = requirements  # ✅ SAVE INPUT

                st.session_state.plan_success = True
                st.session_state.creating_plan = False
                st.rerun()

        with col2:
            if st.button("Cancel"):
                st.session_state.creating_plan = False
                st.rerun()

    # -----------------------------
    # MANAGE TASKS
    # -----------------------------
    st.divider()
    st.subheader("⚙️ Manage Tasks")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Edit Task"):
            st.session_state.manage_mode = "edit"

    with col2:
        if st.button("Delete Task"):
            st.session_state.manage_mode = "delete"

    # -----------------------------
    # EDIT MODE
    # -----------------------------
    if st.session_state.manage_mode == "edit":

        if st.session_state.tasks:

            task_names = [task["task_name"] for task in st.session_state.tasks]

            selected_task_name = st.selectbox("Select task", task_names)

            selected_index = next(
                i for i, t in enumerate(st.session_state.tasks)
                if t["task_name"] == selected_task_name
            )

            task = st.session_state.tasks[selected_index]

            new_name = st.text_input("Task name", value=task["task_name"])
            new_type = st.text_input("Type", value=task["type"])
            new_due = st.text_input("Due date", value=task["due"])

            if st.button("Save"):
                task["task_name"] = new_name
                task["type"] = new_type
                task["due"] = new_due
                st.success("Task updated!")
                st.session_state.manage_mode = None
                st.rerun()

        else:
            st.info("No tasks available.")

    # -----------------------------
    # DELETE MODE
    # -----------------------------
    elif st.session_state.manage_mode == "delete":

        if st.session_state.tasks:

            task_names = [task["task_name"] for task in st.session_state.tasks]

            selected_task_name = st.selectbox("Select task", task_names)

            selected_index = next(
                i for i, t in enumerate(st.session_state.tasks)
                if t["task_name"] == selected_task_name
            )

            if st.button("Delete Selected Task"):
                st.session_state.tasks.pop(selected_index)
                st.success("Task deleted!")
                st.session_state.manage_mode = None
                st.rerun()

        else:
            st.info("No tasks available.")
