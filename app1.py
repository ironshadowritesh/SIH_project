import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# 1. Website Setup
st.set_page_config(page_title="Maharashtra Skilling Tracker", layout="wide")
st.title("🏛️ Government of Maharashtra - Skilling Impact Tracker")

# 2. Database Load Karna (SIH Strict Version)
import os

mandatory_columns = [
    'Student Ka Naam', 'Kaun sa course kiya?', 'Job_Status', 'Salary', 
    'Skill_Gap', 'District', 'Gender', 'Employer_Verified', 
    'Mobile_Number', 'User_Consent', 'Aadhaar_Number', 'No_Placement_Reason'
]

try:
    if not os.path.exists("data.csv"):
        # Agar file nahi hai, to automatically headers ke saath nayi file create karo
        df = pd.DataFrame(columns=mandatory_columns)
        df.to_csv("data.csv", index=False)
    else:
        df = pd.read_csv("data.csv")
        # Ensure completely empty files get structures
        if df.empty or len(df.columns) == 0:
            df = pd.DataFrame(columns=mandatory_columns)
        else:
            for col in mandatory_columns:
                if col not in df.columns:
                    df[col] = "None"
except Exception as e:
    df = pd.DataFrame(columns=mandatory_columns)

for col in df.columns:
    df[col] = df[col].astype(str).str.strip()
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

# 3. Sidebar / Login System (Role-Based Access)
st.sidebar.header("🔐 User Authentication")
role = st.sidebar.selectbox("Choose Your Role", ["Student / Candidate", "Government Officer"])

if role == "Government Officer":
    st.sidebar.markdown("---")
    password = st.sidebar.text_input("Enter Officer Password", type="password")
    
    if password == "mahasarkar123":
        st.sidebar.success("✅ Access Granted")
        menu = "Sarkar Ka Dashboard"
    else:
        if password != "":
            st.sidebar.error("❌ Invalid Password")
        menu = "Locked"
        st.warning("🔒 This section is locked. Please enter the Government Officer password in the sidebar to view live analytics.")
else:
    menu = "Student Registration"

