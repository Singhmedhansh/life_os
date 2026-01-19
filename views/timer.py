import streamlit as st
from datetime import date, datetime, timedelta
from modules import database as db
import time

# Optional serial import (for Arduino support)
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

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
    if not SERIAL_AVAILABLE:
        return False, "❌ pyserial not installed. Arduino support unavailable on Render."
    
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
    if not SERIAL_AVAILABLE:
        return False
    
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
    if not SERIAL_AVAILABLE:
        return ["COM3", "COM4", "COM5", "COM9"]
    
    try:
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        return port_list if port_list else ["COM3", "COM4", "COM5", "COM9"]
    except:
        return ["COM3", "COM4", "COM5", "COM9"]

def create_pip_timer(mins, secs, subject, duration):
    """Create Picture-in-Picture timer HTML"""
    return f"""
    <style>
        .pip-timer {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            cursor: move;
            user-select: none;
        }}
        .pip-time {{
            font-size: 3em;
            font-weight: 300;
            letter-spacing: -1px;
            margin: 0;
            text-align: center;
        }}
        .pip-subject {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 8px;
            text-align: center;
        }}
        .pip-close {{
            position: absolute;
            top: 8px;
            right: 12px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 14px;
        }}
        .pip-close:hover {{
            background: rgba(255,255,255,0.3);
        }}
    </style>
    <div class="pip-timer" id="pipTimer">
        <button class="pip-close" onclick="document.getElementById('pipTimer').style.display='none'">✕</button>
        <div class="pip-time">{mins:02d}:{secs:02d}</div>
        <div class="pip-subject">{subject} • {duration}m</div>
    </div>
    <script>
        const timer = document.getElementById('pipTimer');
        let isDragging = false;
        let currentX, currentY, initialX, initialY;
        
        timer.addEventListener('mousedown', function(e) {{
            if (e.target.className === 'pip-close') return;
            isDragging = true;
            initialX = e.clientX - timer.offsetLeft;
            initialY = e.clientY - timer.offsetTop;
        }});
        
        document.addEventListener('mousemove', function(e) {{
            if (isDragging) {{
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                timer.style.left = currentX + 'px';
                timer.style.top = currentY + 'px';
                timer.style.right = 'auto';
            }}
        }});
        
        document.addEventListener('mouseup', function() {{
            isDragging = false;
        }});
    </script>
    """
        return ["COM3", "COM4", "COM5", "COM9"]

# Timer presets
PRESETS = {
    "🍅 Pomodoro (25m)": 25,
    "⚡ Short Focus (15m)": 15,
    "🚀 Deep Work (50m)": 50,
    "🎯 Custom": 0,
}


def render():
    st.header("⏱️ Focus Timer")
    
    # Request notification permission on load
    st.markdown("""
    <script>
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    </script>
    """, unsafe_allow_html=True)
    
    # Initialize focus mode in session state
    if 'focus_mode' not in st.session_state:
        st.session_state.focus_mode = "Focus Mode"
    
    # Focus Mode Selection
    st.write("**Select Focus Mode**")
    focus_mode = st.radio(
        "",
        ["🧠 Focus Mode (No Rev Meter)", "🎯 Focus with Rev Meter"],
        horizontal=True,
        label_visibility="collapsed",
        key="focus_mode_radio"
    )
    st.session_state.focus_mode = focus_mode
    
    # Arduino Connection Status & Testing (only show if using Rev Meter mode)
    if "Focus with Rev Meter" in focus_mode:
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
    else:
        st.info("💡 Focus Mode - Timer only, no Arduino needed!")
    
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
            
            # Check if timer has completed
            if remaining == 0 and not st.session_state.get('timer_completed', False):
                st.session_state.timer_completed = True
                st.session_state.timer_running = False
                
                if "Focus with Rev Meter" in st.session_state.focus_mode and st.session_state.arduino_connected:
                    send_to_arduino(0, st.session_state.arduino_port)
                
                start_time = datetime.fromtimestamp(st.session_state.timer_start_time).strftime("%H:%M")
                db.add_timer_session(date.today(), start_time, st.session_state.timer_duration, subject, completed=1)
                
                st.toast("⏰ Focus Session Complete! Great work!", icon="🎉")
                st.markdown(f"""
                <script>
                    if (Notification.permission === "granted") {{
                        var notification = new Notification("🎯 Focus Session Complete!", {{
                            body: "Amazing! Your {subject} session is done. Time for a break!",
                            requireInteraction: true,
                            tag: "timer-complete"
                        }});
                        setTimeout(() => notification.close(), 10000);
                    }}
                </script>
                """, unsafe_allow_html=True)
                
                st.success(f"🎉 Awesome! {st.session_state.timer_duration}m {subject} session completed!")
                st.balloons()
            
            # Calculate percentage for servo (100% at start, 0% at end)
            percentage = (remaining / (st.session_state.timer_duration * 60)) * 100
            
            # Send to Arduino if using Rev Meter mode and connected
            if "Focus with Rev Meter" in st.session_state.focus_mode and st.session_state.arduino_connected:
                send_to_arduino(percentage, st.session_state.arduino_port)
            
            # Picture-in-Picture floating timer
            pip_html = create_pip_timer(mins, secs, subject, st.session_state.timer_duration)
            st.markdown(pip_html, unsafe_allow_html=True)
            
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
                    # Move servo to 0% (timer complete) if using Rev Meter
                    if "Focus with Rev Meter" in st.session_state.focus_mode and st.session_state.arduino_connected:
                        send_to_arduino(0, st.session_state.arduino_port)
                    # Save completed session
                    start_time = datetime.fromtimestamp(st.session_state.timer_start_time).strftime("%H:%M")
                    db.add_timer_session(today, start_time, st.session_state.timer_duration, subject, completed=1)
                    st.session_state.timer_running = False
                    st.success(f"🎉 Great! {st.session_state.timer_duration}m focus session completed!")
                    time.sleep(2)
                    st.rerun()
            
            # Auto-rerun for timer updates (only if still running)
            if st.session_state.timer_running and not st.session_state.get('timer_completed', False):
                time.sleep(0.1)
                st.rerun()
        
        else:
            # Start button
            if st.button("▶️ Start Focus Session", use_container_width=True, key="start_timer"):
                # Check if Arduino is required and connected
                if "Focus with Rev Meter" in st.session_state.focus_mode and not st.session_state.arduino_connected:
                    st.warning("⚠️ Arduino not connected. Test connection first!")
                else:
                    # Move servo to 100% if using Rev Meter mode
                    if "Focus with Rev Meter" in st.session_state.focus_mode and st.session_state.arduino_connected:
                        send_to_arduino(100, st.session_state.arduino_port)
                    
                    st.session_state.timer_running = True
                    st.session_state.timer_start_time = time.time()
                    st.session_state.timer_paused = False
                    st.session_state.timer_pause_time = 0
                    st.session_state.timer_completed = False  # Reset completion flag
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
