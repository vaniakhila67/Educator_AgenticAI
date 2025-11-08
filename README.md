# Agentic AI Professional Development Coach

An intelligent coaching system that helps educators adopt innovative pedagogies and integrate educational technologies through personalized recommendations, resource provision, and guided coaching sequences.

## 🎯 Features

- **Personalized Coaching**: Tailored recommendations based on teacher profile (subject, grade, tech comfort, time availability)
- **Multi-Step Interventions**: Plans workshops → provides micro-tasks → follows up with reflection prompts
- **Evidence-Based Practices**: Grounded in educational research (active learning, retrieval practice, formative assessment)
- **Resource Library**: Lesson templates, rubrics, slide decks, and tool recommendations
- **Interactive Chat**: Dynamic conversational interface for real-time coaching
- **Lesson Plan Generator**: Create customized lesson plans with technology integration
- **Workshop Planning**: Personalized professional development workshop recommendations
- **Export Options**: Google Docs and PowerPoint export capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   LangChain     │
│   Frontend      │◄──►│   Backend       │◄──►│   Agent         │
│                 │    │                 │    │   System        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Session       │    │   API           │    │   Tools         │
│   Management    │    │   Endpoints     │    │   (6 tools)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional)
- OpenAI API key (or other LLM provider)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd educator-agentic-ai
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the system**
   ```bash
   # Start backend
   python -m app.api.main
   
   # In another terminal, start frontend
   streamlit run frontend/app.py
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the applications**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📊 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_comprehensive.py -v

# Run with coverage
pytest tests/test_comprehensive.py --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_comprehensive.py::TestTools -v  # Unit tests
pytest tests/test_comprehensive.py::TestAPI -v      # API tests
pytest tests/test_comprehensive.py::TestEndToEnd -v # E2E tests
```

## 🔧 Configuration

### Environment Variables

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Memory Configuration
ENABLE_LONG_TERM_MEMORY=true
VECTOR_DB_TYPE=faiss
MEMORY_RETENTION_DAYS=90

# Safety Configuration
ENABLE_PII_DETECTION=true
ENABLE_CONTENT_FILTERING=true
MAX_AGENT_ITERATIONS=3
```

### Tool Configuration

The system includes 6 core tools:

1. **knowledge_search**: Search pedagogical knowledge base
2. **fetch_resource**: Get educational resources and tools
3. **generate_lesson_plan**: Create customized lesson plans
4. **save_profile**: Save teacher profile data
5. **load_profile**: Retrieve teacher profile data
6. **schedule_workshop**: Plan professional development workshops

## 📈 Evaluation Metrics

The system tracks several key metrics:

- **Personalization Score**: How well recommendations match teacher profile (0-1)
- **Pedagogical Alignment**: Presence of evidence-based practices (0-1)
- **Resource Validity**: Accessibility and relevance of recommended resources (0-1)
- **User Satisfaction**: Teacher feedback and ratings (0-1)

Run evaluation:
```bash
python -m app.evaluation.run_evaluation
```

## 🔒 Safety & Privacy

- **PII Detection**: Automatically detects and handles personal information
- **Content Filtering**: Filters inappropriate content and requests
- **Data Encryption**: Encrypts sensitive data at rest
- **Consent Management**: Explicit opt-in for data storage
- **Right to be Forgotten**: Complete profile deletion capability
- **FERPA/CIPA Compliance**: Follows educational privacy regulations

## 🛠️ Extension Points

### Adding New Tools

1. Create tool function in `app/tools/tools.py`
2. Define input/output schemas with Pydantic
3. Register tool in `create_tools()` function
4. Update agent prompt if needed

### Adding New Resources

1. Add to knowledge base in `sample_data/knowledge_base.json`
2. Update workshops/tools in `sample_data/workshops_tools.json`
3. Regenerate embeddings if using vector search

### Customizing Agent Behavior

1. Modify system prompt in `app/agents/pd_coach_agent.py`
2. Update few-shot examples
3. Adjust tool selection logic
4. Configure memory settings

## 📚 Sample Interactions

### Example 1: Blended Learning Inquiry
**Teacher**: "I want to implement blended learning in my 6th grade science class. What would be a good starting point?"

**Agent Response**: 
- Explains blended learning fundamentals
- Recommends specific tools (Padlet, Google Classroom)
- Suggests workshop attendance
- Provides next steps for implementation
- Includes confidence score and rationale

### Example 2: Lesson Plan Generation
**Teacher**: "Help me create a 45-minute lesson about food chains using technology"

**Agent Response**:
- Generates complete lesson plan with steps
- Integrates recommended technology tools
- Provides materials list and assessment
- Includes prep time and difficulty level
- Offers export options

### Example 3: Assessment Strategy
**Teacher**: "My students struggle with remembering formulas. How can I help them?"

**Agent Response**:
- Explains retrieval practice benefits
- Provides specific routine examples
- Suggests assessment strategies
- Recommends relevant workshops
- Includes implementation timeline

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [FAQ](docs/FAQ.md)
- Review the [troubleshooting guide](docs/TROUBLESHOOTING.md)

## 🏆 Acknowledgments

- Built with [LangChain](https://langchain.com/) for agent orchestration
- Frontend powered by [Streamlit](https://streamlit.io/)
- Backend API using [FastAPI](https://fastapi.tiangolo.com/)
- Educational research from multiple pedagogical sources

---

**⭐ Star this repository if you find it helpful!**