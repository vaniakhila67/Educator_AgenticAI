"""
Streamlit Frontend for Agentic AI PD Coach
Interactive educator-facing interface with chat, profile management, and resource library
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
PAGE_TITLE = "🎓 AI PD Coach"
PAGE_ICON = "🎓"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

if 'teacher_profile' not in st.session_state:
    st.session_state.teacher_profile = None

if 'current_lesson_plan' not in st.session_state:
    st.session_state.current_lesson_plan = None

if 'resources' not in st.session_state:
    st.session_state.resources = []

def init_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .coach-message {
            background-color: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        .resource-card {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .confidence-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 1rem;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .confidence-high { background-color: #4caf50; color: white; }
        .confidence-medium { background-color: #ff9800; color: white; }
        .confidence-low { background-color: #f44336; color: white; }
        </style>
    """, unsafe_allow_html=True)

def api_request(method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def create_teacher_profile():
    """Create teacher profile form"""
    st.header("👤 Create Your Teacher Profile")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="Your name")
            grade_level = st.text_input("Grade Level(s) *", placeholder="e.g., 6, K-2, 9-10")
            subject = st.text_input("Subject Area *", placeholder="e.g., Science, Math, ELA")
            
        with col2:
            tech_comfort = st.selectbox(
                "Technology Comfort Level *",
                ["beginner", "intermediate", "advanced"],
                help="How comfortable are you with educational technology?"
            )
            time_availability = st.text_input(
                "Time Available for PD *",
                placeholder="e.g., 2 hours per week"
            )
            class_duration = st.number_input(
                "Typical Class Duration (minutes) *",
                min_value=15, max_value=120, value=45
            )
        
        goals = st.multiselect(
            "Professional Development Goals",
            [
                "Implement blended learning",
                "Improve assessment techniques",
                "Integrate educational technology",
                "Enhance student engagement",
                "Develop project-based learning",
                "Improve classroom management",
                "Differentiate instruction",
                "Build retrieval practice routines"
            ],
            help="Select your main PD goals"
        )
        
        preferences = st.text_area(
            "Additional Preferences (Optional)",
            placeholder="Any specific preferences, learning styles, or requirements..."
        )
        
        submitted = st.form_submit_button("Create Profile", type="primary")
        
        if submitted and name and grade_level and subject and time_availability:
            profile_data = {
                "name": name,
                "grade_level": grade_level,
                "subject": subject,
                "tech_comfort": tech_comfort,
                "time_availability": time_availability,
                "class_duration": class_duration,
                "goals": goals,
                "preferences": {"notes": preferences} if preferences else {}
            }
            
            response = api_request("POST", "/profile", profile_data)
            if response:
                st.session_state.teacher_profile = response
                st.success("Profile created successfully!")
                st.rerun()

