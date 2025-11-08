"""
Comprehensive test suite for Agentic AI PD Coach
Includes unit tests, integration tests, and end-to-end tests
"""

import pytest
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, List, Any

# Import our modules
import sys
sys.path.append('..')
from app.agents.pd_coach_agent import PDCOachAgent, TeacherProfile, AgentResponse
from app.tools.tools import (
    knowledge_search_tool, fetch_resource_tool, generate_lesson_plan_tool,
    save_profile_tool, load_profile_tool, schedule_workshop_tool
)
from app.api.main import app
from fastapi.testclient import TestClient


class TestTools:
    """Unit tests for LangChain tools"""
    
    def test_knowledge_search_tool(self):
        """Test knowledge search functionality"""
        result = knowledge_search_tool.run({"query": "blended learning"})
        
        assert "results" in result
        assert len(result["results"]) > 0
        assert "title" in result["results"][0]
        assert "content" in result["results"][0]
        assert "evidence_level" in result["results"][0]
    
    def test_knowledge_search_specific_topics(self):
        """Test knowledge search for specific educational topics"""
        topics = ["retrieval practice", "formative assessment", "active learning"]
        
        for topic in topics:
            result = knowledge_search_tool.run({"query": topic})
            assert len(result["results"]) > 0
            assert topic.lower() in result["results"][0]["content"].lower()
    
    def test_fetch_resource_tool(self):
        """Test resource fetching functionality"""
        result = fetch_resource_tool.run({
            "resource_type": "tool",
            "grade_level": "6-8",
            "subject": "Science",
            "tech_level": "intermediate"
        })
        
        assert "resources" in result
        assert len(result["resources"]) > 0
        assert "title" in result["resources"][0]
        assert "url" in result["resources"][0]
        assert "description" in result["resources"][0]
    
    def test_generate_lesson_plan_tool(self):
        """Test lesson plan generation"""
        result = generate_lesson_plan_tool.run({
            "grade": "6",
            "subject": "Science",
            "duration_minutes": 45,
            "objective": "Understand food chains",
            "technology": ["Padlet"],
            "skill_level": "intermediate"
        })
        
        assert "title" in result
        assert "steps" in result
        assert "materials" in result
        assert "assessment" in result
        assert len(result["steps"]) > 0
        assert result["duration_minutes"] == 45
    
    def test_save_and_load_profile_tools(self):
        """Test profile save and load functionality"""
        test_profile = {
            "name": "Test Teacher",
            "grade_level": "9",
            "subject": "Math",
            "tech_comfort": "intermediate",
            "time_availability": "2 hours per week",
            "class_duration": 50,
            "goals": ["Improve assessment", "Use technology"]
        }
        
        # Save profile
        save_result = save_profile_tool.run(test_profile)
        assert "profile_id" in save_result
        profile_id = save_result["profile_id"]
        
        # Load profile
        load_result = load_profile_tool.run({"profile_id": profile_id})
        assert load_result["name"] == test_profile["name"]
        assert load_result["grade_level"] == test_profile["grade_level"]
        assert load_result["subject"] == test_profile["subject"]
    
    def test_schedule_workshop_tool(self):
        """Test workshop scheduling"""
        result = schedule_workshop_tool.run({
            "teacher_id": "teacher_001",
            "workshop_title": "Blended Learning Workshop",
            "suggested_times": ["2024-01-15T14:00", "2024-01-16T10:00"],
            "duration_minutes": 120
        })
        
        assert "workshop_id" in result
        assert "scheduled_time" in result
        assert "status" in result
        assert result["status"] == "scheduled"


