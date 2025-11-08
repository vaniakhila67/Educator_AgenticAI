"""
Sample data for PD Coach Agent testing and demonstration
"""

# Sample teacher profiles for testing
SAMPLE_TEACHER_PROFILES = [
    {
        "id": "teacher_001",
        "name": "Sarah Johnson",
        "grade_level": "6",
        "subject": "Science",
        "tech_comfort": "intermediate",
        "time_availability": "2 hours per week",
        "class_duration": 45,
        "goals": ["Implement blended learning", "Integrate educational technology"],
        "preferences": {"notes": "Prefers hands-on activities and collaborative learning"}
    },
    {
        "id": "teacher_002", 
        "name": "Michael Chen",
        "grade_level": "9-10",
        "subject": "Mathematics",
        "tech_comfort": "advanced",
        "time_availability": "3 hours per week",
        "class_duration": 50,
        "goals": ["Improve assessment techniques", "Build retrieval practice routines"],
        "preferences": {"notes": "Interested in gamification and interactive tools"}
    },
    {
        "id": "teacher_003",
        "name": "Emily Rodriguez",
        "grade_level": "K-2",
        "subject": "Elementary",
        "tech_comfort": "beginner",
        "time_availability": "1 hour per week",
        "class_duration": 30,
        "goals": ["Enhance student engagement", "Differentiate instruction"],
        "preferences": {"notes": "Needs simple, age-appropriate tools and activities"}
    }
]

# Sample workshops and tools data
SAMPLE_WORKSHOPS_TOOLS = [
    {
        "id": "workshop_001",
        "title": "Blended Learning Fundamentals",
        "type": "workshop",
        "description": "Learn to integrate online and face-to-face instruction effectively",
        "duration_minutes": 120,
        "difficulty": "beginner",
        "grade_levels": ["3-12"],
        "subjects": ["All"],
        "tech_requirements": ["Basic computer skills", "Learning management system access"],
        "learning_outcomes": [
            "Understand blended learning models",
            "Design effective hybrid lessons",
            "Select appropriate digital tools"
        ],
        "url": "https://example.com/blended-learning-workshop",
        "evidence_based_practices": ["active_learning", "differentiated_instruction"]
    },
    {
        "id": "tool_001",
        "title": "Padlet",
        "type": "tool",
        "description": "Collaborative digital bulletin board for student engagement",
        "category": "collaboration",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "tech_level": "beginner",
        "setup_time": "5 minutes",
        "cost": "freemium",
        "url": "https://padlet.com",
        "tutorial_url": "https://padlet.com/tutorials",
        "evidence_based_practices": ["collaborative_learning", "formative_assessment"]
    },
    {
        "id": "workshop_002",
        "title": "Retrieval Practice Strategies",
        "type": "workshop",
        "description": "Master evidence-based techniques for improving long-term retention",
        "duration_minutes": 90,
        "difficulty": "intermediate",
        "grade_levels": ["6-12"],
        "subjects": ["All"],
        "tech_requirements": ["Basic presentation tools"],
        "learning_outcomes": [
            "Understand cognitive science behind retrieval practice",
            "Implement spaced repetition techniques",
            "Design effective retrieval activities"
        ],
        "url": "https://example.com/retrieval-practice-workshop",
        "evidence_based_practices": ["retrieval_practice", "spaced_repetition"]
    },
    {
        "id": "tool_002",
        "title": "Kahoot!",
        "type": "tool",
        "description": "Game-based learning platform for formative assessment",
        "category": "assessment",
        "grade_levels": ["K-12"],
        "subjects": ["All"],
        "tech_level": "beginner",
        "setup_time": "10 minutes",
        "cost": "freemium",
        "url": "https://kahoot.com",
        "tutorial_url": "https://kahoot.com/academy",
        "evidence_based_practices": ["formative_assessment", "gamification"]
    },
    {
        "id": "workshop_003",
        "title": "Formative Assessment with Technology",
        "type": "workshop",
        "description": "Use digital tools to monitor student understanding in real-time",
        "duration_minutes": 105,
        "difficulty": "intermediate",
        "grade_levels": ["3-12"],
        "subjects": ["All"],
        "tech_requirements": ["Tablet or laptop", "Internet access"],
        "learning_outcomes": [
            "Select appropriate formative assessment tools",
            "Interpret real-time data",
            "Adjust instruction based on feedback"
        ],
        "url": "https://example.com/formative-assessment-workshop",
        "evidence_based_practices": ["formative_assessment", "data_driven_instruction"]
    }
]

