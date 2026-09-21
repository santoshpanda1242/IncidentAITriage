# Incident Triage System - Interview Guide

## Project Overview

**Project Name:** AI-Powered Incident Triage System with RAG

**Project Type:** Full-stack AI application for automated incident resolution

**Duration:** Development project focused on integrating AI with enterprise incident management

**Problem Solved:** Automated the process of triaging and resolving technical incidents by combining structured data (MySQL) with unstructured knowledge base (KB) articles and AI-powered synthesis.

---

## What I Built

### System Architecture

I built a complete incident triage system that:

1. **Ingests structured incident data** from MySQL database (services, error logs, incidents)
2. **Processes unstructured knowledge** from markdown-based troubleshooting guides
3. **Performs semantic search** using vector embeddings to find relevant KB articles
4. **Generates human-readable solutions** using local LLM (Ollama)
5. **Provides web-based chatbot interface** for user interaction

### Key Features Implemented

- ✅ **Real-time incident processing** with MySQL integration
- ✅ **Semantic search** using ChromaDB vector database
- ✅ **Local AI processing** using Ollama (no external API costs)
- ✅ **Knowledge base management** with automatic chunking and embedding
- ✅ **Web-based chatbot UI** with Flask
- ✅ **Smart initialization** to avoid redundant processing
- ✅ **Fallback mechanisms** for robustness

---

## Technologies Used

### Backend Technologies

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Python 3.9+** | Primary development language | Rich AI/ML ecosystem |
| **Flask** | Web framework | Lightweight, easy to deploy |
| **MySQL** | Relational database | Structured incident data storage |
| **ChromaDB** | Vector database | Local semantic search |
| **Ollama** | Local LLM runtime | No API costs, privacy-focused |
| **LangChain** | AI framework | Simplified LLM integration |

### AI/ML Technologies

| Technology | Purpose | Model Used |
|------------|---------|------------|
| **nomic-embed-text** | Text embeddings | Converts text to 768-dimensional vectors |
| **qwen2.5** | Large Language Model | Generates incident solutions |
| **ChromaDB** | Vector similarity search | Finds semantically similar KB articles |

### Libraries & Frameworks

| Library | Purpose |
|---------|---------|
| **mysql-connector-python** | MySQL database connectivity |
| **langchain-ollama** | Ollama integration with LangChain |
| **langchain-community** | Community LangChain integrations |
| **langchain-core** | Core LangChain abstractions |
| **langchain-text-splitters** | Text chunking for embeddings |
| **python-dotenv** | Environment variable management |

### Development Tools

- **Git** - Version control
- **MySQL Workbench** - Database management
- **VS Code / Windsurf** - IDE
- **PowerShell** - Terminal and command execution

---

## Technical Concepts Explained

### 1. RAG (Retrieval-Augmented Generation)

**What is RAG?**

RAG is a technique that combines:
1. **Retrieval** - Finding relevant information from a knowledge base
2. **Augmentation** - Adding that information to the AI's context
3. **Generation** - Using the AI to generate a response based on retrieved information

**How RAG Works in My Project:**

```
User Question → Vector Search → Relevant KB Articles → LLM → Structured Answer
```

**Step-by-Step Implementation:**

1. **User Query:** "Payment service database timeout"
   
2. **Context Building:** 
   - Fetch error logs from MySQL for payment-service
   - Build search query from incident context

3. **Retrieval (Vector Search):**
   - Convert query to vector using nomic-embed-text
   - Search ChromaDB for semantically similar KB articles
   - Retrieve top 3 most relevant articles

4. **Augmentation:**
   - Combine incident context + retrieved KB articles
   - Format as prompt for LLM

5. **Generation:**
   - Send augmented prompt to qwen2.5 LLM
   - LLM generates structured resolution guide
   - Return human-readable solution

**Why RAG is Important:**

- **Accuracy:** LLM has access to specific, relevant information
- **Reduced Hallucinations:** LLM relies on retrieved facts, not just training data
- **Up-to-date:** Knowledge base can be updated without retraining LLM
- **Explainable:** Can show which KB articles were used

**Example from My Project:**

```python
# Retrieval
kb_results = vector_store.similarity_search("database timeout", n_results=3)

# Augmentation
prompt = f"""
Incident: {incident_context}
Relevant KB Articles: {kb_results}
Generate solution:
"""

# Generation
solution = llm.invoke(prompt)
```

---

### 2. Vector Embeddings

**What are Vector Embeddings?**

