import streamlit as st
from datetime import date, datetime, timedelta
from modules import database as db
import time
import serial
import serial.tools.list_ports

# Arduino configuration
ARDUINO_PORT = 'COM9'
BAUD_RATE = 9600

# Calibration table for non-linear gauge (from CPU meter)
CALIBRATION_TABLE = [
    (0, 180),
    (5, 180),
    (6, 179),
    (10, 175),
    (13, 170),
    (20, 160),
    (30, 135),
    (50, 90),
    (70, 45),
    (73, 40),
    (80, 30),
    (85, 20),
    (100, 0)
]

# Initialize Arduino connection state in session
if 'arduino_connected' not in st.session_state:
    st.session_state.arduino_connected = False
    st.session_state.arduino_port = ARDUINO_PORT

def get_calibrated_angle(percentage):
    """Convert percentage to calibrated servo angle using piecewise linear interpolation"""
    percentage = max(0, min(100, percentage))
    
    for i in range(len(CALIBRATION_TABLE) - 1):
        p1, a1 = CALIBRATION_TABLE[i]
        p2, a2 = CALIBRATION_TABLE[i + 1]
        
        if p1 <= percentage <= p2:
            if p2 == p1:
                return int(a1)
            ratio = (percentage - p1) / (p2 - p1)
            angle = a1 + ratio * (a2 - a1)
            return int(angle)
    
    return 90

def test_arduino_connection(port=ARDUINO_PORT):
    """Test if Arduino is connected and working"""
    try:
        arduino = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)
        
        # Send test angle (90 degrees = middle position)
        arduino.write(bytes([90]))
        time.sleep(0.5)
        
        arduino.close()
        return True, "✅ Arduino Connected! Servo responded."
    except serial.SerialException as e:
        return False, f"❌ Connection failed: {str(e)}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def send_to_arduino(percentage, port=ARDUINO_PORT):
    """Send angle to Arduino servo"""
    try:
        arduino = serial.Serial(port, BAUD_RATE, timeout=1)
        angle = get_calibrated_angle(percentage)
        arduino.write(bytes([angle]))
        arduino.close()
        return True
    except:
        return False

def list_available_ports():
    """List all available COM ports"""
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]
    return port_list if port_list else ["COM3", "COM4", "COM5", "COM9"]

# Timer presets
PRESETS = {
    "🍅 Pomodoro (25m)": 25,
    "⚡ Short Focus (15m)": 15,
    "🚀 Deep Work (50m)": 50,
    "🎯 Custom": 0,
}