# Sample lesson plans
SAMPLE_LESSON_PLANS = [
    {
        "id": "lesson_001",
        "title": "Introduction to Food Chains",
        "grade": "6",
        "subject": "Science",
        "duration_minutes": 45,
        "objective": "Students will understand how energy flows through food chains and identify producers, consumers, and decomposers",
        "technology": ["Padlet"],
        "difficulty_level": "beginner",
        "estimated_prep_time": 15,
        "steps": [
            {
                "time": 5,
                "activity": "Warm-up: Students brainstorm what they ate for breakfast",
                "materials": ["Whiteboard"]
            },
            {
                "time": 10,
                "activity": "Direct instruction: Introduce food chain vocabulary",
                "materials": ["Projector", "Vocabulary cards"]
            },
            {
                "time": 15,
                "activity": "Collaborative activity: Create food chains on Padlet",
                "materials": ["Tablets/computers", "Padlet access"]
            },
            {
                "time": 10,
                "activity": "Gallery walk: Students review and comment on peer work",
                "materials": ["Padlet posts"]
            },
            {
                "time": 5,
                "activity": "Exit ticket: Draw and label a food chain",
                "materials": ["Exit ticket template"]
            }
        ],
        "materials": ["Projector", "Vocabulary cards", "Tablets/computers", "Exit ticket template"],
        "assessment": "Students create accurate food chains and correctly identify energy flow direction",
        "evidence_based_practices": ["collaborative_learning", "formative_assessment"]
    },
    {
        "id": "lesson_002",
        "title": "Quadratic Functions in Real Life",
        "grade": "9",
        "subject": "Mathematics",
        "duration_minutes": 50,
        "objective": "Students will model real-world scenarios using quadratic functions and interpret key features",
        "technology": ["PhET Simulations", "Google Docs"],
        "difficulty_level": "intermediate",
        "estimated_prep_time": 20,
        "steps": [
            {
                "time": 5,
                "activity": "Hook: Show video of basketball trajectory",
                "materials": ["Video", "Projector"]
            },
            {
                "time": 15,
                "activity": "Explore: Use PhET simulation to investigate projectile motion",
                "materials": ["Computers", "PhET access"]
            },
            {
                "time": 20,
                "activity": "Apply: Students model their own scenarios in Google Docs",
                "materials": ["Chromebooks", "Google Docs"]
            },
            {
                "time": 8,
                "activity": "Share: Groups present their models",
                "materials": ["Projector"]
            },
            {
                "time": 2,
                "activity": "Reflect: Quick poll on learning confidence",
                "materials": ["Kahoot!"]
            }
        ],
        "materials": ["Video", "Projector", "Computers", "Chromebooks", "PhET access", "Google Docs"],
        "assessment": "Students create accurate quadratic models and explain key features",
        "evidence_based_practices": ["active_learning", "formative_assessment"]
    }
]