Vector embeddings are numerical representations of text that capture semantic meaning. Instead of text being stored as words, it's converted into a list of numbers (vectors) where similar meanings have similar number patterns.

**How They Work:**

```
Text: "database connection timeout"
↓ (Embedding Model)
Vector: [0.123, -0.456, 0.789, 0.234, ...] (768 numbers)
```

**Why 768 Dimensions?**

The nomic-embed-text model creates 768-dimensional vectors, meaning each piece of text is represented by 768 numbers. Each dimension captures a different aspect of meaning.

**How Similarity Works:**

- "database timeout" → Vector A
- "SQL connection issues" → Vector B
- "cat videos" → Vector C

**Mathematical Similarity:**
- Vector A and B are **close** (similar meaning)
- Vector A and C are **far apart** (different meaning)

**How I Used It:**

```python
from langchain_ollama import OllamaEmbeddings

# Initialize embedding model
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Convert text to vector
query_vector = embeddings.embed_query("database timeout")
# Result: [0.123, -0.456, 0.789, ...]

# Search similar vectors
results = chroma_db.query(query_embeddings=[query_vector])
```

---

### 3. Vector Databases (ChromaDB)

**What is a Vector Database?**

A vector database is specialized for storing and searching vector embeddings efficiently. Unlike traditional databases that search by exact matches, vector databases search by semantic similarity.

**Why Not Traditional Database?**

| Traditional Database | Vector Database |
|---------------------|-----------------|
| Exact keyword match | Semantic similarity match |
| "database" matches "database" | "database timeout" matches "SQL connection issues" |
| No understanding of meaning | Understands relationships between concepts |

**How ChromaDB Works in My Project:**

1. **Storage:**
   - Stores both text and its vector embedding
   - Organized in collections (like tables)
   - Persisted locally in `chroma_db/` directory

2. **Ingestion:**
   ```python
   # Split KB articles into chunks
   chunks = text_splitter.split_documents(kb_articles)
   
   # Generate embeddings
   embeddings = ollama_embeddings.embed_documents([chunk.text for chunk in chunks])
   
   # Store in ChromaDB
   chroma_db.add(documents=chunks, embeddings=embeddings)
   ```

3. **Search:**
   ```python
   # Convert query to vector
   query_vector = embeddings.embed_query(user_query)
   
   # Find similar vectors
   results = chroma_db.query(query_embeddings=[query_vector], n_results=3)
   ```

**Why I Chose ChromaDB:**

- **Local deployment** - No external API needed
- **Python-native** - Easy integration
- **Open-source** - Free to use
- **Good performance** - Sufficient for our scale

---

### 4. Text Chunking

**What is Text Chunking?**

Text chunking is breaking long documents into smaller segments (chunks) for better embedding and retrieval.

**Why Chunking is Necessary:**

1. **Model Limits:** Embedding models have maximum input length
2. **Precision:** Smaller chunks allow more precise matching
3. **Efficiency:** Faster embedding generation
4. **Flexibility:** Can retrieve specific relevant sections

**How I Implemented It:**

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 500 characters per chunk
    chunk_overlap=50,    # 50 characters overlap between chunks
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Try paragraphs first, then sentences
)

# Split KB article into chunks
chunks = text_splitter.split_documents([kb_article])
# Result: 375 chunks from 12 KB articles
```

**Example:**

**Original:**
```
# Payment Service Troubleshooting

## Database Issues
If you encounter database timeouts, check connection pool settings...
[500 more characters]

## API Issues
For API rate limits, implement retry logic...
```

**Chunks:**
```
Chunk 1: "# Payment Service Troubleshooting\n\n## Database Issues\nIf you encounter..."
Chunk 2: "...database timeouts, check connection pool settings.## API Issues\nFor API..."
Chunk 3: "...rate limits, implement retry logic..."
```

---

### 5. Local LLM with Ollama

**What is Ollama?**

Ollama is a tool that runs large language models (LLMs) locally on your machine, allowing you to use AI models without API calls or internet connectivity.

**Why Local LLM?**

| Local LLM (Ollama) | Cloud LLM (OpenAI) |
|-------------------|-------------------|
| Free | Costs money per token |
| Data stays local | Data sent to external servers |
| Works offline | Requires internet |
| Privacy-focused | Privacy concerns |
| Slower on CPU | Faster on GPUs |

**How I Used Ollama:**

```python
from langchain_ollama import OllamaLLM

# Initialize local LLM
llm = OllamaLLM(
    model="qwen2.5",           # Model name
    base_url="http://localhost:11434",  # Ollama server
    temperature=0.7,           # Creativity level
    num_predict=1000           # Max tokens to generate
)