def display_chat_interface():
    """Display chat interface"""
    st.header("💬 Chat with Your AI PD Coach")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Coach message with confidence badge
                confidence_class = "confidence-high"
                if message.get("confidence", 0.7) < 0.6:
                    confidence_class = "confidence-low"
                elif message.get("confidence", 0.7) < 0.8:
                    confidence_class = "confidence-medium"
                
                confidence_html = f"""
                    <span class="confidence-badge {confidence_class}">
                        Confidence: {message.get('confidence', 0.7):.0%}
                    </span>
                """ if "confidence" in message else ""
                
                st.markdown(f"""
                    <div class="chat-message coach-message">
                        <strong>🎓 AI Coach:</strong> {message["content"]}
                        {confidence_html}
                    </div>
                """, unsafe_allow_html=True)
                
                # Display resources if available
                if message.get("resources"):
                    st.markdown("**📚 Recommended Resources:**")
                    for resource in message["resources"]:
                        st.markdown(f"""
                            <div class="resource-card">
                                <strong>{resource.get('title', 'Resource')}</strong><br>
                                {resource.get('description', '')}<br>
                                <a href="{resource.get('url', '#')}" target="_blank">Access Resource</a>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Display next steps if available
                if message.get("next_steps"):
                    with st.expander("🎯 Next Steps"):
                        for step in message["next_steps"]:
                            st.write(f"• {step}")
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask your PD Coach anything...",
                placeholder="How can I implement blended learning in my classroom?",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send", type="primary")
        
        if submitted and user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Prepare chat request
            chat_data = {
                "message": user_input,
                "session_id": st.session_state.session_id
            }
            
            if st.session_state.teacher_profile:
                chat_data["teacher_id"] = st.session_state.teacher_profile["id"]
            
            # Get coach response
            with st.spinner("🤔 Coach is thinking..."):
                response = api_request("POST", "/chat", chat_data)
                
                if response:
                    st.session_state.session_id = response.get("session_id")
                    
                    # Add coach message
                    coach_message = {
                        "role": "coach",
                        "content": response.get("response", "I apologize, I couldn't process your request."),
                        "confidence": response.get("confidence_score", 0.7),
                        "resources": response.get("resources", []),
                        "next_steps": response.get("next_steps", [])
                    }
                    
                    st.session_state.messages.append(coach_message)
                    
                    # Store resources for the library
                    if response.get("resources"):
                        st.session_state.resources.extend(response.get("resources", []))
            
            st.rerun()

def lesson_plan_generator():
    """Lesson plan generator interface"""
    st.header("📋 Lesson Plan Generator")
    
    with st.form("lesson_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            grade = st.text_input("Grade Level *", placeholder="e.g., 6, 9-10")
            subject = st.text_input("Subject *", placeholder="e.g., Science, Math")
            duration = st.number_input("Duration (minutes) *", min_value=15, max_value=120, value=45)
            
        with col2:
            objective = st.text_input("Learning Objective *", placeholder="Students will understand...")
            skill_level = st.selectbox("Your Skill Level", ["beginner", "intermediate", "advanced"])
            
        technology = st.multiselect(
            "Available Technology",
            ["Padlet", "Kahoot", "PhET Simulations", "Google Docs", "Zoom", "Nearpod", "Edpuzzle"],
            help="Select tools you have available"
        )
        
        submitted = st.form_submit_button("Generate Lesson Plan", type="primary")
        
        if submitted and grade and subject and objective:
            lesson_data = {
                "grade": grade,
                "subject": subject,
                "duration_minutes": duration,
                "objective": objective,
                "technology": technology,
                "skill_level": skill_level
            }
            
            if st.session_state.teacher_profile:
                lesson_data["teacher_id"] = st.session_state.teacher_profile["id"]
            
            with st.spinner("📝 Generating lesson plan..."):
                response = api_request("POST", "/generate/lesson-plan", lesson_data)
                
                if response:
                    st.session_state.current_lesson_plan = response
                    st.success("Lesson plan generated!")
                    st.rerun()
    
    # Display current lesson plan
    if st.session_state.current_lesson_plan:
        st.subheader("Your Generated Lesson Plan")
        plan = st.session_state.current_lesson_plan
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prep Time", f"{plan.get('estimated_prep_time', 0)} min")
        with col2:
            st.metric("Duration", f"{plan.get('duration_minutes', 0)} min")
        with col3:
            st.metric("Difficulty", plan.get('difficulty_level', 'Unknown'))
        
        st.markdown(f"**Objective:** {plan.get('objective', 'Not specified')}")
        st.markdown(f"**Assessment:** {plan.get('assessment', 'Not specified')}")
        
        if plan.get('steps'):
            st.markdown("**Lesson Steps:**")
            for i, step in enumerate(plan.get('steps', [])):
                with st.expander(f"Step {i+1}: {step.get('activity', 'Activity')}"):
                    st.write(f"**Time:** {step.get('time', 'Unknown')} minutes")
                    st.write(f"**Materials:** {', '.join(step.get('materials', []))}")
        
        if plan.get('materials'):
            st.markdown(f"**Materials Needed:** {', '.join(plan.get('materials', []))}")
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Export to Google Docs"):
                st.info("Google Docs export would be implemented here")
        with col2:
            if st.button("📊 Export to PPTX"):
                st.info("PowerPoint export would be implemented here")

def resource_library():
    """Resource library interface"""
    st.header("📚 Resource Library")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        resource_type = st.selectbox("Resource Type", ["All", "Tools", "Templates", "Tutorials", "Research"])
    with col2:
        grade_filter = st.text_input("Grade Level", placeholder="e.g., 6, K-2")
    with col3:
        subject_filter = st.text_input("Subject", placeholder="e.g., Science")
    
    # Generate resources based on filters
    if st.button("Search Resources"):
        resource_data = {
            "resource_type": resource_type.lower() if resource_type != "All" else "all",
            "grade_level": grade_filter or "K-12",
            "subject": subject_filter or "All",
            "tech_level": st.session_state.teacher_profile.get("tech_comfort", "intermediate") if st.session_state.teacher_profile else "intermediate"
        }
        
        response = api_request("POST", "/generate/resource", resource_data)
        if response and response.get("resources"):
            st.session_state.resources = response.get("resources", [])
    
    # Display resources
    if st.session_state.resources:
        st.subheader(f"Found {len(st.session_state.resources)} Resources")
        
        for resource in st.session_state.resources:
            with st.container():
                st.markdown(f"""
                    <div class="resource-card">
                        <h4>{resource.get('title', 'Resource')}</h4>
                        <p><strong>Type:</strong> {resource.get('type', 'Unknown')}</p>
                        <p>{resource.get('description', 'No description available')}</p>
                        <a href="{resource.get('url', '#')}" target="_blank">🔗 Access Resource</a>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Use the search above to find resources, or ask the coach for recommendations in the chat!")

def profile_management():
    """Profile management interface"""
    st.header("👤 Profile Management")
    
    if not st.session_state.teacher_profile:
        st.info("Create your profile to get personalized recommendations!")
        return
    
    profile = st.session_state.teacher_profile
    
    # Display current profile
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Profile:**")
        st.write(f"**Name:** {profile.get('name', 'Unknown')}")
        st.write(f"**Grade Level:** {profile.get('grade_level', 'Unknown')}")
        st.write(f"**Subject:** {profile.get('subject', 'Unknown')}")
        st.write(f"**Tech Comfort:** {profile.get('tech_comfort', 'Unknown')}")
    
    with col2:
        st.write(f"**Time Available:** {profile.get('time_availability', 'Unknown')}")
        st.write(f"**Class Duration:** {profile.get('class_duration', 'Unknown')} minutes")
        if profile.get('goals'):
            st.write(f"**Goals:** {', '.join(profile.get('goals', []))}")
    
    # Profile actions
    st.subheader("Profile Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Profile"):
            response = api_request("GET", f"/profile/{profile['id']}")
            if response:
                st.session_state.teacher_profile = response
                st.success("Profile refreshed!")
                st.rerun()
    
    with col2:
        if st.button("🗑️ Delete Profile"):
            response = api_request("DELETE", f"/profile/{profile['id']}")
            if response:
                st.session_state.teacher_profile = None
                st.session_state.messages = []
                st.session_state.session_id = None
                st.success("Profile deleted successfully!")
                st.rerun()
    
    with col3:
        if st.button("💬 Clear Chat History"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.success("Chat history cleared!")
            st.rerun()

def main():
    """Main Streamlit app"""
    init_page()
    
    # Sidebar
    with st.sidebar:
        st.title(f"{PAGE_ICON} AI PD Coach")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["💬 Chat", "📋 Lesson Plan Generator", "📚 Resource Library", "👤 Profile"]
        )
        
        st.divider()
        
        # Profile status
        if st.session_state.teacher_profile:
            st.success(f"✅ Profile Active\n{st.session_state.teacher_profile['name']}")
        else:
            st.warning("⚠️ No Profile Set")
        
        # Chat status
        if st.session_state.messages:
            st.info(f"💬 {len(st.session_state.messages)} messages")
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        
        if st.button("🆕 New Chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
        
        if st.button("📊 Export Chat"):
            chat_export = {
                "timestamp": datetime.now().isoformat(),
                "profile": st.session_state.teacher_profile,
                "messages": st.session_state.messages
            }
            st.download_button(
                "💾 Download Chat",
                data=json.dumps(chat_export, indent=2),
                file_name=f"pd_coach_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Main content
    if page == "💬 Chat":
        if not st.session_state.teacher_profile:
            create_teacher_profile()
        else:
            display_chat_interface()
    
    elif page == "📋 Lesson Plan Generator":
        if not st.session_state.teacher_profile:
            st.warning("Please create your profile first to get personalized lesson plans!")
            create_teacher_profile()
        else:
            lesson_plan_generator()
    
    elif page == "📚 Resource Library":
        resource_library()
    
    elif page == "👤 Profile":
        if not st.session_state.teacher_profile:
            create_teacher_profile()
        else:
            profile_management()

if __name__ == "__main__":
    main()