class TestAgent:
    """Integration tests for the PD Coach Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return PDCOachAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.llm is not None
        assert agent.memory is not None
        assert len(agent.tools) == 6  # Number of tools
    
    def test_agent_process_simple_request(self, agent):
        """Test processing a simple request"""
        request = "What is blended learning?"
        teacher_profile = TeacherProfile(
            id="test_001",
            name="Test Teacher",
            grade_level="6",
            subject="Science",
            tech_comfort="intermediate",
            time_availability="2 hours per week",
            class_duration=45,
            goals=["Learn blended learning"],
            preferences={}
        )
        
        response = agent.process_request(request, teacher_profile)
        
        assert isinstance(response, AgentResponse)
        assert response.response != ""
        assert response.confidence_score > 0
        assert response.teacher_id == "test_001"
    
    def test_agent_process_complex_request(self, agent):
        """Test processing a complex multi-step request"""
        request = "I want to implement blended learning in my 6th grade science class. Can you help me plan a lesson about food chains?"
        teacher_profile = TeacherProfile(
            id="test_001",
            name="Test Teacher", 
            grade_level="6",
            subject="Science",
            tech_comfort="intermediate",
            time_availability="2 hours per week",
            class_duration=45,
            goals=["Implement blended learning"],
            preferences={}
        )
        
        response = agent.process_request(request, teacher_profile)
        
        assert isinstance(response, AgentResponse)
        assert response.response != ""
        assert response.confidence_score > 0.6
        assert len(response.resources) > 0
        assert len(response.next_steps) > 0
        assert response.teacher_id == "test_001"
    
    def test_agent_handles_unknown_request(self, agent):
        """Test agent handles unknown requests gracefully"""
        request = "What is the capital of France?"
        teacher_profile = TeacherProfile(
            id="test_001",
            name="Test Teacher",
            grade_level="6",
            subject="Science",
            tech_comfort="intermediate",
            time_availability="2 hours per week",
            class_duration=45,
            goals=["Learn new things"],
            preferences={}
        )
        
        response = agent.process_request(request, teacher_profile)
        
        assert isinstance(response, AgentResponse)
        assert "education" in response.response.lower() or "professional development" in response.response.lower()
        assert response.confidence_score < 0.5  # Low confidence for off-topic
    
    def test_agent_memory_persistence(self, agent):
        """Test agent memory persists across requests"""
        teacher_profile = TeacherProfile(
            id="test_001",
            name="Test Teacher",
            grade_level="6",
            subject="Science",
            tech_comfort="intermediate",
            time_availability="2 hours per week",
            class_duration=45,
            goals=["Learn blended learning"],
            preferences={}
        )
        
        # First request
        request1 = "I want to learn about blended learning for my science class"
        response1 = agent.process_request(request1, teacher_profile)
        
        # Second request (should reference previous conversation)
        request2 = "Can you give me a specific example?"
        response2 = agent.process_request(request2, teacher_profile)
        
        # Response should show continuity
        assert response2.response != ""
        # Should reference previous context implicitly or explicitly
        assert len(response2.resources) > 0 or "example" in response2.response.lower()


class TestAPI:
    """Integration tests for FastAPI endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint"""
        response = client.post("/chat", json={
            "message": "What is blended learning?",
            "session_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "confidence_score" in data
        assert "resources" in data
        assert "next_steps" in data
    
    def test_profile_creation(self, client):
        """Test profile creation endpoint"""
        profile_data = {
            "name": "Test Teacher",
            "grade_level": "6",
            "subject": "Science",
            "tech_comfort": "intermediate",
            "time_availability": "2 hours per week",
            "class_duration": 45,
            "goals": ["Implement blended learning"],
            "preferences": {"notes": "Test preferences"}
        }
        
        response = client.post("/profile", json=profile_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == profile_data["name"]
        assert data["grade_level"] == profile_data["grade_level"]
        assert data["subject"] == profile_data["subject"]
        
        # Test profile retrieval
        profile_id = data["id"]
        get_response = client.get(f"/profile/{profile_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == profile_id
    
    def test_lesson_plan_generation(self, client):
        """Test lesson plan generation endpoint"""
        lesson_data = {
            "grade": "6",
            "subject": "Science",
            "duration_minutes": 45,
            "objective": "Understand food chains",
            "technology": ["Padlet"],
            "skill_level": "intermediate"
        }
        
        response = client.post("/generate/lesson-plan", json=lesson_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "steps" in data
        assert "materials" in data
        assert "assessment" in data
        assert "estimated_prep_time" in data
        assert len(data["steps"]) > 0
    
    def test_workshop_planning(self, client):
        """Test workshop planning endpoint"""
        workshop_data = {
            "teacher_id": "test_001",
            "topic": "Blended Learning",
            "goals": ["Implement blended learning"],
            "time_constraints": "2 hours per week",
            "preferred_formats": ["hands-on", "collaborative"]
        }
        
        response = client.post("/plan/workshop", json=workshop_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "workshop_plan" in data
        assert "recommended_workshops" in data["workshop_plan"]
        assert len(data["workshop_plan"]["recommended_workshops"]) > 0
    
    def test_feedback_submission(self, client):
        """Test feedback submission endpoint"""
        feedback_data = {
            "teacher_id": "test_001",
            "interaction_id": "test_interaction_001",
            "rating": 4,
            "comments": "Great response, very helpful!",
            "improvements": ["More specific examples", "Visual aids"]
        }
        
        response = client.post("/feedback", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "feedback_id" in data
        assert data["status"] == "submitted"
    
    def test_profile_deletion(self, client):
        """Test profile deletion endpoint"""
        # First create a profile
        profile_data = {
            "name": "Delete Test Teacher",
            "grade_level": "6",
            "subject": "Science",
            "tech_comfort": "intermediate",
            "time_availability": "2 hours per week",
            "class_duration": 45,
            "goals": ["Test deletion"],
            "preferences": {}
        }
        
        create_response = client.post("/profile", json=profile_data)
        profile_id = create_response.json()["id"]
        
        # Delete the profile
        delete_response = client.delete(f"/profile/{profile_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/profile/{profile_id}")
        assert get_response.status_code == 404


class TestEndToEnd:
    """End-to-end tests simulating real user flows"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_complete_teacher_flow(self, client):
        """Test complete teacher workflow from profile creation to lesson generation"""
        
        # Step 1: Create teacher profile
        profile_data = {
            "name": "End-to-End Test Teacher",
            "grade_level": "6",
            "subject": "Science",
            "tech_comfort": "intermediate",
            "time_availability": "2 hours per week",
            "class_duration": 45,
            "goals": ["Implement blended learning", "Improve assessment techniques"],
            "preferences": {"notes": "Prefers hands-on activities"}
        }
        
        profile_response = client.post("/profile", json=profile_data)
        assert profile_response.status_code == 200
        teacher_id = profile_response.json()["id"]
        
        # Step 2: Chat about blended learning
        chat_response = client.post("/chat", json={
            "message": "I want to implement blended learning in my science class. What tools would work well?",
            "teacher_id": teacher_id,
            "session_id": None
        })
        
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert len(chat_data["resources"]) > 0
        assert len(chat_data["next_steps"]) > 0
        session_id = chat_data["session_id"]
        
        # Step 3: Generate specific lesson plan
        lesson_response = client.post("/generate/lesson-plan", json={
            "teacher_id": teacher_id,
            "grade": "6",
            "subject": "Science",
            "duration_minutes": 45,
            "objective": "Understand ecosystems and food chains",
            "technology": ["Padlet", "Google Docs"],
            "skill_level": "intermediate"
        })
        
        assert lesson_response.status_code == 200
        lesson_data = lesson_response.json()
        assert "title" in lesson_data
        assert len(lesson_data["steps"]) > 0
        
        # Step 4: Plan workshop attendance
        workshop_response = client.post("/plan/workshop", json={
            "teacher_id": teacher_id,
            "topic": "Blended Learning Implementation",
            "goals": ["Successfully implement blended learning"],
            "time_constraints": "2 hours per week",
            "preferred_formats": ["hands-on", "collaborative"]
        })
        
        assert workshop_response.status_code == 200
        workshop_data = workshop_response.json()
        assert len(workshop_data["workshop_plan"]["recommended_workshops"]) > 0
        
        # Step 5: Submit feedback
        feedback_response = client.post("/feedback", json={
            "teacher_id": teacher_id,
            "interaction_id": session_id,
            "rating": 5,
            "comments": "Excellent experience! Very helpful recommendations.",
            "improvements": ["More visual examples", "Video tutorials"]
        })
        
        assert feedback_response.status_code == 200
        
        # Verify profile still exists
        profile_check = client.get(f"/profile/{teacher_id}")
        assert profile_check.status_code == 200
        
        print(f"✅ Complete teacher flow test passed for teacher {teacher_id}")