# Generate response
response = llm.invoke("Explain database timeouts")
```

**Models I Used:**

1. **nomic-embed-text** (274 MB)
   - Purpose: Text embeddings
   - Output: 768-dimensional vectors
   - Use: Convert text to vectors for search

2. **qwen2.5** (4.7 GB)
   - Purpose: General LLM
   - Use: Generate incident solutions
   - Alternative to: qwen2.5-coder (more code-focused)

---

### 6. Context Fusion

**What is Context Fusion?**

Context fusion is the process of combining data from multiple sources into a unified context for AI processing.

**Why Context Fusion is Needed:**

Incident data comes from different places:
- MySQL: Structured error logs
- KB Articles: Unstructured troubleshooting guides
- Service Profiles: Metadata about services

**How I Implemented It:**

```python
class ContextFusionBuilder:
    def build_context(self, incident_data):
        context_parts = []
        
        # Add service information
        context_parts.append(f"Service: {incident_data['service_name']}")
        
        # Add error logs
        for log in incident_data['error_logs']:
            context_parts.append(f"- {log['error_code']}: {log['error_message']}")
        
        # Add incident details
        if incident_data['incident_data']:
            context_parts.append(f"Severity: {incident_data['incident_data']['severity']}")
        
        return "\n".join(context_parts)
```

**Example Output:**

```
Service: payment-service
Incident: Payment Processing Outage
Severity: CRITICAL
Affected Users: 1500

Error Logs:
- ERR-5001: Database connection timeout during payment processing
- ERR-5002: Payment gateway API rate limit exceeded
- ERR-5003: Transaction deadlock detected
```

---

### 7. Semantic Search vs Keyword Search

**Keyword Search (Traditional):**

```python
# Traditional SQL query
SELECT * FROM kb_articles 
WHERE content LIKE '%database timeout%'
```

**Problems:**
- Only finds exact phrase matches
- "database timeout" ≠ "SQL connection issues"
- Misses semantically similar content

**Semantic Search (Vector):**

```python
# Vector similarity search
query_vector = embeddings.embed_query("database timeout")
results = chroma_db.query(query_embeddings=[query_vector])
```

**Benefits:**
- Finds similar concepts, not just exact words
- "database timeout" ≈ "SQL connection issues"
- Understands relationships between terms

**Example from My Project:**

**Query:** "Payment service database timeout"

**Keyword Search Results:**
- "Database connection timeout during payment processing" ✅
- "Payment service database configuration" ✅
- (Would miss: "SQL connection failure" ❌)

**Semantic Search Results:**
- "Database connection timeout during payment processing" ✅
- "SQL connection issues in payment processing" ✅ (Found via similarity)
- "Payment gateway timeout handling" ✅ (Related concept)

---

### 8. Web Framework (Flask)

**What is Flask?**

Flask is a lightweight Python web framework for building web applications and APIs.

**Why I Chose Flask:**

- **Simple:** Easy to learn and use
- **Flexible:** Can add extensions as needed
- **Lightweight:** Minimal overhead
- **Good for APIs:** Perfect for RESTful services

**How I Used Flask:**

```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Serve web interface
@app.route('/')
def index():
    return render_template('chat.html')

# Chat API endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    # Process incident
    response = process_incident(user_message)
    return jsonify({'response': response})

# Status endpoint
@app.route('/api/status')
def status():
    return jsonify(system_status)

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**API Endpoints I Created:**

- `GET /` - Chat interface
- `POST /api/chat` - Process incident queries
- `GET /api/status` - System health check
- `POST /api/init` - Initialize system
- `GET /api/history` - Chat history
- `POST /api/clear` - Clear chat

---

### 9. Database Integration (MySQL)

**What is MySQL?**

MySQL is a popular open-source relational database management system.

**Why MySQL for This Project:**

- **Structured Data:** Perfect for incidents, error logs, services
- **SQL:** Powerful querying capabilities
- **Relational:** Relationships between services, errors, incidents
- **Local:** Can run on my machine for development

**Database Schema I Designed:**

```sql
-- Services table
CREATE TABLE services (
    service_id INT PRIMARY KEY,
    service_name VARCHAR(100),
    version VARCHAR(50),
    environment VARCHAR(50),
    team VARCHAR(50),
    criticality ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')
);

-- Error logs table
CREATE TABLE error_logs (
    log_id INT PRIMARY KEY,
    service_name VARCHAR(100),
    error_code VARCHAR(50),
    error_message TEXT,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    timestamp DATETIME
);

-- Incidents table
CREATE TABLE incidents (
    incident_id VARCHAR(50) PRIMARY KEY,
    service_name VARCHAR(100),
    title VARCHAR(200),
    description TEXT,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    status VARCHAR(50),
    affected_users INT
);
```

