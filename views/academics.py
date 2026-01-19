import streamlit as st
from datetime import date, datetime
from modules import database as db

def check_and_send_reminders():
    """Check time and send task reminders throughout the day"""
    current_hour = datetime.now().hour
    
    # Reminder schedule
    reminders = {
        8: ("🌅 Morning Reminder", "Time to plan your day! Enter all your tasks for today."),
        14: ("☀️ Afternoon Check-in", "You're halfway through the day! Complete 2-3 tasks now."),
        18: ("🌆 Evening Reminder", "Finish another task before dinner. You're doing great!"),
        21: ("🌙 Night Review", "How many tasks did you complete today? Time to review your progress!")
    }
    
    if current_hour in reminders:
        title, message = reminders[current_hour]
        
        # Show in-app notification
        st.toast(f"{title}: {message}", icon="🔔")
        
        # Browser notification
        st.markdown(f"""
        <script>
            if (Notification.permission === "granted") {{
                var notification = new Notification("{title}", {{
                    body: "{message}",
                    icon: "📚",
                    tag: "task-reminder-{current_hour}"
                }});
                setTimeout(() => notification.close(), 15000);
            }}
        </script>
        """, unsafe_allow_html=True)

# Hardcoded exam schedule
SCHEDULE = {
    "2026-01-02": [
        "Mech: Memorize TIG vs MIG",
        "Maths: Maclaurin Series & Calculator Mode",
        "Python: Class Syntax",
    ],
    "2026-01-03": [
        "Maths: Radius of Curvature (Handbook Check)",
        "Mech: Draw Welding Diagrams",
        "Mech: Flashcard Quiz",
    ],
    "2026-01-04": [
        "Maths: Jacobians & Lagrange",
        "Chem: CNTs & Graphene Props",
        "Chem: Piezoelectric Sensor Diagram",
    ],
    "2026-01-05": [
        "Mech: Open/Closed Loop Block Diagrams",
        "Mech: Robot Configurations",
        "Maths: Review Taylor/Maclaurin",
    ],
    "2026-01-06": [
        "Chem: Wiener & Zagreb Indices",
        "Chem: Topological Matrix",
        "Python: File Handling Code",
    ],
    "2026-01-07": [
        "Maths: Change of Order (Integration)",
        "Maths: Verify with Calculator",
        "Python: Numpy Basics",
    ],
    "2026-01-08": [
        "Mech: IC Engine Formula (Eff=Out/In)",
        "Mech: BHP/IHP Numericals",
        "Mech: Review Stress-Strain",
    ],
    "2026-01-09": [
        "Python: Pandas (read_csv, head)",
        "Python: Matplotlib Basics",
        "Maths: Verify Eigenvalues (Calc)",
    ],
    "2026-01-10": [
        "Chem: Review Polymers/Memory",
        "Maths: Stats Regression Mode (Calc)",
        "Buffer: Review Weak Spots",
    ],
    "2026-01-11": [
        "Mech: Full Diagram Mock",
        "Maths: Full PYQ Mock (2hrs)",
        "Relax: Movie/Game",
    ],
    "2026-01-12": [
        "Python: Write Class/Pandas by hand",
        "Chem: Write Unit 4/5 Answers",
        "Mech: Re-memorize TIG/MIG",
    ],
    "2026-01-13": ["Focus on First Exam Subject"],
    "2026-01-14": ["Focus on First Exam Subject"],
    "2026-01-15": ["Focus on First Exam Subject"],
    "2026-01-16": ["Review Day / Buffer"],
}


def render():
    st.header(" Academics ? Exam Plan")
    
    # Check and send reminders
    check_and_send_reminders()
    
    # Calculate overall progress
    total_days = 15
    all_completed = 0
    all_total = 0
    for d in SCHEDULE.keys():
        tasks = db.get_tasks(d, category="Academics")
        if tasks:
            all_total += len(tasks)
            all_completed += sum(1 for t in tasks if t["status"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        completion_pct = int((all_completed / all_total * 100)) if all_total > 0 else 0
        st.metric(" Overall Progress", f"{completion_pct}%", delta=f"{all_completed}/{all_total} tasks")
    
    with col2:
        if completion_pct >= 80:
            st.metric(" Status", "Excellent!", delta="Keep it up!")
        elif completion_pct >= 50:
            st.metric(" Status", "On Track", delta="Push harder!")
        else:
            st.metric(" Status", "Need Focus", delta="Let's do this!")
    
    with col3:
        total_tasks = sum(len(SCHEDULE.get(d, [])) for d in SCHEDULE.keys())
        st.metric(" Total Tasks", total_tasks, delta="to track")
    
    st.write("---")
    st.write("Track daily exam prep tasks. Checkboxes persist instantly.")

    today = date.today()
    selected = st.date_input(
        "Select date",
        value=min(today, date(2026, 1, 16)),
        min_value=date(2026, 1, 2),
        max_value=date(2026, 2, 28),
    )
    date_str = selected.isoformat()

    # Quick add
    with st.expander(" Quick Add Task"):
        new_task = st.text_input("Task name")
        if st.button("Add", key="add_custom_task") and new_task.strip():
            db.add_custom_task(date_str, new_task.strip(), category="Academics")
            st.success(" Task added")
            st.rerun()

    # Ensure hardcoded tasks exist
    for task in SCHEDULE.get(date_str, []):
        db.upsert_task(date_str, task, "Academics", status=0)

    tasks = db.get_tasks(date_str, category="Academics")
    if not tasks:
        st.info("No tasks for this date.")
        return

    completed = 0
    total = len(tasks)
    for idx, t in enumerate(tasks):
        key = f"acad_{date_str}_{idx}"
        checked = bool(t["status"])

        def _on_change(ds=date_str, tn=t["task_name"], cat=t["category"], k=key):
            db.set_task_status(ds, tn, cat, bool(st.session_state.get(k, False)))

        st.checkbox(t["task_name"], value=checked, key=key, on_change=_on_change)
        if st.session_state.get(key, checked):
            completed += 1

    # Visual progress
    progress_pct = completed / total if total else 0
    st.progress(progress_pct)
    
    if progress_pct == 1.0:
        st.success(f" Perfect! All {total} tasks completed today!")
    elif progress_pct >= 0.7:
        st.info(f" {completed}/{total} completed ? Almost there!")
    else:
        st.caption(f" {completed}/{total} completed")