# --- PAGE 1: STUDENT REGISTRATION FORM ---
if menu == "Student Registration" :
    st.header("📝 Consent-Based Student Data Entry")
    
    with st.form("student_form"):
        name = st.text_input("Student Ka Naam")
        mobile = st.text_input("Mobile Number", max_chars=10)
        aadhaar = st.text_input("Aadhaar Card Number (12 Digits)", max_chars=12)
        course = st.selectbox("Kaun sa course kiya?", ["Web Dev", "Python", "Data Entry", "Nursing", "Digital Marketing"])
        job = st.radio("Naukri Mili?", ["Yes", "No"])
        salary = st.number_input("Salary (INR)", min_value=0, value=0)
        gap = st.selectbox("Aapko kis skill mein dikkat aayi?", ["English Speaking", "Technical", "Interview Confidence", "Communication"])
        district = st.selectbox("Aapka District (Zila)", ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"])
        gender = st.radio("Gender", ["Male", "Female"])
        verified = st.radio("Employer Se Verified?", ["Yes", "No"])
        
        # SARKAR KI DEMAND: Reason for non-placement
        no_job_reason = st.selectbox("Agar naukri nahi mili, toh kya wajah rahi?", ["None", "Low Salary Offered", "No Local Jobs", "Lacked Technical Skills", "Higher Studies"])
        
        st.markdown("---")
        consent = st.checkbox("Main Maharashtra Sarkar ko apna data track karne ki anumati deta hoon.")
        
        request_otp = st.form_submit_button("🛡️ Verify Aadhaar via OTP")
        
        if request_otp:
            if len(aadhaar) != 12 or not aadhaar.isdigit():
                st.error("❌ Pehle sahi 12-digit ka Aadhaar number dalo!")
            elif aadhaar in df['Aadhaar_Number'].values:
                st.error("❌ Yeh Aadhaar pehle se registered hai!")
            elif not consent:
                st.warning("❌ Consent dena zaroori hai!")
            else:
                st.session_state.generated_otp = str(random.randint(1000, 9999))
                st.session_state.otp_sent = True

    if st.session_state.otp_sent:
        st.markdown("### 🔐 Enter Aadhaar Verification OTP")
        st.warning(f"✨ [DEMO MODE]: OTP is: {st.session_state.generated_otp}")
        with st.form("otp_verification_form"):
            user_otp = st.text_input("Enter 4-Digit OTP", max_chars=4)
            final_submit = st.form_submit_button("✅ Final Registration & Save")
            
            if final_submit:
                if user_otp == st.session_state.generated_otp:
                    new_row = [name, course, job, salary, gap, district, gender, verified, mobile, "Yes", aadhaar, no_job_reason]
                    new_data = pd.DataFrame([new_row], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv("data.csv", index=False)
                    st.success("🎉 Data safely save ho gaya.")
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = None
                else:
                    st.error("❌ Galat OTP!")
                   # --- PAGE 2: ADVANCED SARKAR DASHBOARD ---
if menu == "Sarkar Ka Dashboard" and not df.empty:
    st.header("📊 Live Analytics Dashboard for Officers")
    districts_list = ["All Districts"] + list(df['District'].unique())
    selected_district = st.selectbox("🔎 Filter by District", districts_list)
    
    filtered_df = df if selected_district == "All Districts" else df[df['District'] == selected_district]

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students Tracked", len(filtered_df))
    
    # 1. Job Status Clean Check
    if 'Job_Status' in filtered_df.columns:
        col2.metric("Total Employed", len(filtered_df[filtered_df['Job_Status'].str.strip() == 'Yes']))
    else:
        col2.metric("Total Employed", 0)
        
    # 2. Salary Crash Safe Calculation
    if 'Salary' in filtered_df.columns:
        numeric_salary = pd.to_numeric(filtered_df['Salary'], errors='coerce').fillna(0)
        avg_sal = numeric_salary[numeric_salary > 0].mean()
    else:
        avg_sal = 0

    col3.metric("Average Salary (INR)", int(avg_sal if pd.notna(avg_sal) else 0))
    st.markdown("---")
    
    graph_col1, graph_col2 = st.columns(2)
    with graph_col1:
        st.subheader("🎯 Employment Status (Pie Chart)")
        if 'Job_Status' in filtered_df.columns:
            job_counts = filtered_df['Job_Status'].value_counts()
            if not job_counts.empty:
                fig, ax = plt.subplots(figsize=(4, 4))
                colors = ['#2ca02c', '#d62728'] if 'Yes' in job_counts.index and 'No' in job_counts.index else None
                ax.pie(job_counts, labels=job_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
                ax.axis('equal')
                st.pyplot(fig)
            
    with graph_col2:
        st.subheader("⚠️ Major Skill Gaps Identified")
        if 'Skill_Gap' in filtered_df.columns:
            st.bar_chart(filtered_df['Skill_Gap'].value_counts())
        elif 'gap' in filtered_df.columns:
            st.bar_chart(filtered_df['gap'].value_counts())
        
    st.markdown("---")
    
    graph_col3, graph_col4 = st.columns(2)
    with graph_col3:
        st.subheader("🧑‍🤝‍🧑 Gender-wise Training Distribution")
        if 'Gender' in filtered_df.columns:
            st.bar_chart(filtered_df['Gender'].value_counts())
        
    with graph_col4:
        st.subheader("🛑 Reasons for Non-Placement / Attrition")
        if 'Job_Status' in filtered_df.columns and 'No_Placement_Reason' in filtered_df.columns:
            no_job_df = filtered_df[(filtered_df['Job_Status'].str.strip() == 'No') & (filtered_df['No_Placement_Reason'].str.strip() != 'None')]
            if not no_job_df.empty:
                st.bar_chart(no_job_df['No_Placement_Reason'].value_counts())
            else:
                st.write("Abhi koi Unemployed data nahi hai.")