**How I Connected to MySQL:**

```python
import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='incident_logs'
)

# Query error logs
cursor = connection.cursor(dictionary=True)
cursor.execute(
    "SELECT * FROM error_logs WHERE service_name = %s",
    ('payment-service',)
)
logs = cursor.fetchall()
```

---

### 10. Chatbot UI Design

**UI Components I Built:**

1. **Status Bar:** Shows system initialization status
2. **Chat Interface:** Message display and input
3. **Suggestion Buttons:** Quick sample incidents
4. **Typing Indicator:** Shows AI is processing
5. **Metadata Display:** Shows service name, KB articles used

**Frontend Technologies:**

- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **JavaScript** - Dynamic interactions
- **Fetch API** - AJAX calls to backend

**Key JavaScript Features:**

```javascript
// Send message to backend
async function sendMessage() {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: userInput})
    });
    const data = await response.json();
    displayResponse(data.response);
}

// Poll system status
async function pollStatus() {
    const response = await fetch('/api/status');
    const status = await response.json();
    updateStatusUI(status);
}
```

---

## How RAG Works in My Project (Detailed)

### Complete Data Flow

```
1. User Input
   "Payment service database timeout"
   ↓
2. Service Detection
   Detect: payment-service
   ↓
3. MySQL Query
   SELECT * FROM error_logs WHERE service_name = 'payment-service'
   Result: 10 error logs
   ↓
4. Context Fusion
   Combine: service info + error logs + incident details
   ↓
5. Search Query Building
   "payment-service database timeout error logs..."
   ↓
6. Vector Embedding
   nomic-embed-text → [0.123, -0.456, ...]
   ↓
7. ChromaDB Search
   Find top 3 similar KB articles
   ↓
8. Prompt Construction
   "Incident: [context]
    KB Articles: [retrieved articles]
    Generate solution:"
   ↓
9. LLM Generation
   qwen2.5 processes prompt → structured solution
   ↓
10. Response Display
   Show solution in chat interface
```

### Why This is RAG

**R (Retrieval):**
- Step 6-7: Vector search in ChromaDB retrieves relevant KB articles

**A (Augmentation):**
- Step 8: Retrieved KB articles are added to the LLM prompt context

**G (Generation):**
- Step 9: LLM generates response based on augmented context

### Key RAG Benefits Demonstrated

1. **Grounded Responses:** LLM uses actual KB articles, not just training data
2. **Specific Solutions:** Retrieved articles are about exact issues
3. **Explainable:** Can show which KB articles were used
4. **Updatable:** KB can be updated without retraining LLM

---

## Challenges I Solved

### Challenge 1: LLM Performance

**Problem:** qwen2.5-coder was taking 3+ minutes to generate responses

**Solution:**
- Switched to faster qwen2.5 model
- Reduced token limit from 2000 to 1000
- Simplified prompt template
- Added timeout handling

### Challenge 2: Database Query Time Constraints

**Problem:** Initial query only looked at last 24 hours of logs, but test data was older

**Solution:**
- Removed time constraint from MySQL query
- Retrieved all logs for the service
- Improved data retrieval for testing

### Challenge 3: Redundant Vector Database Ingestion

**Problem:** System re-ingested 375 chunks on every startup (30+ seconds)

**Solution:**
- Added check for existing ChromaDB data
- Skip ingestion if collection already has documents
- Reduced startup time from 30s to <5s

### Challenge 4: LangChain Deprecation Warnings

**Problem:** LangChain updated, old imports were deprecated

**Solution:**
- Updated imports: `langchain_community` → `langchain_ollama`
- Updated classes: `Ollama` → `OllamaLLM`
- Updated text splitters: `langchain.text_splitter` → `langchain_text_splitters`

### Challenge 5: Flask Development Server

**Problem:** Port 5000 was busy or blocked

**Solution:**
- Changed port to 5001
- Added auto-redirect in HTML
- Provided alternative URL

---

## What I Learned

### Technical Skills

1. **RAG Implementation:** End-to-end retrieval-augmented generation
2. **Vector Databases:** ChromaDB setup, ingestion, and querying
3. **Local LLM:** Ollama installation and integration
4. **MySQL Integration:** Database design and Python connectivity
5. **Web Development:** Flask API and chatbot UI
6. **LangChain:** Using AI frameworks for LLM integration
7. **Text Processing:** Chunking, embeddings, and semantic search