# Sample knowledge base entries
SAMPLE_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "topic": "Blended Learning",
        "title": "The Four Models of Blended Learning",
        "content": "Blended learning combines online and face-to-face instruction. The four main models are: Rotation Model, Flex Model, A La Carte Model, and Enriched Virtual Model. Each offers different approaches to integrating digital content with traditional classroom instruction.",
        "evidence_level": "high",
        "research_citations": ["Horn & Staker, 2015", "Christensen Institute, 2020"],
        "practical_applications": [
            "Use rotation model for differentiated instruction",
            "Implement flex model for personalized pacing",
            "Apply enriched virtual for homework extensions"
        ]
    },
    {
        "id": "kb_002",
        "topic": "Retrieval Practice",
        "title": "The Power of Retrieval Practice in Learning",
        "content": "Retrieval practice involves actively recalling information from memory, strengthening neural pathways and improving long-term retention. This technique is more effective than passive review or re-reading.",
        "evidence_level": "high",
        "research_citations": ["Roediger & Karpicke, 2006", "Agarwal & Bain, 2019"],
        "practical_applications": [
            "Use low-stakes quizzes regularly",
            "Implement brain dumps at lesson end",
            "Practice spaced repetition schedules"
        ]
    },
    {
        "id": "kb_003",
        "topic": "Formative Assessment",
        "title": "Real-Time Feedback for Learning",
        "content": "Formative assessment provides ongoing feedback during the learning process, allowing teachers to adjust instruction and students to improve understanding. It's most effective when used frequently and acted upon immediately.",
        "evidence_level": "high",
        "research_citations": ["Black & Wiliam, 1998", "Hattie, 2009"],
        "practical_applications": [
            "Use exit tickets daily",
            "Implement think-pair-share activities",
            "Apply traffic light feedback systems"
        ]
    }
]

# Sample test scenarios
SAMPLE_TEST_SCENARIOS = [
    {
        "name": "Blended Learning Inquiry",
        "teacher_profile": "teacher_001",
        "user_input": "I want to implement blended learning in my 6th grade science class. What would be a good starting point?",
        "expected_intent": "blended_learning_implementation",
        "expected_tools": ["knowledge_search", "fetch_resource"],
        "expected_outcomes": [
            "Provides blended learning overview",
            "Suggests specific tools (like Padlet)",
            "Recommends workshop participation",
            "Offers next steps for implementation"
        ]
    },
    {
        "name": "Retrieval Practice Request",
        "teacher_profile": "teacher_002",
        "user_input": "My math students struggle to remember formulas. Can you help me build retrieval practice routines?",
        "expected_intent": "retrieval_practice_implementation",
        "expected_tools": ["knowledge_search", "generate_lesson_plan"],
        "expected_outcomes": [
            "Explains retrieval practice benefits",
            "Provides specific routine examples",
            "Suggests assessment strategies",
            "Includes confidence-building elements"
        ]
    },
    {
        "name": "Technology Integration Help",
        "teacher_profile": "teacher_003",
        "user_input": "I need simple tools for my kindergarten class. What would work for basic assessment?",
        "expected_intent": "technology_integration_assistance",
        "expected_tools": ["fetch_resource", "generate_lesson_plan"],
        "expected_outcomes": [
            "Recommends age-appropriate tools",
            "Considers teacher's beginner tech level",
            "Provides simple implementation steps",
            "Offers safety and privacy guidance"
        ]
    }
]

def export_sample_data():
    """Export sample data to JSON files for testing"""
    import json
    import os
    
    # Create sample_data directory if it doesn't exist
    os.makedirs("sample_data", exist_ok=True)
    
    # Export teacher profiles
    with open("sample_data/teacher_profiles.json", "w") as f:
        json.dump(SAMPLE_TEACHER_PROFILES, f, indent=2)
    
    # Export workshops and tools
    with open("sample_data/workshops_tools.json", "w") as f:
        json.dump(SAMPLE_WORKSHOPS_TOOLS, f, indent=2)
    
    # Export lesson plans
    with open("sample_data/lesson_plans.json", "w") as f:
        json.dump(SAMPLE_LESSON_PLANS, f, indent=2)
    
    # Export knowledge base
    with open("sample_data/knowledge_base.json", "w") as f:
        json.dump(SAMPLE_KNOWLEDGE_BASE, f, indent=2)
    
    # Export test scenarios
    with open("sample_data/test_scenarios.json", "w") as f:
        json.dump(SAMPLE_TEST_SCENARIOS, f, indent=2)
    
    print("Sample data exported successfully!")

if __name__ == "__main__":
    export_sample_data()