class TestMetrics:
    """Test evaluation metrics"""
    
    def test_personalization_score(self):
        """Test personalization score calculation"""
        from app.evaluation.metrics import calculate_personalization_score
        
        teacher_profile = {
            "grade_level": "6",
            "subject": "Science",
            "tech_comfort": "intermediate",
            "goals": ["Implement blended learning"]
        }
        
        agent_response = {
            "response": "Here's a blended learning approach for 6th grade science...",
            "resources": [
                {"title": "Padlet for Science", "type": "tool"},
                {"title": "Blended Learning Workshop", "type": "workshop"}
            ],
            "next_steps": ["Try Padlet", "Attend workshop"]
        }
        
        score = calculate_personalization_score(teacher_profile, agent_response)
        
        assert 0 <= score <= 1
        assert score > 0.7  # Should be well-personalized
    
    def test_pedagogical_alignment_score(self):
        """Test pedagogical alignment score"""
        from app.evaluation.metrics import calculate_pedagogical_alignment_score
        
        agent_response = {
            "response": "Use retrieval practice and formative assessment...",
            "resources": [
                {"title": "Retrieval Practice Guide", "type": "guide"},
                {"title": "Formative Assessment Tools", "type": "tool"}
            ]
        }
        
        score = calculate_pedagogical_alignment_score(agent_response)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should contain evidence-based practices
    
    def test_resource_validity_score(self):
        """Test resource validity score"""
        from app.evaluation.metrics import calculate_resource_validity_score
        
        agent_response = {
            "resources": [
                {"title": "Padlet", "url": "https://padlet.com"},
                {"title": "Kahoot!", "url": "https://kahoot.com"},
                {"title": "Broken Link", "url": "https://invalid-url-12345.com"}
            ]
        }
        
        score = calculate_resource_validity_score(agent_response)
        
        assert 0 <= score <= 1
        assert score < 1.0  # Should be less than perfect due to broken link
    
    def test_user_satisfaction_score(self):
        """Test user satisfaction score calculation"""
        from app.evaluation.metrics import calculate_user_satisfaction_score
        
        feedback_data = {
            "rating": 4,
            "comments": "Very helpful, learned a lot!",
            "improvements": ["More examples", "Faster response"]
        }
        
        score = calculate_user_satisfaction_score(feedback_data)
        
        assert 0 <= score <= 1
        assert score > 0.7  # 4/5 rating should be good


