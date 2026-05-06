import streamlit as st
from services.ai_service import organize_task
from services.speech_service import transcribe_audio
from audio_recorder_streamlit import audio_recorder
import datetime


def show(client):

    st.title("🧠 Capture")
    st.write("Brain dump your tasks here.")

    # -----------------------------
    # STATE
    # -----------------------------
    if "input_mode" not in st.session_state:
        st.session_state.input_mode = None

    if "pending_tasks" not in st.session_state:
        st.session_state.pending_tasks = []

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    # -----------------------------
    # MODE SELECTION
    # -----------------------------
    st.write("How do you want to add tasks?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✍️ Write"):
            st.session_state.input_mode = "write"

    with col2:
        if st.button("🎤 Speak"):
            st.session_state.input_mode = "speak"

    st.markdown("<br>", unsafe_allow_html=True)

    user_input = ""

    # -----------------------------
    # WRITE MODE
    # -----------------------------
    if st.session_state.input_mode == "write":

        st.write("Enter your tasks (natural language):")

        user_input = st.text_area(
            "",
            placeholder="Example: I have a math exam next Thursday..."
        )

    # -----------------------------
    # SPEAK MODE
    # -----------------------------
    elif st.session_state.input_mode == "speak":

        st.markdown("🎤 Tap the mic and start speaking")

        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

        audio_bytes = audio_recorder(
            text="",
            icon_size="2x",
            neutral_color="#FFFFFF",
            recording_color="#FF4B4B"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if audio_bytes:
            transcript = transcribe_audio(client, audio_bytes)
            user_input = transcript

            st.success("Captured!")
            st.write(transcript)

    # -----------------------------
    # PROCESS TASKS
    # -----------------------------
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Process Tasks"):

        if user_input:
            extracted_tasks = organize_task(client, user_input)
            st.session_state.pending_tasks.extend(extracted_tasks)
            st.success("Tasks processed successfully!")
        else:
            st.warning("Please enter or record your tasks first.")

    # -----------------------------
    # SHOW CAPTURED TASKS
    # -----------------------------
    if st.session_state.pending_tasks:

        st.markdown("## 📌 Captured Tasks")

        for i, task in enumerate(st.session_state.pending_tasks):

            if f"edit_{i}" not in st.session_state:
                st.session_state[f"edit_{i}"] = False

            # -------------------------
            # VALIDATION
            # -------------------------
            missing_name = not task.get("task_name")
            missing_type = not task.get("type")
            missing_due = not task.get("due")

            def is_duplicate_task(task):
                for existing in st.session_state.tasks:
                    if (
                        existing["task_name"].strip().lower() == task.get("task_name", "").strip().lower()
                        and existing.get("due") == task.get("due")
                    ):
                        return True
                return False

            is_duplicate = is_duplicate_task(task)

            # -------------------------
            # EDIT MODE
            # -------------------------
            if st.session_state[f"edit_{i}"]:

                task_name = st.text_input("Task", value=task["task_name"], key=f"name_{i}")
                task_type = st.text_input("Type", value=task["type"], key=f"type_{i}")

                try:
                    default_date = datetime.datetime.strptime(task["due"], "%Y-%m-%d").date()
                except:
                    default_date = datetime.date.today()

                due_date = st.date_input("Due", value=default_date, key=f"due_{i}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Save", key=f"save_{i}"):
                        task["task_name"] = task_name.strip()
                        task["type"] = task_type.strip()
                        task["due"] = due_date.strftime("%Y-%m-%d")
                        st.session_state[f"edit_{i}"] = False
                        st.rerun()

                with col2:
                    if not (missing_name or missing_type or missing_due or is_duplicate):
                        if st.button("Add Task", key=f"add_{i}"):
                            if is_duplicate_task(task):
                                st.error("Task already exists!")
                            else:
                                st.session_state.tasks.append(task)
                                st.session_state.pending_tasks.pop(i)
                                st.success("Task added successfully!")
                                st.rerun()

            # -------------------------
            # NORMAL VIEW
            # -------------------------
            else:

                st.markdown(f"""
<div class="task-card">
<p><b>Task:</b> {"🔴 Missing task name" if missing_name else task['task_name']}</p>
<p><b>Type:</b> {"🔴 Missing type" if missing_type else task['type']}</p>
<p><b>Due:</b> {"🔴 Missing due date" if missing_due else task['due']}</p>
</div>
""", unsafe_allow_html=True)

                if is_duplicate:
                    st.error("This task already exists")
                elif missing_name or missing_type or missing_due:
                    st.warning("Please complete missing fields")

                # -------------------------
                # BUTTONS
                # -------------------------
                if is_duplicate:
                    # 👉 Only case where Delete appears
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Edit", key=f"editbtn_{i}"):
                            st.session_state[f"edit_{i}"] = True

                    with col2:
                        if st.button("Delete", key=f"deletebtn_{i}"):
                            st.session_state.pending_tasks.pop(i)
                            st.success("Duplicate removed")
                            st.rerun()

                else:
                    # 👉 Normal case (no delete)
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Edit", key=f"editbtn_{i}"):
                            st.session_state[f"edit_{i}"] = True

                    with col2:
                        if not (missing_name or missing_type or missing_due):
                            if st.button("Add Task", key=f"addbtn_{i}"):
                                if is_duplicate_task(task):
                                    st.error("Task already exists!")
                                else:
                                    st.session_state.tasks.append(task)
                                    st.session_state.pending_tasks.pop(i)
                                    st.success("Task added successfully!")
                                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # FINAL TASKS
    # -----------------------------
    if st.session_state.tasks:

        st.markdown("## 📥 Added Tasks")

        for task in st.session_state.tasks:
            st.markdown(f"""
• {task['task_name']} ({task['type']}) – {task['due']}
""")
