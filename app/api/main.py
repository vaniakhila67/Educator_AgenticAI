"""
FastAPI Backend for Agentic AI PD Coach
Core API endpoints and request/response models
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
import json
import logging
from datetime import datetime
from enum import Enum

# Import our agent
from app.agents.pd_coach_agent import PDCOachAgent, TeacherProfile, AgentResponse
from app.tools.tools import create_tools
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI PD Coach API",
    description="Agentic AI Professional Development Coach for Educators",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for simplicity (in production, use proper database)
teacher_profiles = {}
conversation_sessions = {}

# Request/Response Models
class TechComfortLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message to the coach")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    teacher_id: Optional[str] = Field(None, description="Teacher profile ID")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Coach's response")
    session_id: str = Field(..., description="Conversation session ID")
    actions_taken: List[str] = Field(default_factory=list, description="Actions taken by agent")
    resources: List[Dict[str, str]] = Field(default_factory=list, description="Recommended resources")
    explanation: str = Field("", description="Explanation of recommendation")
    confidence_score: float = Field(0.0, description="Confidence in recommendation")
    next_steps: List[str] = Field(default_factory=list, description="Suggested next steps")

class TeacherProfileRequest(BaseModel):
    name: str = Field(..., description="Teacher's name")
    grade_level: str = Field(..., description="Grade level(s) taught")
    subject: str = Field(..., description="Primary subject area")
    tech_comfort: TechComfortLevel = Field(..., description="Technology comfort level")
    time_availability: str = Field(..., description="Available time per week for PD")
    class_duration: int = Field(..., description="Typical class period length in minutes")
    goals: List[str] = Field(default_factory=list, description="Professional development goals")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Additional preferences")

class TeacherProfileResponse(BaseModel):
    id: str = Field(..., description="Teacher profile ID")
    name: str = Field(..., description="Teacher's name")
    grade_level: str = Field(..., description="Grade level(s) taught")
    subject: str = Field(..., description="Primary subject area")
    tech_comfort: str = Field(..., description="Technology comfort level")
    time_availability: str = Field(..., description="Available time per week for PD")
    class_duration: int = Field(..., description="Typical class period length in minutes")
    goals: List[str] = Field(default_factory=list, description="Professional development goals")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Additional preferences")
    created_at: datetime = Field(..., description="Profile creation timestamp")

class LessonPlanRequest(BaseModel):
    grade: str = Field(..., description="Grade level")
    subject: str = Field(..., description="Subject area")
    duration_minutes: int = Field(..., description="Lesson duration in minutes")
    objective: str = Field(..., description="Learning objective")
    technology: List[str] = Field(default_factory=list, description="Available technology tools")
    skill_level: str = Field("intermediate", description="Teacher's skill level")
    teacher_id: Optional[str] = Field(None, description="Teacher profile ID for personalization")

class LessonPlanResponse(BaseModel):
    title: str = Field(..., description="Lesson plan title")
    steps: List[Dict[str, Any]] = Field(..., description="Lesson steps with timing")
    materials: List[str] = Field(..., description="Required materials")
    assessment: str = Field(..., description="Assessment approach")
    technology_integration: str = Field(..., description="How technology is integrated")
    estimated_prep_time: int = Field(..., description="Estimated preparation time in minutes")
    difficulty_level: str = Field(..., description="Difficulty level")

class WorkshopPlanRequest(BaseModel):
    topic: str = Field(..., description="Workshop topic")
    duration_hours: float = Field(..., description="Workshop duration in hours")
    audience_level: str = Field(..., description="Audience experience level")
    teacher_id: Optional[str] = Field(None, description="Teacher profile ID")

class ResourceRequest(BaseModel):
    resource_type: str = Field(..., description="Type of resource needed")
    grade_level: str = Field(..., description="Target grade level")
    subject: str = Field(..., description="Subject area")
    tech_level: str = Field(..., description="Technology level")

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback: Optional[str] = Field(None, description="Optional feedback text")
    teacher_id: Optional[str] = Field(None, description="Teacher profile ID")

# Initialize agent (this would be done more properly in production)
def get_agent():
    """Get or create the PD Coach Agent"""
    if not hasattr(app, "agent"):
        # Load API key from environment
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY must be set in the .env file")
        
        # Initialize LLM with explicit API key
        llm = ChatOpenAI(
            temperature=0.7, 
            model="gpt-3.5-turbo",
            api_key=api_key
        )
        
        # Create tools
        tools = create_tools()
        
        # Create memory
        memory = ChatMessageHistory()
        
        # Create agent
        app.agent = PDCOachAgent(llm=llm, tools=tools, memory=memory)
    
    return app.agent

# API Endpoints

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for conversational requests"""
    try:
        agent = get_agent()
        
        # Get or create session
        if not request.session_id:
            session_id = str(uuid.uuid4())
        else:
            session_id = request.session_id
        
        # Get teacher profile if provided
        teacher_profile = None
        if request.teacher_id and request.teacher_id in teacher_profiles:
            profile_data = teacher_profiles[request.teacher_id]
            teacher_profile = TeacherProfile(**profile_data)
        
        # Process request
        agent_response = await agent.process_request(
            user_input=request.message,
            teacher_profile=teacher_profile
        )
        
        # Store session data
        conversation_sessions[session_id] = {
            "last_interaction": datetime.now(),
            "teacher_id": request.teacher_id
        }
        
        return ChatResponse(
            response=agent_response.response,
            session_id=session_id,
            actions_taken=agent_response.actions_taken,
            resources=agent_response.resources,
            explanation=agent_response.rationale,
            confidence_score=agent_response.confidence_score,
            next_steps=agent_response.next_steps
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/profile", response_model=TeacherProfileResponse)
async def create_profile(request: TeacherProfileRequest):
    """Create a new teacher profile"""
    try:
        profile_id = str(uuid.uuid4())
        
        profile_data = {
            "id": profile_id,
            "name": request.name,
            "grade_level": request.grade_level,
            "subject": request.subject,
            "tech_comfort": request.tech_comfort.value,
            "time_availability": request.time_availability,
            "class_duration": request.class_duration,
            "goals": request.goals,
            "preferences": request.preferences,
            "created_at": datetime.now()
        }
        
        teacher_profiles[profile_id] = profile_data
        
        return TeacherProfileResponse(**profile_data)
        
    except Exception as e:
        logger.error(f"Profile creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{profile_id}", response_model=TeacherProfileResponse)
async def get_profile(profile_id: str):
    """Get teacher profile by ID"""
    if profile_id not in teacher_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return TeacherProfileResponse(**teacher_profiles[profile_id])

@app.post("/generate/lesson-plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(request: LessonPlanRequest):
    """Generate a customized lesson plan"""
    try:
        # This would call the lesson plan generation tool
        # For now, return a mock response
        mock_response = LessonPlanResponse(
            title=f"{request.subject} Lesson: {request.objective}",
            steps=[
                {"time": 5, "activity": "Warm-up and introduction", "materials": ["Whiteboard", "Markers"]},
                {"time": 15, "activity": "Main instruction with technology integration", "materials": request.technology},
                {"time": 20, "activity": "Guided practice and application", "materials": ["Handouts", "Digital tools"]},
                {"time": 5, "activity": "Assessment and wrap-up", "materials": ["Exit tickets"]}
            ],
            materials=["Computer", "Projector"] + request.technology,
            assessment="Formative assessment through observation and exit tickets",
            technology_integration=f"Integrate {', '.join(request.technology)} for interactive learning",
            estimated_prep_time=30,
            difficulty_level="Intermediate"
        )
        
        return mock_response
        
    except Exception as e:
        logger.error(f"Lesson plan generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan/workshop")
async def plan_workshop(request: WorkshopPlanRequest):
    """Plan a professional development workshop"""
    try:
        # This would use the workshop planning tool
        workshop_plan = {
            "title": f"{request.topic} Workshop",
            "duration": f"{request.duration_hours} hours",
            "agenda": [
                {"time": "30 min", "activity": "Introduction and objectives"},
                {"time": "60 min", "activity": "Hands-on exploration"},
                {"time": "30 min", "activity": "Implementation planning"},
                {"time": "30 min", "activity": "Q&A and next steps"}
            ],
            "materials_needed": ["Computers", "Internet access", "Handouts"],
            "audience_level": request.audience_level
        }
        
        return workshop_plan
        
    except Exception as e:
        logger.error(f"Workshop planning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/resource")
async def generate_resource(request: ResourceRequest):
    """Generate or fetch educational resources"""
    try:
        # This would use the resource generation tool
        resources = [
            {
                "title": f"{request.subject} {request.resource_type} for {request.grade_level}",
                "type": request.resource_type,
                "url": f"/resources/{request.resource_type}/{request.subject.lower()}/{request.grade_level}",
                "description": f"Customized {request.resource_type} for {request.grade_level} {request.subject}"
            }
        ]
        
        return {"resources": resources}
        
    except Exception as e:
        logger.error(f"Resource generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Submit feedback for a conversation session"""
    try:
        # Store feedback (in production, save to database)
        feedback_data = {
            "session_id": request.session_id,
            "rating": request.rating,
            "feedback": request.feedback,
            "teacher_id": request.teacher_id,
            "timestamp": datetime.now()
        }
        
        # Background task to process feedback for model improvement
        background_tasks.add_task(process_feedback, feedback_data)
        
        return {"status": "feedback_received", "message": "Thank you for your feedback!"}
        
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/profile/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete teacher profile (forget me functionality)"""
    if profile_id not in teacher_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Remove profile
    del teacher_profiles[profile_id]
    
    # Also clear any associated conversation data
    sessions_to_remove = [sid for sid, session in conversation_sessions.items() 
                          if session.get("teacher_id") == profile_id]
    for session_id in sessions_to_remove:
        del conversation_sessions[session_id]
    
    return {"status": "profile_deleted", "message": "Profile and associated data deleted"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI PD Coach API",
        "timestamp": datetime.now()
    }

# Background task function
def process_feedback(feedback_data: dict):
    """Process feedback for model improvement"""
    # In production, this would:
    # 1. Store feedback in database
    # 2. Analyze feedback trends
    # 3. Trigger model retraining if needed
    # 4. Send alerts for low ratings
    logger.info(f"Processing feedback: {feedback_data}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)