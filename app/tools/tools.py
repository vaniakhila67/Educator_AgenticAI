"""
LangChain Tools for PD Coach Agent
Implementation of all tools used by the agent for knowledge search, resource fetching, etc.
"""

from typing import Dict, List, Optional, Any
from langchain_core.tools import Tool, StructuredTool
from langchain_core.documents import Document
from pydantic import BaseModel, Field
import json
import logging
import requests
from datetime import datetime, timedelta
import csv
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Tool Input Schemas
class KnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="Search query for pedagogical knowledge")
    grade_level: Optional[str] = Field(None, description="Target grade level")
    subject: Optional[str] = Field(None, description="Subject area")
    max_results: int = Field(5, description="Maximum number of results")

class FetchResourceInput(BaseModel):
    url: str = Field(..., description="URL of the resource to fetch")
    resource_type: Optional[str] = Field(None, description="Type of resource")

class GenerateLessonPlanInput(BaseModel):
    grade: str = Field(..., description="Grade level")
    subject: str = Field(..., description="Subject area")
    duration_minutes: int = Field(..., description="Lesson duration in minutes")
    objective: str = Field(..., description="Learning objective")
    technology: List[str] = Field(default_factory=list, description="Available technology tools")
    skill_level: str = Field("intermediate", description="Teacher's skill level")

class SaveProfileInput(BaseModel):
    profile_data: Dict[str, Any] = Field(..., description="Teacher profile data")

class LoadProfileInput(BaseModel):
    profile_id: str = Field(..., description="Teacher profile ID")

class ScheduleWorkshopInput(BaseModel):
    topic: str = Field(..., description="Workshop topic")
    suggested_times: List[str] = Field(..., description="Suggested time slots")
    duration_hours: float = Field(1.0, description="Workshop duration in hours")
    teacher_id: Optional[str] = Field(None, description="Teacher ID for personalization")

# Mock Knowledge Base (in production, this would be a real database/vector store)
PEDAGOGICAL_KNOWLEDGE = [
    {
        "title": "Active Learning Strategies",
        "content": "Active learning engages students in activities that promote analysis, synthesis, and evaluation. Research shows 23% improvement in student outcomes.",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "evidence_level": "High",
        "implementation_time": "15-30 minutes",
        "difficulty": "Beginner"
        
    },
    {
        "title": "Retrieval Practice",
        "content": "Regular low-stakes quizzing strengthens long-term retention. Studies show 50% improvement in long-term memory retention.",
        "grade_levels": ["3-12"],
        "subjects": ["All"],
        "evidence_level": "High",
        "implementation_time": "5-10 minutes",
        "difficulty": "Beginner"
    },
    {
        "title": "Formative Assessment Techniques",
        "content": "Ongoing assessment during instruction improves learning outcomes by 20-30%. Use exit tickets, think-pair-share, and digital tools.",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "evidence_level": "High",
        "implementation_time": "5-15 minutes",
        "difficulty": "Beginner"
    },
    {
        "title": "Blended Learning Models",
        "content": "Combining face-to-face and online instruction. Station rotation works well for beginners, flipped classroom for advanced users.",
        "grade_levels": ["3-12"],
        "subjects": ["All"],
        "evidence_level": "Moderate",
        "implementation_time": "1-2 weeks setup",
        "difficulty": "Intermediate"
    },
    {
        "title": "Universal Design for Learning",
        "content": "Create flexible learning environments that accommodate all learners. Provide multiple means of representation, engagement, and expression.",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "evidence_level": "High",
        "implementation_time": "Ongoing",
        "difficulty": "Intermediate"
    }
]

# Sample Resources Database
SAMPLE_RESOURCES = [
    {
        "title": "PhET Interactive Simulations",
        "url": "https://phet.colorado.edu",
        "type": "tool",
        "description": "Free interactive math and science simulations",
        "grade_levels": ["3-12"],
        "subjects": ["Science", "Math"],
        "cost": "Free"
    },
    {
        "title": "Padlet",
        "url": "https://padlet.com",
        "type": "tool",
        "description": "Digital collaboration board for student responses",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "cost": "Freemium"
    },
    {
        "title": "Kahoot",
        "url": "https://kahoot.com",
        "type": "tool",
        "description": "Game-based learning platform for formative assessment",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "cost": "Freemium"
    },
    {
        "title": "Retrieval Practice Question Bank",
        "url": "/resources/retrieval-questions",
        "type": "resource",
        "description": "Collection of retrieval practice questions by subject and grade",
        "grade_levels": ["3-12"],
        "subjects": ["All"],
        "cost": "Free"
    },
    {
        "title": "Station Rotation Template",
        "url": "/templates/station-rotation",
        "type": "template",
        "description": "Editable template for station rotation activities",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "cost": "Free"
    }
]

