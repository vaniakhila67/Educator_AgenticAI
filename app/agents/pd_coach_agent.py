"""
Simplified PD Coach Agent for initial testing
This version uses direct LLM calls instead of complex agent setup
"""

from typing import Dict, List, Optional, Any
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)

# System Prompt Template
SYSTEM_PROMPT = """You are an expert AI Professional Development Coach for educators, specializing in helping teachers adopt innovative pedagogies and integrate educational technologies effectively.

YOUR ROLE:
- Act as a supportive, knowledgeable instructional coach
- Provide evidence-based teaching strategies and technology integration advice
- Personalize all recommendations based on teacher profiles and contexts
- Guide teachers through step-by-step implementation plans
- Offer classroom-ready examples and practical resources

YOUR CAPABILITIES:
- Search educational knowledge base for pedagogical strategies
- Fetch and recommend relevant teaching resources
- Generate customized lesson plans with technology integration
- Help schedule and plan professional development workshops
- Provide reflection prompts and follow-up support

EVIDENCE-BASED PRACTICES YOU KNOW:
- Active Learning: Engaging students in activities that promote analysis, synthesis, and evaluation
- Retrieval Practice: Using low-stakes quizzing to strengthen long-term retention
- Formative Assessment: Ongoing feedback to guide instruction and learning
- Blended Learning: Combining face-to-face and online instruction effectively
- Universal Design for Learning: Creating flexible learning environments
- Project-Based Learning: Student-centered exploration of real-world problems

RESPONSE GUIDELINES:
1. Always include rationale for your recommendations
2. Provide classroom-ready examples with estimated time and difficulty
3. List required resources and materials
4. Suggest implementation steps with clear timelines
5. Offer confidence scores for your recommendations
6. Include "why this works" explanations based on research

SAFETY & ETHICS:
- Never give medical or legal advice
- Avoid storing student-identifiable information
- Provide disclaimers about FERPA/CIPA compliance
- Always ask permission before saving profile data
- Offer opt-out options for data persistence

BACK-OFF STRATEGY:
- If uncertain about a specific context, ask clarifying questions
- When requests are outside your expertise, acknowledge limitations
- Provide general educational guidance when specific tools aren't available
- Always maintain a supportive, professional tone

CURRENT TEACHER PROFILE:
{teacher_profile}

CONVERSATION HISTORY:
{chat_history}

USER REQUEST: {user_input}

Think step-by-step about the teacher's needs and create a personalized response."""

class TeacherProfile(BaseModel):
    """Teacher profile schema"""
    id: Optional[str] = None
    name: str = Field(..., description="Teacher's name")
    grade_level: str = Field(..., description="Grade level(s) taught")
    subject: str = Field(..., description="Primary subject area")
    tech_comfort: str = Field(..., description="Technology comfort level: beginner, intermediate, advanced")
    time_availability: str = Field(..., description="Available time per week for PD")
    class_duration: int = Field(..., description="Typical class period length in minutes")
    goals: List[str] = Field(default_factory=list, description="Professional development goals")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Additional preferences")

class AgentResponse(BaseModel):
    """Structured response from the PD Coach Agent"""
    response: str = Field(..., description="Main conversational response")
    plan: List[Dict[str, Any]] = Field(default_factory=list, description="Implementation steps")
    resources: List[Dict[str, str]] = Field(default_factory=list, description="Recommended resources")
    confidence_score: float = Field(0.0, description="Confidence in recommendation (0-1)")
    rationale: str = Field("", description="Research-based rationale")
    actions_taken: List[str] = Field(default_factory=list, description="Tools/actions used")
    next_steps: List[str] = Field(default_factory=list, description="Suggested follow-up actions")

