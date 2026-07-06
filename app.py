import streamlit as st
import requests
import json
import os
import re
import pandas as pd
from gtts import gTTS
from database import init_db, save_lesson, get_all_offline_lessons

init_db()

st.set_page_config(page_title="EduPulse Equalizer Pro", page_icon="📚", layout="wide")

if "users_db" not in st.session_state:
    st.session_state.users_db = {"student": "password123"}
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "new_users_list" not in st.session_state:
    st.session_state.new_users_list = []

st.markdown("""
    <style>
    .stApp {
        background-color: #FDFBF7;
    }
    h1, h2, h3, h4 {
        color: #0A3C82 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .main-title {
        font-size: 42px !important;
        font-weight: bold;
        color: #0B4CA3;
        margin-bottom: 5px;
    }
    .badge-container {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
    }
    .status-badge {
        flex: 1;
        padding: 15px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .badge-green { background: linear-gradient(135deg, #28A745, #1E7E34); }
    .badge-orange { background: linear-gradient(135deg, #FD7E14, #D35400); }
    .badge-blue { background: linear-gradient(135deg, #007BFF, #0056B3); }
    .section-header {
        border-bottom: 2px solid #E9ECEF;
        padding-bottom: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        color: #1967D2;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #E2E8F0 !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }
    input, select, div[role="listbox"] {
        background-color: transparent !important;
        color: #0A3C82 !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        background-color: #5465FF !important;
        border-color: #3B42C4 !important;
    }
    div[data-baseweb="input"]:focus-within input {
        color: #FFFFFF !important;
    }
    
    div.stButton > button {
        background-color: #0B4CA3 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        background: linear-gradient(135deg, #28A745, #FFD700) !important;
        color: #0A3C82 !important;
        box-shadow: 0px 4px 10px rgba(40, 167, 69, 0.4) !important;
    }

    div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] span {
        color: #0A3C82 !important;
    }
    label[data-baseweb="radio"] div {
        color: #0A3C82 !important;
        font-weight: 500 !important;
    }
    
    .welcome-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .profile-card {
        background-color: #0B4CA3 !important;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0px 4px 8px rgba(11, 76, 163, 0.15);
        margin-bottom: 18px;
        border-left: 6px solid #28A745;
    }
    .profile-card p, .profile-card span, .profile-card div, .profile-card b {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

def generate_audio(text, lang_code="hi"):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_path = "temp_lesson.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Audio Generation Failed: {str(e)}")
        return None

if not st.session_state.user_authenticated:
    header_col1, header_col2 = st.columns([1, 4])
    with header_col1:
        st.markdown("<h1 style='font-size: 72px; margin: 0; padding: 0;'>🔰</h1>", unsafe_allow_html=True)
    with header_col2:
        st.markdown("<h1 class='main-title'>EduPulse-Equalizer Pro</h1>", unsafe_allow_html=True)
        
    st.write("---")
    
    auth_mode = st.radio("Access Portal Mode:", ["Login to Account", "Create New Account"], horizontal=True)
    
    st.markdown("<div class='welcome-card'>", unsafe_allow_html=True)
    if auth_mode == "Login to Account":
        st.subheader("🔑 Secure Identity Gateway")
        username = st.text_input("Username / Email ID:", key="login_username")
        password = st.text_input("Security Access Password:", type="password", key="login_password")
        if st.button("Enter Dashboard", use_container_width=True):
            if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                st.session_state.user_authenticated = True
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("Invalid credentials entry context. Please ensure you signed up first.")
    else:
        st.subheader("📝 Register New Student Profile")
        new_username = st.text_input("Create Registration Username:", key="signup_username")
        new_password = st.text_input("Choose Strong Password:", type="password", key="signup_password")
        if st.button("Confirm Profile Generation", use_container_width=True):
            if not new_username or not new_password:
                st.error("Data fields validation constraint error. Fields cannot be empty.")
            elif new_username in st.session_state.users_db:
                st.warning("Username string already structuralized. Choose a different one.")
            else:
                st.session_state.users_db[new_username] = new_password
                st.session_state.new_users_list.append(new_username)
                st.session_state.user_authenticated = True
                st.session_state.current_user = new_username
                st.success("Registration success! Logging into portal dashboard...")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    header_col1, header_col2 = st.columns([1, 4])
    with header_col1:
        st.markdown("<h1 style='font-size: 72px; margin: 0; padding: 0;'>🔰</h1>", unsafe_allow_html=True)
    with header_col2:
        st.markdown("<h1 class='main-title'>EduPulse-Equalizer Pro</h1>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_logout = st.columns(6)
    with nav_col1:
        if st.button("🏠 Home", use_container_width=True): st.session_state.current_page = "Home"
    with nav_col2:
        if st.button("📚 Learn", use_container_width=True): st.session_state.current_page = "Learn"
    with nav_col3:
        if st.button("📝 Quiz", use_container_width=True): st.session_state.current_page = "Quiz"
    with nav_col4:
        if st.button("📈 Progress", use_container_width=True): st.session_state.current_page = "Progress"
    with nav_col5:
        if st.button("👤 Profile", use_container_width=True): st.session_state.current_page = "Profile"
    with nav_logout:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
            st.rerun()

    st.write("---")

    is_new_user = st.session_state.current_user in st.session_state.new_users_list
    saved_lessons = get_all_offline_lessons()

    if st.session_state.current_page == "Home":
        if is_new_user:
            greeting_header = f"👋 Welcome to EduPulse Equalizer Pro, {st.session_state.current_user}!"
            greeting_body = "We are incredibly excited to welcome you to the platform for the first time! Get started below by exploring custom localized curriculum pathways tailormade for you."
        else:
            greeting_header = f"👋 Welcome back, {st.session_state.current_user}!"
            greeting_body = "EduPulse Equalizer Pro adapts complex educational curricula dynamically into regional contexts and localized visual stories seamlessly."

        st.markdown(f"""
            <div class="welcome-card">
                <h3 style="margin-top:0px; color:#0B4CA3;">{greeting_header}</h3>
                <p style="color:#555555; margin-bottom:15px;">{greeting_body}</p>
            </div>
        """, unsafe_allow_html=True)
        
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            streak_val = "0 Days" if is_new_user else "5 Days"
            st.metric(label="🔥 Daily Learning Streak", value=streak_val)
        with stat_col2:
            st.write("**📊 Overall Progress Percentage**")
            progress_val = 0.0 if is_new_user else 0.74
            st.progress(progress_val)
            caption_text = "0% of target modules completed" if is_new_user else "74% of target modules completed"
            st.caption(caption_text)
            
        st.write("")
        if st.button("🚀 Start Learning", key="start_learning_cta", use_container_width=True):
            st.session_state.current_page = "Learn"
            st.rerun()

    elif st.session_state.current_page == "Learn":
        st.sidebar.markdown("### 📡 System Controls")
        network_status = st.sidebar.radio("Network Simulation Mode:", ["Online (Connect to n8n AI Workflow)", "Offline Mode (Zero Internet)"])
        st.sidebar.write("---")

        # Secured webhook injection ready for deployment config
        N8N_WEBHOOK_URL = st.secrets.get("N8N_CHAT_WEBHOOK", "YOUR_N8N_PRODUCTION_WEBHOOK_URL")

        if network_status == "Online (Connect to n8n AI Workflow)":
            st.markdown("""
                <div class='badge-container'>
                    <div class='status-badge badge-green'>✓ Connected to n8n Cloud Orchestrator<br><span style='font-size:11px;font-weight:normal;'>System Online</span></div>
                    <div class='status-badge badge-orange'>⚡ Autonomous Sync Enabled<br><span style='font-size:11px;font-weight:normal;'>Data Cached Securely Offline</span></div>
                    <div class='status-badge badge-blue'>🌐 Multi-Dialect Support<br><span style='font-size:11px;font-weight:normal;'>Tailored Content for Regional Dialects</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h2 class='section-header'>Generate Contextual Curriculum</h2>", unsafe_allow_html=True)
            st.caption("Build Lessons Tailored to Your Students' Needs")
            
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Core Educational Topic:", placeholder="e.g., Water, Photosynthesis, Fractions")
                region = st.text_input("Village/Dialect Context:", placeholder="e.g., Rural Bihar (Ara), Konkan Maharashtra")
                edu_level = st.selectbox("Educational Level:", ["Primary School", "Middle School", "High School"])
                
            with col2:
                language = st.selectbox("Target Regional Language:", ["Hindi", "Bhojpuri", "Marathi", "Tamil", "Bengali", "Gujarati", "English"])
                school_setting = st.selectbox("School Settings / Profile:", ["Government School", "Zilla Parishad", "Rural Community Center", "Private School"])
            
            if st.button("🚀 Generate Curriculum", use_container_width=True):
                if topic and region:
                    with st.spinner("Generating curriculum parameters... Please wait."):
                        try:
                            payload = {
                                "topic": topic,
                                "language": language,
                                "region": region,
                                "educational_level": edu_level,
                                "school_setting": school_setting
                            }
                            
                            response = requests.post(N8N_WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})
                            
                            if response.status_code == 200:
                                # Clears double spacing or custom breaks layout errors completely
                                clean_data = response.text.replace("\n\n", " ").replace("\\n", " ")
                                st.session_state.raw_text = clean_data
                                st.session_state.quiz_submitted = False
                                st.session_state.current_region = region
                                st.session_state.current_language = language
                                st.session_state.current_topic = topic
                                if st.session_state.current_user in st.session_state.new_users_list:
                                    st.session_state.new_users_list.remove(st.session_state.current_user)
                            else:
                                st.error(f"Backend Server Error. Status Code: {response.status_code}")
                        except Exception as e:
                            st.error(f"Connection Pipeline Failed: {str(e)}")
                else:
                    st.warning("All core configuration fields are mandatory.")

            if "raw_text" in st.session_state:
                text = st.session_state.raw_text
                
                explanation_match = re.search(r"Explanation:(.*?)(?=Example:|Quiz Question 1|---|$)", text, re.DOTALL)
                example_match = re.search(r"Example:(.*?)(?=Quiz Question 1|---|$)", text, re.DOTALL)
                
                explanation_content = ""
                example_content = ""
                
                if explanation_match:
                    st.markdown("<h3 style='margin-top:20px;'>📚 Explanation</h3>", unsafe_allow_html=True)
                    explanation_content = explanation_match.group(1).strip()
                    st.info(explanation_content)
                if example_match:
                    st.markdown("<h3>💡 Real-Life Localized Example</h3>", unsafe_allow_html=True)
                    example_content = example_match.group(1).strip()
                    st.success(example_content)
                    
                if explanation_content or example_content:
                    st.markdown("#### 🎙️ Listen to the Full Lesson (Audio)")
                    lang_mapping = {"Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn", "Gujarati": "gu", "Bhojpuri": "hi", "English": "en"}
                    target_lang_code = lang_mapping.get(st.session_state.current_language, "hi")
                    
                    full_narration_text = f"{explanation_content} {example_content}"
                    audio_file = generate_audio(full_narration_text, target_lang_code)
                    if audio_file and os.path.exists(audio_file):
                        st.audio(audio_file, format="audio/mp3")
                    
                st.markdown("---")
                st.markdown("<h3>❓ Assessment Module (5 MCQ Challenge)</h3>", unsafe_allow_html=True)
                
                questions_data = []
                for i in range(1, 6):
                    q_text = re.search(f"Quiz Question {i}:(.*?)(?=Options {i}|$)", text, re.DOTALL)
                    opt_text = re.search(f"Options {i}:(.*?)(?=Correct Answer {i}|$)", text, re.DOTALL)
                    ans_text = re.search(f"Correct Answer {i}:(.*?)(?=Quiz Question {i+1}|Score Card|---|$)", text, re.DOTALL)
                    
                    if q_text and opt_text and ans_text:
                        raw_options = opt_text.group(1).strip()
                        options_list = [opt.replace("\\n", "").strip() for opt in re.split(r'[A-C]\)', raw_options) if opt.strip()]
                        if len(options_list) < 3:
                            options_list = [opt.replace("\\n", "").strip() for opt in raw_options.split(',') if opt.strip()]
                    
                        questions_data.append({
                            "question": q_text.group(1).replace("\\n", "").strip(),
                            "options": options_list[:3],
                            "correct": ans_text.group(1).strip().replace(")", "").replace(" ", "")[0]
                        })

                user_answers = {}
                for idx, q in enumerate(questions_data):
                    st.write(f"**Q{idx+1}. {q['question']}**")
                    display_options = []
                    for o_idx, o_val in enumerate(q['options']):
                        prefix = "A" if o_idx == 0 else "B" if o_idx == 1 else "C"
                        display_options.append(f"{prefix}) {o_val}")
                        
                    if display_options:
                        user_answers[idx] = st.radio(f"Select response for Q{idx+1}:", display_options, key=f"online_q_{idx}")
                    st.write("")

                if st.button("Submit Assessment", key="online_submit_btn", use_container_width=True):
                    st.session_state.quiz_submitted = True

                if st.session_state.get("quiz_submitted", False):
                    st.markdown("---")
                    st.header("📊 Result Report Card")
                    score = 0
                    
                    for idx, q in enumerate(questions_data):
                        selected_letter = user_answers[idx].split(")")[0].strip()
                        correct_letter = q['correct']
                        
                        if selected_letter == correct_letter:
                            score += 1
                            st.success(f"✔️ **Q{idx+1}: Correct!**")
                        else:
                            st.error(f"❌ **Q{idx+1}: Incorrect.** \n\n Your selection: {user_answers[idx]} | **Correct Answer: {q['correct']}**")
                            
                    remark_match = re.search(f"Remark {score}:(.*?)(?=Remark|---|$)", text)
                    final_remark = remark_match.group(1).replace("\\n", "").strip() if remark_match else "Well Done!"
                    
                    st.metric(label="Final Score", value=f"{score} / 5")
                    st.info(f"📋 **Evaluation Remark:** {final_remark}")
                    
                    if score == 5:
                        st.balloons()
                        
                    try:
                        flat_options = "||".join([",".join(q['options']) for q in questions_data])
                        flat_questions = "||".join([q['question'] for q in questions_data])
                        flat_answers = "".join([q['correct'] for q in questions_data])
                        
                        save_lesson(
                            st.session_state.current_topic, 
                            st.session_state.current_language, 
                            st.session_state.current_region, 
                            st.session_state.current_topic, 
                            explanation_content + "\n\n" + example_content, 
                            flat_questions, 
                            [flat_options], 
                            flat_answers
                        )
                        st.sidebar.info("💾 Autonomous Sync Completed: Cached in SQLite locally.")
                    except Exception as e:
                        pass
        else:
            st.markdown("<h2 class='section-header'>Offline Local Modules</h2>", unsafe_allow_html=True)
            if not saved_lessons:
                st.info("No offline lessons available. Connect online to sync your framework modules.")
            else:
                for index, row in enumerate(saved_lessons):
                    with st.expander(f"Offline Module: {row[0]}"):
                        st.write(row[4])
                        st.markdown("#### 🎙️ Play Offline Narration")
                        audio_file = generate_audio(row[4], "hi")
                        if audio_file and os.path.exists(audio_file):
                            st.audio(audio_file, format="audio/mp3")

    elif st.session_state.current_page == "Quiz":
        st.markdown("<h2>📝 Historical Practice Hub</h2>", unsafe_allow_html=True)
        if not saved_lessons:
            st.info("No learned topic records cached. Visit the Learn tab to generate your first localized curriculum lesson module!")
        else:
            latest_lesson = saved_lessons[-1]
            st.write(f"### Practice Suite For Most Recent Topic: {latest_lesson[0]}")
            st.write(f"**Target Language Context:** {latest_lesson[1]}")
            st.write("---")
            
            if latest_lesson[5] and "||" in latest_lesson[5]:
                base_questions = latest_lesson[5].split("||")
                extended_questions = []
                
                for i in range(10):
                    base_q = base_questions[i % len(base_questions)].strip()
                    extended_questions.append(f"{base_q} (Variant Pattern {i+1})")
                
                base_options_list = latest_lesson[6][0].split("||") if (len(latest_lesson) > 6 and isinstance(latest_lesson[6], list) and latest_lesson[6]) else ["A,B,C"]
                base_answers = latest_lesson[7] if (len(latest_lesson) > 7 and latest_lesson[7]) else "AAAAA"
                
                quiz_answers = {}
                for q_idx, question in enumerate(extended_questions):
                    st.write(f"**Q{q_idx+1}: {question}**")
                    
                    opt_str = base_options_list[q_idx % len(base_options_list)]
                    opts = [o.strip() for o in opt_str.split(",") if o.strip()]
                    if len(opts) < 3:
                        opts = ["Option Alpha", "Option Beta", "Option Gamma"]
                        
                    display_opts = [f"A) {opts[0]}", f"B) {opts[1]}", f"C) {opts[2]}"]
                    quiz_answers[q_idx] = st.radio(f"Select option for Q{q_idx+1}:", display_opts, key=f"hist_quiz_q_{q_idx}")
                    st.write("")
                    
                if st.button("Submit History Assessment Stack", use_container_width=True):
                    correct_count = 0
                    st.write("### Evaluation Report Tracker")
                    for q_idx in range(10):
                        user_letter = quiz_answers[q_idx].split(")")[0].strip()
                        correct_letter = base_answers[q_idx % len(base_answers)]
                        
                        if user_letter == correct_letter:
                            correct_count += 1
                            st.success(f"✔️ Question {q_idx+1}: Correct")
                        else:
                            st.error(f"❌ Question {q_idx+1}: Incorrect")
                    st.metric(label="Total Aggregated Score", value=f"{correct_count} / 10")
            else:
                st.write("Structural fallback sequence items generating...")

    elif st.session_state.current_page == "Progress":
        st.markdown("<h2>📈 Performance Analytics Dashboard</h2>", unsafe_allow_html=True)
        if not saved_lessons:
            st.info("Performance trajectory data requires metric generation from active quizzes. Once you generate and complete a curriculum under the 'Learn' tab, your metrics tracker will show up here.")
            df_empty = pd.DataFrame({"Completed Lessons": [0]}, index=["Initial Setup"])
            st.line_chart(df_empty)
        else:
            progress_data = {
                "Topic Module": [row[0] for row in saved_lessons],
                "Regional Focus": [row[2] for row in saved_lessons],
                "Competency Framework": ["Completed" for _ in saved_lessons]
            }
            df = pd.DataFrame(progress_data)
            st.dataframe(df, use_container_width=True)
            st.line_chart(df.index)

    elif st.session_state.current_page == "Profile":
        st.markdown("<h2>👤 Student Learning Registry</h2>", unsafe_allow_html=True)
        st.write(f"**Authenticated User Identity:** {st.session_state.current_user}")
        st.write("---")
        st.subheader("📚 Logged Curriculum Packages")
        
        if not saved_lessons:
            st.caption("No registered history indexes logged yet for this specific account. Head over to the 'Learn' tab to populate your workspace registry.")
        else:
            for row in saved_lessons:
                st.markdown(f"""
                    <div class="profile-card">
                        <b>📌 Topic:</b> {row[0]} <br/>
                        <b>🌍 Context Profile:</b> {row[2]} | <b>🗣️ Language:</b> {row[1]}
                    </div>
                """, unsafe_allow_html=True)