def knowledge_search_tool(query: str, grade_level: Optional[str] = None, 
                         subject: Optional[str] = None, max_results: int = 5) -> str:
    """
    Search pedagogical knowledge base for teaching strategies and evidence-based practices
    """
    try:
        # Filter knowledge base
        filtered_knowledge = []
        
        for item in PEDAGOGICAL_KNOWLEDGE:
            # Check if query matches
            query_match = query.lower() in item["title"].lower() or query.lower() in item["content"].lower()
            
            # Check grade level filter
            grade_match = True
            if grade_level:
                grade_match = any(grade_level in gl for gl in item["grade_levels"])
            
            # Check subject filter
            subject_match = True
            if subject:
                subject_match = subject.lower() in [s.lower() for s in item["subjects"]]
            
            if query_match and grade_match and subject_match:
                filtered_knowledge.append(item)
        
        # Limit results
        filtered_knowledge = filtered_knowledge[:max_results]
        
        if not filtered_knowledge:
            return json.dumps({
                "results": [],
                "message": "No specific strategies found. Try general terms like 'active learning' or 'assessment'."
            })
        
        return json.dumps({
            "results": filtered_knowledge,
            "count": len(filtered_knowledge),
            "query": query
        })
        
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        return json.dumps({"error": str(e), "results": []})

def fetch_resource_tool(url: str, resource_type: Optional[str] = None) -> str:
    """
    Fetch educational resource details and content
    """
    try:
        # Check if it's a sample resource
        for resource in SAMPLE_RESOURCES:
            if resource["url"] == url:
                return json.dumps({
                    "resource": resource,
                    "status": "found",
                    "content": f"Detailed information about {resource['title']}: {resource['description']}"
                })
        
        # For external URLs, attempt to fetch (with safety checks)
        if url.startswith("http"):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return json.dumps({
                        "url": url,
                        "status": "accessible",
                        "content_preview": response.text[:500],
                        "resource_type": resource_type
                    })
            except Exception as e:
                logger.warning(f"Could not fetch external URL {url}: {e}")
        
        return json.dumps({
            "url": url,
            "status": "not_found",
            "message": "Resource not found in database or could not be accessed."
        })
        
    except Exception as e:
        logger.error(f"Resource fetch error: {e}")
        return json.dumps({"error": str(e)})

def generate_lesson_plan_tool(grade: str, subject: str, duration_minutes: int, 
                              objective: str, technology: List[str] = None, 
                              skill_level: str = "intermediate") -> str:
    """
    Generate a customized lesson plan with technology integration
    """
    try:
        if technology is None:
            technology = []
        
        # Calculate steps based on duration
        if duration_minutes <= 30:
            steps = [
                {"time": 5, "activity": "Warm-up and engagement", "materials": ["Whiteboard"]},
                {"time": 20, "activity": "Main instruction and guided practice", "materials": technology},
                {"time": 5, "activity": "Assessment and closure", "materials": ["Exit tickets"]}
            ]
        elif duration_minutes <= 60:
            steps = [
                {"time": 10, "activity": "Introduction and hook", "materials": ["Whiteboard", "Visual aids"]},
                {"time": 25, "activity": "Direct instruction with technology integration", "materials": technology + ["Projector"]},
                {"time": 20, "activity": "Guided and independent practice", "materials": ["Handouts"] + technology},
                {"time": 5, "activity": "Assessment and wrap-up", "materials": ["Exit tickets"]}
            ]
        else:
            steps = [
                {"time": 15, "activity": "Introduction and prior knowledge activation", "materials": ["Whiteboard", "Chart paper"]},
                {"time": 30, "activity": "Main instruction with interactive elements", "materials": technology + ["Projector", "Speakers"]},
                {"time": 20, "activity": "Collaborative practice and discussion", "materials": ["Group materials"] + technology},
                {"time": 10, "activity": "Independent application", "materials": ["Worksheets"] + technology},
                {"time": 5, "activity": "Reflection and assessment", "materials": ["Reflection journals"]}
            ]
        
        # Generate assessment approach
        assessment = "Formative assessment through observation, questioning, and exit tickets"
        if technology:
            assessment += f" Technology-enhanced assessment using {', '.join(technology)}"
        
        # Calculate prep time based on complexity
        prep_time = 30 if skill_level == "beginner" else 20 if skill_level == "intermediate" else 15
        if technology:
            prep_time += len(technology) * 5
        
        lesson_plan = {
            "title": f"{subject} - {objective}",
            "grade": grade,
            "duration_minutes": duration_minutes,
            "objective": objective,
            "steps": steps,
            "materials": ["Basic classroom supplies"] + technology,
            "assessment": assessment,
            "technology_integration": f"Use {', '.join(technology)} to enhance engagement and learning" if technology else "Technology not specified",
            "estimated_prep_time": prep_time,
            "difficulty_level": skill_level,
            "tips": [
                "Test all technology before the lesson",
                "Have a backup plan for tech failures",
                "Prepare materials in advance",
                "Differentiate for various learning levels"
            ]
        }
        
        return json.dumps(lesson_plan)
        
    except Exception as e:
        logger.error(f"Lesson plan generation error: {e}")
        return json.dumps({"error": str(e)})