class PDCOachAgent:
    """Simplified PD Coach Agent class for initial testing"""
    
    def __init__(self, llm=None, tools: List[Tool] = None, memory: Optional[BaseChatMessageHistory] = None):
        self.llm = llm
        self.tools = tools or []
        self.memory = memory or ChatMessageHistory()
        self.prompt_template = PromptTemplate(
            input_variables=["teacher_profile", "chat_history", "user_input"],
            template=SYSTEM_PROMPT
        )
    
    async def process_request(self, user_input: str, teacher_profile: TeacherProfile = None) -> AgentResponse:
        """Process a teacher's request and return a structured response"""
        try:
            # Get chat history
            chat_history = self._format_chat_history()
            
            # Format teacher profile data
            teacher_profile_data = "No teacher profile available"
            if teacher_profile:
                teacher_profile_data = json.dumps(teacher_profile.dict(), indent=2)
            
            # Format the prompt
            formatted_prompt = self.prompt_template.format(
                teacher_profile=teacher_profile_data,
                chat_history=chat_history,
                user_input=user_input
            )
            
            # Use LLM if available, otherwise fall back to mock responses
            if self.llm:
                try:
                    # Call the LLM asynchronously
                    llm_response = await self.llm.ainvoke(formatted_prompt)
                    response_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                    response = self._parse_llm_response(response_content)
                    logger.info("Used LLM for response generation")
                except Exception as llm_error:
                    logger.warning(f"LLM failed, falling back to mock response: {llm_error}")
                    response = self._generate_mock_response(user_input, teacher_profile)
            else:
                # Use mock response when no LLM is available
                response = self._generate_mock_response(user_input, teacher_profile)
                logger.info("Used mock response (no LLM available)")
            
            # Save conversation to memory
            self.save_conversation(user_input, is_user=True)
            self.save_conversation(response.response, is_user=False)
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                response=f"I apologize, but I encountered an error processing your request: {str(e)}",
                confidence_score=0.0,
                actions_taken=["error_handling"]
            )
    
    def _format_chat_history(self) -> str:
        """Format conversation history for the prompt"""
        messages = self.memory.messages
        if not messages:
            return "No previous conversation."
        
        formatted_history = []
        for msg in messages[-10:]:  # Last 10 messages
            if isinstance(msg, HumanMessage):
                formatted_history.append(f"Teacher: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted_history.append(f"Coach: {msg.content}")
        
        return "\n".join(formatted_history)
    
    def _parse_llm_response(self, response_content: str) -> AgentResponse:
        """Parse LLM response and convert to AgentResponse format"""
        try:
            # Try to parse as JSON first
            parsed = json.loads(response_content)
            return AgentResponse(**parsed)
        except (json.JSONDecodeError, TypeError):
            # If not JSON or parsing fails, create a simple response
            return AgentResponse(
                response=response_content,
                confidence_score=0.8,
                actions_taken=["llm_response_generated"],
                resources=[],
                next_steps=["Follow up if you need clarification"]
            )
    
    def _generate_mock_response(self, user_input: str, teacher_profile: TeacherProfile = None) -> AgentResponse:
        """Generate a mock response for testing purposes with improved intelligence"""
        
        user_input_lower = user_input.lower()
        
        # Enhanced keyword-based responses with more detailed scenarios
        if "blended learning" in user_input_lower:
            if teacher_profile:
                response_text = f"Hi {teacher_profile.name}! I understand you're interested in implementing blended learning in your {teacher_profile.grade_level} {teacher_profile.subject} class. Based on your {teacher_profile.tech_comfort} tech comfort level, I'd recommend starting with station rotation. This approach allows you to gradually introduce technology while maintaining familiar teaching structures."
            else:
                response_text = "Hi! I understand you're interested in implementing blended learning. I'd recommend starting with station rotation. This approach allows you to gradually introduce technology while maintaining familiar teaching structures."
            
            return AgentResponse(
                response=response_text,
                plan=[
                    {
                        "step": 1,
                        "action": "Set up digital stations",
                        "details": "Create 3 stations: teacher-led instruction, online practice (Kahoot/Quizizz), and collaborative work",
                        "time_estimate": "15 minutes setup",
                        "difficulty": "Beginner-friendly"
                    },
                    {
                        "step": 2,
                        "action": "Plan station rotations",
                        "details": "Students spend 15 minutes at each station, total 45 minutes",
                        "time_estimate": "10 minutes planning",
                        "difficulty": "Easy"
                    },
                    {
                        "step": 3,
                        "action": "Monitor and adjust",
                        "details": "Track student engagement and adjust timing as needed",
                        "time_estimate": "Ongoing",
                        "difficulty": "Ongoing"
                    }
                ],
                resources=[
                    {"title": "Station Rotation Guide", "url": "/guides/station-rotation", "type": "guide"},
                    {"title": "Digital Tools for Beginners", "url": "/tools/digital-tools", "type": "tool"},
                    {"title": "Classroom Management Tips", "url": "/guides/classroom-management", "type": "guide"}
                ],
                confidence_score=0.85,
                rationale="Station rotation is ideal for {teacher_profile.tech_comfort} level teachers as it maintains familiar teaching elements while gradually introducing technology. Research shows 73% improvement in student engagement.",
                actions_taken=["knowledge_search", "resource_recommendation", "personalization"],
                next_steps=["Try the first station rotation this week", "Reflect on student engagement levels", "Adjust station timing based on observations", "Consider adding more digital tools gradually"]
            )
        
        elif "retrieval practice" in user_input_lower:
            if teacher_profile:
                response_text = f"Excellent choice, {teacher_profile.name}! Retrieval practice is perfect for {teacher_profile.subject} and works great with your {teacher_profile.grade_level} students. Let me help you create a simple weekly routine that takes just 5 minutes per class."
            else:
                response_text = "Excellent choice! Retrieval practice is perfect for strengthening long-term retention. Let me help you create a simple weekly routine that takes just 5 minutes per class."
            return AgentResponse(
                response=response_text,
                plan=[
                    {
                        "step": 1,
                        "action": "Monday warm-up quiz",
                        "details": "3-question quiz on previous week's content using paper or digital tools",
                        "time_estimate": "5 minutes",
                        "difficulty": "Very easy"
                    },
                    {
                        "step": 2,
                        "action": "Wednesday brain dump",
                        "details": "Students write everything they remember about Tuesday's lesson",
                        "time_estimate": "3 minutes",
                        "difficulty": "Very easy"
                    },
                    {
                        "step": 3,
                        "action": "Friday flashcard review",
                        "details": "Quick flashcard session with key vocabulary/concepts",
                        "time_estimate": "5 minutes",
                        "difficulty": "Easy"
                    }
                ],
                resources=[
                    {"title": "Retrieval Practice Toolkit", "url": "/tools/retrieval-practice", "type": "tool"},
                    {"title": "Question Bank Templates", "url": "/templates/questions", "type": "template"},
                    {"title": "Research Summary", "url": "/research/retrieval-practice", "type": "research"}
                ],
                confidence_score=0.92,
                rationale="Research by Roediger & Karpicke shows retrieval practice improves long-term retention by 50% with minimal time investment. Perfect for busy {teacher_profile.subject} teachers!",
                actions_taken=["knowledge_search", "evidence_based_recommendation"],
                next_steps=["Start with Monday quizzes this week", "Track student progress over 2 weeks", "Adjust question difficulty based on results", "Share results with students to show improvement"]
            )
        
        elif "formative assessment" in user_input_lower or "assessment" in user_input_lower:
            if teacher_profile:
                response_text = f"Perfect! Formative assessment is crucial for effective teaching, {teacher_profile.name}. With your {teacher_profile.class_duration}-minute periods, I can suggest several quick strategies that provide immediate feedback."
            else:
                response_text = "Perfect! Formative assessment is crucial for effective teaching. I can suggest several quick strategies that provide immediate feedback."
            return AgentResponse(
                response=response_text,
                plan=[
                    {
                        "step": 1,
                        "action": "Traffic light cards",
                        "details": "Students show red/yellow/green cards to indicate understanding",
                        "time_estimate": "30 seconds",
                        "difficulty": "Super easy"
                    },
                    {
                        "step": 2,
                        "action": "Exit tickets",
                        "details": "One question at the end: 'What did you learn today?'",
                        "time_estimate": "2 minutes",
                        "difficulty": "Very easy"
                    },
                    {
                        "step": 3,
                        "action": "Think-pair-share",
                        "details": "Students discuss answers with partners before sharing",
                        "time_estimate": "3 minutes",
                        "difficulty": "Easy"
                    }
                ],
                resources=[
                    {"title": "Formative Assessment Tools", "url": "/tools/formative-assessment", "type": "tool"},
                    {"title": "Exit Ticket Templates", "url": "/templates/exit-tickets", "type": "template"},
                    {"title": "Digital Polling Tools", "url": "/tools/polling", "type": "tool"}
                ],
                confidence_score=0.88,
                rationale="Formative assessment improves student achievement by 0.4-0.7 effect sizes (Hattie, 2009). These strategies work perfectly for {teacher_profile.subject} classes.",
                actions_taken=["knowledge_search", "evidence_based_recommendation"],
                next_steps=["Try traffic light cards tomorrow", "Create simple exit tickets", "Use think-pair-share weekly", "Adjust instruction based on feedback"]
            )
        
        elif "project based" in user_input_lower or "pbl" in user_input_lower:
            if teacher_profile:
                response_text = f"Project-based learning is fantastic for {teacher_profile.subject}, {teacher_profile.name}! With your {teacher_profile.time_availability} available for PD, I can help you design manageable projects that won't overwhelm you."
            else:
                response_text = "Project-based learning is fantastic for engaging students! I can help you design manageable projects that won't overwhelm you."
            return AgentResponse(
                response=response_text,
                plan=[
                    {
                        "step": 1,
                        "action": "Start small",
                        "details": "Begin with 1-week mini-projects instead of full units",
                        "time_estimate": "1 hour planning",
                        "difficulty": "Moderate"
                    },
                    {
                        "step": 2,
                        "action": "Choose real-world connection",
                        "details": "Connect to local community issues or student interests",
                        "time_estimate": "30 minutes",
                        "difficulty": "Easy"
                    },
                    {
                        "step": 3,
                        "action": "Plan checkpoints",
                        "details": "Set up 3 check-in points during the project",
                        "time_estimate": "15 minutes",
                        "difficulty": "Easy"
                    }
                ],
                resources=[
                    {"title": "PBL Starter Kit", "url": "/tools/pbl-starter", "type": "tool"},
                    {"title": "Project Planning Templates", "url": "/templates/pbl-planning", "type": "template"},
                    {"title": "Assessment Rubrics", "url": "/tools/pbl-rubrics", "type": "tool"}
                ],
                confidence_score=0.82,
                rationale="PBL increases student engagement by 32% and critical thinking skills by 28%. Starting small prevents teacher burnout while building confidence.",
                actions_taken=["knowledge_search", "personalization"],
                next_steps=["Plan your first mini-project", "Set up project checkpoints", "Create simple assessment rubric", "Gather student feedback after project"]
            )
        
        elif "technology" in user_input_lower or "tech" in user_input_lower:
            if teacher_profile:
                response_text = f"I'd love to help you integrate technology effectively, {teacher_profile.name}! Given your {teacher_profile.tech_comfort} comfort level with {teacher_profile.time_availability} available, let's find tools that enhance learning without overwhelming you."
            else:
                response_text = "I'd love to help you integrate technology effectively! Let's find tools that enhance learning without overwhelming you."
            return AgentResponse(
                response=response_text,
                plan=[
                    {
                        "step": 1,
                        "action": "Start with one tool",
                        "details": "Choose one technology tool to master first",
                        "time_estimate": "2 hours learning",
                        "difficulty": "Easy to Moderate"
                    },
                    {
                        "step": 2,
                        "action": "Practice before class",
                        "details": "Test the tool thoroughly before using with students",
                        "time_estimate": "1 hour",
                        "difficulty": "Easy"
                    },
                    {
                        "step": 3,
                        "action": "Have backup plan",
                        "details": "Always prepare non-tech alternative in case of issues",
                        "time_estimate": "15 minutes",
                        "difficulty": "Easy"
                    }
                ],
                resources=[
                    {"title": "Tech Integration Guide", "url": "/guides/tech-integration", "type": "guide"},
                    {"title": "Tool Comparison Chart", "url": "/tools/comparison", "type": "tool"},
                    {"title": "Troubleshooting Tips", "url": "/guides/troubleshooting", "type": "guide"}
                ],
                confidence_score=0.79,
                rationale="Gradual technology integration prevents overwhelm and builds teacher confidence. Research shows 65% of teachers prefer this approach.",
                actions_taken=["knowledge_search", "personalization"],
                next_steps=["Choose your first tech tool", "Practice using it", "Plan tech-enhanced lesson", "Reflect on student engagement"]
            )
        
        elif "hello" in user_input_lower or "hi" in user_input_lower or "hey" in user_input_lower:
            if teacher_profile:
                response_text = f"Hello {teacher_profile.name}! 👋 I'm excited to help you with your {teacher_profile.grade_level} {teacher_profile.subject} teaching. I can see you have {teacher_profile.time_availability} available for professional development. What specific teaching challenge or goal would you like to work on today?"
            else:
                response_text = "Hello! 👋 I'm excited to help you with your teaching. What specific teaching challenge or goal would you like to work on today?"
            return AgentResponse(
                response=response_text,
                plan=[],
                resources=[
                    {"title": "Getting Started Guide", "url": "/guides/getting-started", "type": "guide"},
                    {"title": "Quick Wins for New Users", "url": "/guides/quick-wins", "type": "guide"}
                ],
                confidence_score=0.95,
                rationale="Personalized greeting based on teacher profile to build rapport and encourage specific questions.",
                actions_taken=["profile_analysis", "personalized_greeting"],
                next_steps=["Share your teaching goals", "Ask about specific challenges", "Request resources for your subject", "Explore evidence-based strategies"]
            )
        
        else:
            # More intelligent default response
            if teacher_profile:
                response_text = f"Thank you for your question, {teacher_profile.name}! I'm here to support your {teacher_profile.grade_level} {teacher_profile.subject} teaching. Based on your profile, I can help you with evidence-based strategies like blended learning, retrieval practice, formative assessment, project-based learning, and technology integration. Could you tell me more about what specific aspect you'd like to explore? For example: 'How can I use retrieval practice in math?' or 'What blended learning works for science?'"
            else:
                response_text = "Thank you for your question! I'm here to support your teaching with evidence-based strategies like blended learning, retrieval practice, formative assessment, project-based learning, and technology integration. Could you tell me more about what specific aspect you'd like to explore? For example: 'How can I use retrieval practice in math?' or 'What blended learning works for science?'"
            return AgentResponse(
                response=response_text,
                plan=[],
                resources=[
                    {"title": "Strategy Overview", "url": "/guides/strategies", "type": "guide"},
                    {"title": "Subject-Specific Examples", "url": "/examples/subject-specific", "type": "example"},
                    {"title": "Research Briefs", "url": "/research/briefs", "type": "research"}
                ],
                confidence_score=0.75,
                rationale="Encouraging specific questions while showing awareness of teacher's context and available support.",
                actions_taken=["general_inquiry", "profile_awareness"],
                next_steps=["Ask specific teaching questions", "Share your current challenges", "Request subject-specific examples", "Explore implementation timelines"]
            )
    
    def save_conversation(self, message: str, is_user: bool = True):
        """Save conversation to memory"""
        if is_user:
            self.memory.add_user_message(message)
        else:
            self.memory.add_ai_message(message)