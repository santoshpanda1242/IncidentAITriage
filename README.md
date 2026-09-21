# Incident Triage System

An intelligent incident resolution system that integrates MySQL data, ChromaDB vector search, and Ollama LLM to provide automated incident troubleshooting suggestions.

## Architecture

```
Incident Event → MySQL Data → Context Fusion → ChromaDB Search → Ollama LLM → Structured Solution
```

## Features

- **MySQL Integration**: Query incident data and error logs
- **Vector Search**: Semantic search using ChromaDB and Ollama embeddings
- **LLM Synthesis**: Generate human-readable solutions using qwen2.5-coder
- **Knowledge Base**: Comprehensive troubleshooting guides for common issues
- **Interactive & Demo Modes**: Flexible operation modes

## Prerequisites

1. **Python 3.9+**
2. **Ollama** with required models:
   ```bash
   ollama pull nomic-embed-text
   ollama pull qwen2.5-coder
   ```
3. **MySQL Workbench** (optional, for real database connection)
4. **Python dependencies** (see requirements.txt)

## Installation

1. **Clone/Setup the project**:
   ```bash
   cd incident-triage
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

## Project Structure

```
incident-triage/
├── src/
│   ├── __init__.py
│   ├── database_mocks.py      # MySQL connection and data handling
│   ├── context_fusion.py       # Merge data for search
│   ├── vector_store.py         # ChromaDB integration
│   └── synthesis.py            # Ollama LLM integration
├── kb/                         # Knowledge base documents
│   ├── payment-service-troubleshooting.md
│   ├── authentication-service-guide.md
│   └── ... (10+ KB articles)
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
└── README.md                   # This file
```

## Usage

### Run the Application

```bash
python main.py
```

### Available Modes

1. **Demo Mode**: Process sample incidents
2. **Interactive Mode**: Enter custom incidents
3. **Quick Test**: Single incident processing

### Example Usage

```python
# Programmatic usage
from src.database_mocks import DatabaseManager
from src.context_fusion import ContextFusionBuilder
from src.vector_store import KnowledgeBaseManager
from src.synthesis import IncidentSolutionGenerator

# Initialize components
db_manager = DatabaseManager()
kb_manager = KnowledgeBaseManager()
kb_manager.initialize_knowledge_base()
solution_generator = IncidentSolutionGenerator()

# Process an incident
incident_context = db_manager.get_incident_context('payment-service')
kb_results = kb_manager.search_knowledge_base('database timeout')
solution = solution_generator.generate_solution(incident_context, kb_results)
```

## Components

### Database Manager
- Connects to MySQL for incident data
- Provides mock data for development
- Handles error logs and service profiles

### Context Fusion Builder
- Merges data from multiple sources
- Creates unified context for search
- Supports multiple fusion templates

### Vector Store (ChromaDB)
- Stores KB article embeddings
- Performs semantic similarity search
- Uses Ollama nomic-embed-text model

### LLM Synthesis (Ollama)
- Generates human-readable solutions
- Uses qwen2.5-coder for technical tasks
- Structured output formatting

## Configuration

### Environment Variables

- `MYSQL_HOST`: MySQL server host (default: localhost)
- `MYSQL_USER`: MySQL username (default: root)
- `MYSQL_PASSWORD`: MySQL password (default: empty)
- `MYSQL_DATABASE`: Database name (default: incident_logs)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)

### MySQL Setup

To use real MySQL data, run the provided setup script:

```bash
# In MySQL Workbench, execute: mysql_setup.sql
```

## Development

### Adding New KB Articles

1. Create markdown files in the `kb/` directory
2. Run the application to automatically ingest them
3. Or use the API directly:

```python
kb_manager.initialize_knowledge_base(force_reingest=True)
```

### Testing Components

```python
# Test database connection
db_manager = DatabaseManager()

# Test vector search
kb_manager = KnowledgeBaseManager()
results = kb_manager.search_knowledge_base("database timeout")

# Test LLM
solution_generator = IncidentSolutionGenerator()
solution_generator.synthesizer.test_connection()
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check model installation: `ollama list`
- Verify base URL configuration

### ChromaDB Issues
- Check directory permissions for `chroma_db/`
- Ensure sufficient disk space
- Delete `chroma_db/` to reset

### MySQL Connection Issues
- Verify MySQL Workbench is running
- Check credentials in `.env`
- Ensure database exists

## Future Enhancements

- [ ] Web interface for incident submission
- [ ] Real-time incident monitoring
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Integration with incident management tools

## License

This project is for educational and development purposes.

## Contributing

This is a demonstration project for learning RAG systems and incident management automation.