def render():
    st.header("⏱️ Focus Timer")
    
    # Arduino Connection Status & Testing
    st.write("**Arduino Servo Connection**")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_port = st.selectbox(
            "Select COM Port",
            list_available_ports(),
            index=0 if ARDUINO_PORT not in list_available_ports() else list_available_ports().index(ARDUINO_PORT),
            key="arduino_port_selector"
        )
        st.session_state.arduino_port = selected_port
    
    with col2:
        if st.button("🔌 Test Connection", use_container_width=True):
            success, message = test_arduino_connection(selected_port)
            if success:
                st.session_state.arduino_connected = True
                st.success(message)
            else:
                st.session_state.arduino_connected = False
                st.error(message)
    
    with col3:
        if st.session_state.arduino_connected:
            st.success("✅ Connected")
        else:
            st.warning("⚠️ Not Tested")
    
    st.divider()
    
    today = date.today().isoformat()
    
    # Initialize session state for timer
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
        st.session_state.timer_start_time = None
        st.session_state.timer_duration = 25
        st.session_state.timer_paused = False
        st.session_state.timer_pause_time = 0
    
    # Display stats
    stats = db.get_timer_stats(today)
    focus_streak = db.get_focus_streak()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏰ Today's Focus", f"{stats['total_minutes']}m", delta=f"{stats['total_sessions']} sessions")
    with col2:
        completion_rate = int((stats['completed_sessions'] / stats['total_sessions'] * 100)) if stats['total_sessions'] > 0 else 0
        st.metric("✅ Completed", f"{completion_rate}%", delta=f"{stats['completed_sessions']}/{stats['total_sessions']}")
    with col3:
        st.metric("🔥 Focus Streak", f"{focus_streak} days", delta="Keep it up!" if focus_streak > 0 else "Start today!")
    with col4:
        avg_focus = int(stats['total_minutes'] / stats['total_sessions']) if stats['total_sessions'] > 0 else 0
        st.metric("📊 Avg Session", f"{avg_focus}m", delta="per session")
    
    st.write("---")
    
    # Timer Control Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🎯 Start a Focus Session")
        
        # Preset selection
        selected_preset = st.radio(
            "Choose preset:",
            list(PRESETS.keys()),
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Custom duration input
        if "Custom" in selected_preset:
            duration = st.slider(
                "Duration (minutes)",
                min_value=1,
                max_value=180,
                value=st.session_state.timer_duration,
                step=1
            )
            st.session_state.timer_duration = duration
        else:
            duration = PRESETS[selected_preset]
            st.session_state.timer_duration = duration
        
        # Subject selection (for academics tracking)
        subject = st.selectbox(
            "What are you focusing on?",
            ["General", "Maths", "Mech", "Chem", "Python", "Reading", "Project", "Other"]
        )
    
    with col1:
        st.write("")  # spacing
        
        # Timer display
        if st.session_state.timer_running:
            elapsed = time.time() - st.session_state.timer_start_time
            if st.session_state.timer_paused:
                elapsed = st.session_state.timer_pause_time
            
            remaining = max(0, st.session_state.timer_duration * 60 - elapsed)
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            
            # Calculate percentage for servo (100% at start, 0% at end)
            percentage = (remaining / (st.session_state.timer_duration * 60)) * 100
            
            # Send to Arduino if connected
            if st.session_state.arduino_connected:
                send_to_arduino(percentage, st.session_state.arduino_port)
            
            # Large timer display
            st.markdown(f"""
            <div style="text-align: center; padding: 40px; background: rgba(10, 132, 255, 0.1); border-radius: 16px; border: 2px solid rgba(10, 132, 255, 0.3);">
                <div style="font-size: 4.5em; font-weight: 300; color: #0a84ff; letter-spacing: -2px; font-variant-numeric: tabular-nums;">
                    {mins:02d}:{secs:02d}
                </div>
                <div style="font-size: 1.2em; color: #86868b; margin-top: 10px;">
                    {subject} • {st.session_state.timer_duration}m Focus
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Control buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("⏸️ Pause" if not st.session_state.timer_paused else "▶️ Resume", use_container_width=True):
                    if st.session_state.timer_paused:
                        # Resume
                        st.session_state.timer_start_time = time.time() - st.session_state.timer_pause_time
                        st.session_state.timer_paused = False
                    else:
                        # Pause
                        st.session_state.timer_paused = True
                        st.session_state.timer_pause_time = time.time() - st.session_state.timer_start_time
                    st.rerun()
            
            with col_btn2:
                if st.button("⏹️ Stop", use_container_width=True):
                    st.session_state.timer_running = False
                    st.rerun()
            
            with col_btn3:
                if st.button("✅ Finish", use_container_width=True):
                    # Move servo to 0% (timer complete) if connected
                    if st.session_state.arduino_connected:
                        send_to_arduino(0, st.session_state.arduino_port)
                    # Save completed session
                    start_time = datetime.fromtimestamp(st.session_state.timer_start_time).strftime("%H:%M")
                    db.add_timer_session(today, start_time, st.session_state.timer_duration, subject, completed=1)
                    st.session_state.timer_running = False
                    st.success(f"🎉 Great! {st.session_state.timer_duration}m focus session completed!")
                    time.sleep(2)
                    st.rerun()
            
            # Auto-rerun for timer updates
            time.sleep(0.1)
            st.rerun()
        
        else:
            # Start button
            if sif not st.session_state.arduino_connected:
                    st.warning("⚠️ Arduino not connected. Test connection first!")
                else:
                    # Move servo to 100% (start position) if connected
                    send_to_arduino(100, st.session_state.arduino_port)
                    st.session_state.timer_running = True
                    st.session_state.timer_start_time = time.time()
                    st.session_state.timer_paused = False
                    st.session_state.timer_pause_time = 0
                    st.session_state.timer_pause_time = 0
                st.rerun()
    
    st.write("---")
    
    # Session history
    st.subheader("📜 Today's Sessions")
    sessions = db.get_timer_sessions(today)
    
    if sessions:
        for session in sessions:
            status = "✅ Completed" if session["completed"] else "⏸️ Incomplete"
            st.caption(f"{status} • {session['start_time']} • {session['duration_minutes']}m • {session['subject']}")
    else:
        st.info("No focus sessions yet. Start one above! 🚀")
    
    # Motivational message
    if stats['total_minutes'] >= 180:  # 3 hours
        st.success("🌟 Amazing focus session today! You're crushing your goals!")
    elif stats['total_minutes'] >= 120:  # 2 hours
        st.info("💪 Great work! Keep the momentum going!")
    elif stats['total_minutes'] >= 60:  # 1 hour
        st.info("⚡ Good start! More sessions to go!")