class TestSafetyPrivacy:
    """Test safety and privacy features"""
    
    def test_pii_detection(self):
        """Test PII detection in inputs"""
        from app.safety.pii_detector import detect_pii
        
        # Test with PII
        text_with_pii = "My student John Smith lives at 123 Main St and his phone is 555-1234"
        pii_result = detect_pii(text_with_pii)
        assert pii_result["has_pii"] == True
        assert len(pii_result["detected_entities"]) > 0
        
        # Test without PII
        text_without_pii = "I want to learn about blended learning strategies"
        pii_result = detect_pii(text_without_pii)
        assert pii_result["has_pii"] == False
    
    def test_content_filtering(self):
        """Test inappropriate content filtering"""
        from app.safety.content_filter import filter_content
        
        # Test appropriate content
        appropriate_content = "How can I improve my lesson planning?"
        filter_result = filter_content(appropriate_content)
        assert filter_result["is_appropriate"] == True
        
        # Test inappropriate content (would be blocked)
        # Note: Using mild example for testing
        inappropriate_content = "This is spam content that should be filtered"
        filter_result = filter_content(inappropriate_content)
        assert filter_result["is_appropriate"] == False
    
    def test_data_encryption(self):
        """Test data encryption for sensitive information"""
        from app.safety.encryption import encrypt_data, decrypt_data
        
        sensitive_data = "teacher_email@example.com"
        encrypted = encrypt_data(sensitive_data)
        
        assert encrypted != sensitive_data
        assert len(encrypted) > 0
        
        decrypted = decrypt_data(encrypted)
        assert decrypted == sensitive_data


def run_all_tests():
    """Run all tests and generate report"""
    print("🧪 Running comprehensive test suite for PD Coach Agent...")
    
    # Run pytest with detailed output
    pytest_args = [
        "-v",
        "--tb=short",
        "--html=test_report.html",
        "--self-contained-html",
        __file__
    ]
    
    result = pytest.main(pytest_args)
    
    if result == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Some tests failed. Exit code: {result}")
    
    return result


if __name__ == "__main__":
    run_all_tests()