def save_profile_tool(profile_data: Dict[str, Any]) -> str:
    """
    Save teacher profile data
    """
    try:
        # In production, this would save to a database
        profile_id = profile_data.get("id", str(uuid.uuid4()))
        
        # Simulate saving
        saved_data = {
            "profile_id": profile_id,
            "saved_at": datetime.now().isoformat(),
            "data": profile_data,
            "status": "saved"
        }
        
        return json.dumps(saved_data)
        
    except Exception as e:
        logger.error(f"Profile save error: {e}")
        return json.dumps({"error": str(e)})

def load_profile_tool(profile_id: str) -> str:
    """
    Load teacher profile data
    """
    try:
        # In production, this would load from a database
        # For now, return mock data
        mock_profile = {
            "id": profile_id,
            "name": "Sample Teacher",
            "grade_level": "6",
            "subject": "Science",
            "tech_comfort": "intermediate",
            "time_availability": "2 hours per week",
            "class_duration": 45,
            "goals": ["Implement blended learning", "Improve assessment techniques"],
            "preferences": {"learning_style": "hands-on", "tech_tools": ["Padlet", "Kahoot"]}
        }
        
        return json.dumps({
            "profile": mock_profile,
            "status": "found",
            "loaded_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Profile load error: {e}")
        return json.dumps({"error": str(e)})

def schedule_workshop_tool(topic: str, suggested_times: List[str], 
                          duration_hours: float = 1.0, teacher_id: Optional[str] = None) -> str:
    """
    Schedule a professional development workshop
    """
    try:
        # Generate workshop schedule
        workshop_schedule = {
            "topic": topic,
            "duration_hours": duration_hours,
            "suggested_times": suggested_times,
            "proposed_schedule": {
                "agenda": [
                    {"time": "15 min", "activity": "Welcome and introductions"},
                    {"time": "30 min", "activity": f"Introduction to {topic}"},
                    {"time": "45 min", "activity": "Hands-on exploration and practice"},
                    {"time": "15 min", "activity": "Implementation planning"},
                    {"time": "15 min", "activity": "Q&A and next steps"}
                ],
                "materials_needed": [
                    "Computers or tablets",
                    "Internet access",
                    "Projector and screen",
                    "Handouts and worksheets",
                    "Sticky notes and markers"
                ],
                "preparation_checklist": [
                    "Book venue and equipment",
                    "Send invitations to participants",
                    "Prepare handouts and materials",
                    "Test all technology in advance",
                    "Prepare follow-up resources"
                ]
            },
            "teacher_id": teacher_id,
            "created_at": datetime.now().isoformat()
        }
        
        return json.dumps(workshop_schedule)
        
    except Exception as e:
        logger.error(f"Workshop scheduling error: {e}")
        return json.dumps({"error": str(e)})

def create_tools() -> List[Tool]:
    """
    Create all tools for the PD Coach Agent
    """
    tools = [
        Tool(
            name="knowledge_search",
            func=knowledge_search_tool,
            description="Search pedagogical knowledge base for teaching strategies, evidence-based practices, and educational research"
        ),
        Tool(
            name="fetch_resource",
            func=fetch_resource_tool,
            description="Fetch educational resources, tools, and materials from URLs or databases"
        ),
        Tool(
            name="generate_lesson_plan",
            func=generate_lesson_plan_tool,
            description="Generate customized lesson plans with technology integration and step-by-step instructions"
        ),
        Tool(
            name="save_profile",
            func=save_profile_tool,
            description="Save teacher profile data for personalization and memory"
        ),
        Tool(
            name="load_profile",
            func=load_profile_tool,
            description="Load teacher profile data for personalization"
        ),
        Tool(
            name="schedule_workshop",
            func=schedule_workshop_tool,
            description="Schedule and plan professional development workshops with agendas and materials"
        )
    ]
    
    return tools