import streamlit as st
from datetime import date, timedelta
from modules import database as db

HABITS = [
    "Peanut Butter",
    "Venusia Max",
    "Bisleri Rinse",
    "Night Cream",
    "Workout",
]


def compute_streak(habit: str) -> int:
    # Walk back in time until a miss
    today = date.today()
    streak = 0
    day = today
    while True:
        rows = db.get_habits(day.isoformat())
        status = None
        for r in rows:
            if r["habit"] == habit:
                status = bool(r["status"])
                break
        if status:
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    return streak


def render():
    st.header("Health - Daily Protocol")
    
    # Motivational header with overall completion
    today = date.today().isoformat()
    
    # Ensure habits exist
    for h in HABITS:
        db.upsert_habit(today, h, status=0)
    
    current_rows = db.get_habits(today)
    completed_today = sum(1 for r in current_rows if r["status"])
    total_habits = len(HABITS)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        completion_pct = int((completed_today / total_habits * 100)) if total_habits > 0 else 0
        st.metric(" Today's Progress", f"{completed_today}/{total_habits}", delta=f"{completion_pct}%")
    
    with col2:
        max_streak = max([compute_streak(h) for h in HABITS])
        st.metric(" Best Streak", f"{max_streak} days", delta="Keep Going!")
    
    with col3:
        if completed_today == total_habits:
            st.metric(" Status", "Perfect Day!", delta="100%")
        elif completed_today >= total_habits * 0.6:
            st.metric(" Status", "On Track", delta="Good!")
        else:
            st.metric(" Status", "Let's Go!", delta="Do it!")
    
    st.write("---")
    st.write("Stay consistent. Track your daily checklist and streaks.")

    # Checkboxes with visual feedback
    for idx, h in enumerate(HABITS):
        key = f"habit_{today}_{idx}"
        current_rows_h = [r for r in current_rows if r["habit"] == h]
        checked = bool(current_rows_h[0]["status"]) if current_rows_h else False

        def _on_change(ds=today, habit=h, k=key):
            db.set_habit_status(ds, habit, bool(st.session_state.get(k, False)))

        # Get streak for this habit
        streak = compute_streak(h)
        
        # Add emoji based on streak
        if streak >= 30:
            icon = ""
        elif streak >= 14:
            icon = ""
        elif streak >= 7:
            icon = ""
        else:
            icon = ""
        
        st.checkbox(f"{icon} {h} - {streak} day streak", value=checked, key=key, on_change=_on_change)

    # Progress bar
    st.write("---")
    st.subheader(" Today's Completion")
    st.progress(completed_today / total_habits if total_habits else 0)
    
    if completed_today == total_habits:
        st.success(" All habits done today! You're unstoppable!")
    elif completed_today > 0:
        st.info(f" {total_habits - completed_today} left to complete!")
    
    # Streak visualization
    st.write("---")
    st.subheader(" Streak Leaderboard")
    streak_data = [(h, compute_streak(h)) for h in HABITS]
    streak_data.sort(key=lambda x: x[1], reverse=True)
    
    for habit, streak in streak_data:
        if streak >= 30:
            badge = " Master"
        elif streak >= 14:
            badge = " On Fire"
        elif streak >= 7:
            badge = " Building"
        else:
            badge = " Starting"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{habit}**")
        with col2:
            st.write(f"{badge}  {streak}d")