### Architecture Skills

1. **System Design:** Connecting multiple components (DB, vector DB, LLM, UI)
2. **API Design:** RESTful endpoints for chat and status
3. **Data Flow:** Understanding how data moves through the system
4. **Performance Optimization:** Reducing startup time and response time
5. **Error Handling:** Fallback mechanisms and graceful degradation

### Problem-Solving

1. **Debugging:** Terminal logging to identify bottlenecks
2. **API Integration:** Working with multiple external services
3. **Configuration Management:** Environment variables and .env files
4. **Testing:** Direct Ollama testing vs code integration testing

---

## Talking Points for Interviews

### When Asked: "Tell me about your project"

**Answer Structure:**
1. **Problem:** Automated incident resolution
2. **Solution:** RAG-based system with MySQL + ChromaDB + Ollama
3. **Tech Stack:** Python, Flask, MySQL, ChromaDB, Ollama, LangChain
4. **Key Features:** Semantic search, local AI, web chatbot
5. **Results:** Successfully triages incidents with relevant KB articles

### When Asked: "What is RAG?"

**Answer:**
"RAG stands for Retrieval-Augmented Generation. It's a technique where you first retrieve relevant information from a knowledge base, then augment an AI's prompt with that information, and finally have the AI generate a response based on the retrieved context. In my project, I use ChromaDB to retrieve relevant KB articles, add them to the LLM prompt along with incident data from MySQL, and then use Ollama to generate structured resolution guides."

### When Asked: "Why did you choose these technologies?"

**Answer:**
"I chose MySQL for structured incident data because it's reliable and familiar. ChromaDB for vector search because it's open-source and runs locally. Ollama for LLM because it provides privacy and no API costs. Flask for the web server because it's lightweight and easy to deploy. LangChain because it simplifies LLM integration."

### When Asked: "What was your biggest challenge?"

**Answer:**
"My biggest challenge was optimizing LLM performance. Initially, responses took 3+ minutes. I solved this by switching to a faster model, reducing token limits, and simplifying prompts. I also optimized database queries and eliminated redundant vector database ingestion, reducing startup time from 30+ seconds to under 5 seconds."

### When Asked: "How did you handle errors?"

**Answer:**
"I implemented multiple layers of error handling: fallback to mock data if MySQL fails, improved error messages in the UI, detailed logging in the terminal for debugging, and graceful degradation when the LLM is slow or unavailable. I also added connection pooling and retry logic considerations for production."

---

## Project Statistics

- **Lines of Code:** ~2,000+ lines
- **Python Files:** 6 main modules
- **KB Articles:** 12 markdown files
- **Vector Chunks:** 375 embeddings
- **Database Tables:** 3 (services, error_logs, incidents)
- **Error Logs:** 80+ sample records
- **Incidents:** 20 sample records
- **API Endpoints:** 6 REST endpoints
- **Web Pages:** 1 (chat interface)

---

## Future Enhancements

**What I Would Add Next:**

1. **External KB Integration:** Confluence and ServiceNow (designed in GUIDE.md)
2. **Authentication:** JWT-based user authentication
3. **Rate Limiting:** Prevent API abuse
4. **Monitoring:** Prometheus metrics and Sentry error tracking
5. **Production Deployment:** Docker and Kubernetes
6. **Real-time Updates:** Webhooks for KB article changes
7. **Multi-user Support:** Per-user chat history and preferences
8. **Caching:** Redis for performance optimization

---

## Key Takeaways

1. **RAG Power:** Combining retrieval with generation makes AI more accurate and reliable
2. **Local AI:** Ollama enables privacy-focused AI without API costs
3. **Vector Search:** Semantic search is superior to keyword search for understanding intent
4. **System Integration:** Successfully connected multiple complex components
5. **Performance Matters:** Optimization is crucial for user experience
6. **Error Handling:** Robust systems need fallbacks and graceful degradation

---

## Conclusion

This project demonstrates my ability to:
- Design and implement complex AI systems
- Work with modern AI/ML technologies
- Build full-stack applications
- Solve performance and integration challenges
- Explain technical concepts clearly

The incident triage system showcases practical application of RAG, vector databases, and local LLMs to solve a real business problem: automated incident resolution.

---

*Interview Guide - Incident Triage System*
*Prepared for Technical Interviews*
*Last Updated: 2026-09-21*