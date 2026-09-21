# Incident Triage System - Complete Guide

## Table of Contents
1. [Prompt Templates](#prompt-templates)
2. [Production Readiness Guide](#production-readiness-guide)
3. [External KB Integration](#external-kb-integration)
4. [System Architecture](#system-architecture)
5. [Deployment Considerations](#deployment-considerations)

---

## Prompt Templates

### Template 1: Expert Consultant

**Use when you need expert advice on a specific topic:**

```
Act as an expert in [Topic/Field]. I need help with [Briefly describe what you want to achieve].

Please provide a clear, step-by-step breakdown that covers:
1. Core concepts or direct answers
2. Practical examples or use cases
3. Potential pitfalls or common mistakes to avoid

Keep the tone concise, practical, and easy to understand.
```

**Example:**
```
Act as an expert in Database Performance Tuning. I need help with optimizing MySQL for high-traffic payment processing.

Please provide a clear, step-by-step breakdown that covers:
1. Core concepts or direct answers
2. Practical examples or use cases
3. Potential pitfalls or common mistakes to avoid

Keep the tone concise, practical, and easy to understand.
```

---

### Template 2: Senior Software Engineer

**Use when you need production-ready code solutions:**

```
Act as a senior software engineer. I need a solution for the following requirements:

- Goal: [Describe what the code should do]
- Language/Framework: [e.g., Python, Bash, Kubernetes YAML]
- Constraints: [e.g., must be performant, no third-party libraries, handle edge cases]

Please provide:
1. Clean, production-ready code with inline comments
2. Brief explanations of key parts
3. Instructions on how to test or run it
```

**Example:**
```
Act as a senior software engineer. I need a solution for the following requirements:

- Goal: Create a database connection pool manager for MySQL
- Language/Framework: Python with SQLAlchemy
- Constraints: Must handle connection timeouts, retry logic, and support up to 100 concurrent connections

Please provide:
1. Clean, production-ready code with inline comments
2. Brief explanations of key parts
3. Instructions on how to test or run it
```

---

### Template 3: Editor and Content Strategist

**Use when you need to improve or create documentation:**

```
Act as an editor and content strategist. Please improve/write text based on the following context:

- Goal: [e.g., Draft an email, rewrite a document, polish a proposal]
- Target Audience: [e.g., Technical team, executive leadership, client]
- Tone: [e.g., Professional, direct, persuasive]

Here is the draft or key points:
[Insert text or bullet points here]
```

**Example:**
```
Act as an editor and content strategist. Please improve/write text based on the following context:

- Goal: Create an incident response email to stakeholders
- Target Audience: Executive leadership and product team
- Tone: Professional, direct, actionable

Here is the draft or key points:
- Payment service outage
- 1500 users affected
- Working on fix
- ETA 2 hours
```

---

### Template 4: Concept Explanation

**Use when you need complex topics explained simply:**

```
Explain [Concept/Topic] to me. 

Please structure your explanation as follows:
1. High-Level Overview (a 2-3 sentence summary)
2. Simple Analogy (explain it like I'm 10 years old)
3. Deep Dive (key technical details and architecture/mechanics)
4. Key Takeaways (3-5 bullet points summarizing the main ideas)
```

**Example:**
```
Explain Vector Databases to me. 

Please structure your explanation as follows:
1. High-Level Overview (a 2-3 sentence summary)
2. Simple Analogy (explain it like I'm 10 years old)
3. Deep Dive (key technical details and architecture/mechanics)
4. Key Takeaways (3-5 bullet points summarizing the main ideas)
```

---

## Production Readiness Guide

### Current System Status

**Current Architecture:**
- ✅ Local MySQL database
- ✅ Local ChromaDB vector store
- ✅ Local markdown files for KB
- ✅ Local Ollama LLM
- ✅ Flask development server
- ⚠️ Single-user development setup

### Production Requirements

#### 1. Database Scalability

**Current:** Single MySQL instance with direct connection

**Production Changes Needed:**

```python
# Add connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Production database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'pool_size': 20,  # Connection pool size
    'max_overflow': 10,  # Max additional connections
    'pool_timeout': 30,  # Connection timeout
    'pool_recycle': 3600,  # Recycle connections after 1 hour
}

engine = create_engine(
    f"mysql+mysqlconnector://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}",
    poolclass=QueuePool,
    pool_size=DATABASE_CONFIG['pool_size'],
    max_overflow=DATABASE_CONFIG['max_overflow'],
    pool_timeout=DATABASE_CONFIG['pool_timeout'],
    pool_recycle=DATABASE_CONFIG['pool_recycle']
)
```

**Additional Considerations:**
- Implement read replicas for read-heavy operations
- Add database backup and recovery procedures
- Implement query optimization and indexing
- Add monitoring and alerting for database performance

#### 2. Vector Database Scalability

**Current:** Local ChromaDB with embedded persistence

**Production Options:**

**Option A: ChromaDB Server (Self-hosted)**
```python
# Replace embedded client with server client
import chromadb
from chromadb.config import Settings

# Production ChromaDB server
client = chromadb.HttpClient(
    host=os.getenv('CHROMADB_HOST', 'localhost'),
    port=int(os.getenv('CHROMADB_PORT', 8000)),
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

**Option B: Cloud Vector Database (Pinecone)**
```python
import pinecone

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv('PINECONE_API_KEY'),
    environment=os.getenv('PINECONE_ENVIRONMENT')
)

# Create index
index_name = "incident-kb"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=768,  # Match embedding model dimension
        metric="cosine"
    )
```

**Option C: Weaviate (Cloud or Self-hosted)**
```python
import weaviate

# Production Weaviate client
client = weaviate.Client(
    url=os.getenv('WEAVIATE_URL'),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv('WEAVIATE_API_KEY'))
)
```

#### 3. LLM Scalability

**Current:** Local Ollama with qwen2.5

**Production Options:**

**Option A: Self-hosted Ollama with Load Balancing**
```python
# Multiple Ollama instances behind load balancer
OLLAMA_ENDPOINTS = [
    "http://ollama-1:11434",
    "http://ollama-2:11434",
    "http://ollama-3:11434"
]

# Round-robin selection
import random
endpoint = random.choice(OLLAMA_ENDPOINTS)
llm = OllamaLLM(
    model="qwen2.5",
    base_url=endpoint
)
```

**Option B: Cloud LLM API (OpenAI, Anthropic)**
```python
from langchain_openai import ChatOpenAI

# Production OpenAI client
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.7,
    max_tokens=1000,
    timeout=30
)
```

**Option C: Azure OpenAI Service**
```python
from langchain_openai import AzureChatOpenAI

# Azure OpenAI
llm = AzureChatOpenAI(
    deployment_name="gpt-4-deployment",
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_version="2024-02-15-preview"
)
```

#### 4. Web Server Scalability

**Current:** Flask development server

**Production Changes:**

**Option A: Gunicorn with Gevent**
```bash
# Install
pip install gunicorn gevent

# Run
gunicorn -w 4 -k gevent app:app --bind 0.0.0.0:5000
```

**Option B: Docker + Kubernetes**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: incident-triage
spec:
  replicas: 3
  selector:
    matchLabels:
      app: incident-triage
  template:
    metadata:
      labels:
        app: incident-triage
    spec:
      containers:
      - name: app
        image: incident-triage:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

#### 5. Security Enhancements

**Required Security Changes:**

```python
# Add rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # Chat endpoint
    pass

# Add authentication
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    return decorated

@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    # Protected endpoint
    pass
```

#### 6. Monitoring and Logging

**Add Production Monitoring:**

```python
import logging
from prometheus_flask_exporter import PrometheusMetrics

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
PrometheusMetrics(app)

# Add custom metrics
from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
chat_duration = Histogram('chat_duration_seconds', 'Chat request duration')

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    chat_requests.inc()
    
    try:
        # Process chat
        response = process_chat()
        chat_duration.observe(time.time() - start_time)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise
```

#### 7. Environment Configuration

**Production Environment Variables:**

```bash
# .env.production
# Database
DB_HOST=prod-db.example.com
DB_PORT=3306
DB_USER=incident_user
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=incident_logs

# Vector Database
CHROMADB_HOST=chromadb.prod.example.com
CHROMADB_PORT=8000
CHROMADB_PERSIST_DIR=/data/chromadb

# LLM
OLLAMA_BASE_URL=http://ollama-lb.prod.example.com:11434
OLLAMA_LLM_MODEL=qwen2.5
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Security
JWT_SECRET=${JWT_SECRET}
API_KEY=${API_KEY}

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
PROMETHEUS_ENABLED=true
```

---

## External KB Integration

### Current Setup
- Local markdown files in `kb/` directory
- Manual file ingestion on startup
- No real-time updates

### External KB Source Options

#### 1. Confluence Integration

**Architecture:**
```
Confluence API → Content Fetcher → Text Processor → Vector Store
```

**Implementation:**

```python
import requests
from atlassian import Confluence
from typing import List, Dict, Any

class ConfluenceKBFetcher:
    """Fetch knowledge base articles from Confluence"""
    
    def __init__(self):
        self.confluence = Confluence(
            url=os.getenv('CONFLUENCE_URL'),
            username=os.getenv('CONFLUENCE_USERNAME'),
            password=os.getenv('CONFLUENCE_API_TOKEN')
        )
        self.space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'KB')
    
    def fetch_articles(self, page_limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch all articles from Confluence space"""
        articles = []
        
        try:
            # Get all pages in space
            pages = self.confluence.get_all_pages_from_space(
                self.space_key,
                start=0,
                limit=page_limit,
                status='current'
            )
            
            for page in pages:
                # Get page content
                content = self.confluence.get_page_by_id(
                    page['id'],
                    expand='body.storage'
                )
                
                # Extract text from Confluence storage format
                text_content = self._extract_text_from_storage(
                    content['body']['storage']['value']
                )
                
                articles.append({
                    'id': page['id'],
                    'title': page['title'],
                    'content': text_content,
                    'url': f"{os.getenv('CONFLUENCE_URL')}/pages/viewpage.action?pageId={page['id']}",
                    'last_modified': page['version']['when'],
                    'source': 'confluence'
                })
            
            logger.info(f"Fetched {len(articles)} articles from Confluence")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching Confluence articles: {e}")
            return []
    
    def _extract_text_from_storage(self, storage_format: str) -> str:
        """Extract plain text from Confluence storage format"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(storage_format, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def watch_for_updates(self, callback):
        """Watch for Confluence updates and trigger callback"""
        # Implement webhook or polling mechanism
        pass
```

**Configuration:**
```bash
# .env
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=KB
```

#### 2. ServiceNow Integration

**Architecture:**
```
ServiceNow API → Knowledge Base Fetcher → Text Processor → Vector Store
```

**Implementation:**

```python
import requests
from typing import List, Dict, Any

class ServiceNowKBFetcher:
    """Fetch knowledge base articles from ServiceNow"""
    
    def __init__(self):
        self.base_url = os.getenv('SERVICENOW_URL')
        self.username = os.getenv('SERVICENOW_USERNAME')
        self.password = os.getenv('SERVICENOW_PASSWORD')
        self.kb_category = os.getenv('SERVICENOW_KB_CATEGORY', 'incident')
    
    def fetch_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch knowledge base articles from ServiceNow"""
        articles = []
        
        try:
            # ServiceNow Table API for Knowledge Base
            url = f"{self.base_url}/api/now/table/kb_knowledge_base"
            params = {
                'sysparm_query': f'category={self.kb_category}^active=true',
                'sysparm_limit': limit,
                'sysparm_display_value': 'true'
            }
            
            response = requests.get(
                url,
                auth=(self.username, self.password),
                params=params,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('result', []):
                    # Get article details with content
                    article_url = f"{self.base_url}/api/now/table/kb_knowledge_base/{article['sys_id']}"
                    article_response = requests.get(
                        article_url,
                        auth=(self.username, self.password),
                        headers={'Accept': 'application/json'}
                    )
                    
                    if article_response.status_code == 200:
                        article_data = article_response.json()
                        articles.append({
                            'id': article['sys_id'],
                            'title': article_data['result']['short_description'],
                            'content': article_data['result']['text'],
                            'url': f"{self.base_url}/kb_view.do?sysparm_article={article['sys_id']}",
                            'category': article_data['result']['category'],
                            'last_modified': article_data['result']['sys_updated_on'],
                            'source': 'servicenow'
                        })
                
                logger.info(f"Fetched {len(articles)} articles from ServiceNow")
            
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching ServiceNow articles: {e}")
            return []
    
    def search_articles(self, query: str) -> List[Dict[str, Any]]:
        """Search ServiceNow knowledge base"""
        articles = []
        
        try:
            url = f"{self.base_url}/api/now/table/kb_knowledge_base"
            params = {
                'sysparm_query': f'short_descriptionLIKE{query}^active=true',
                'sysparm_limit': 10
            }
            
            response = requests.get(
                url,
                auth=(self.username, self.password),
                params=params,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('result', [])
            
            return articles
        
        except Exception as e:
            logger.error(f"Error searching ServiceNow: {e}")
            return []
```

**Configuration:**
```bash
# .env
SERVICENOW_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
SERVICENOW_KB_CATEGORY=incident
```

#### 3. Unified KB Integration

**Architecture for Multiple Sources:**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class KBSource(ABC):
    """Abstract base class for KB sources"""
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from the source"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the source name"""
        pass

class UnifiedKBManager:
    """Manage multiple KB sources"""
    
    def __init__(self):
        self.sources: List[KBSource] = []
        self.vector_store = None
    
    def add_source(self, source: KBSource):
        """Add a KB source"""
        self.sources.append(source)
    
    def fetch_all_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from all sources"""
        all_articles = []
        
        for source in self.sources:
            try:
                articles = source.fetch_articles()
                all_articles.extend(articles)
                logger.info(f"Fetched {len(articles)} from {source.get_source_name()}")
            except Exception as e:
                logger.error(f"Error fetching from {source.get_source_name()}: {e}")
        
        return all_articles
    
    def ingest_all_sources(self):
        """Ingest articles from all sources into vector store"""
        articles = self.fetch_all_articles()
        
        for article in articles:
            self.vector_store.ingest_document(
                content=article['content'],
                metadata={
                    'source': article['source'],
                    'title': article['title'],
                    'url': article.get('url', ''),
                    'last_modified': article.get('last_modified', '')
                }
            )
        
        logger.info(f"Ingested {len(articles)} articles from all sources")

# Usage
kb_manager = UnifiedKBManager()
kb_manager.add_source(ConfluenceKBFetcher())
kb_manager.add_source(ServiceNowKBFetcher())
kb_manager.add_source(LocalMarkdownKBFetcher())  # Keep local as fallback
kb_manager.ingest_all_sources()
```

#### 4. Real-time Updates

**Webhook-based Updates:**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/confluence', methods=['POST'])
def confluence_webhook():
    """Handle Confluence page update webhook"""
    data = request.json
    
    if data.get('event') == 'page_updated':
        page_id = data.get('page_id')
        
        # Fetch updated content
        fetcher = ConfluenceKBFetcher()
        article = fetcher.fetch_article_by_id(page_id)
        
        # Update vector store
        vector_store.update_document(
            doc_id=f"confluence_{page_id}",
            content=article['content'],
            metadata=article
        )
        
        return jsonify({'status': 'updated'})
    
    return jsonify({'status': 'ignored'})

@app.route('/webhook/servicenow', methods=['POST'])
def servicenow_webhook():
    """Handle ServiceNow KB update webhook"""
    data = request.json
    
    if data.get('event') == 'kb_updated':
        article_id = data.get('sys_id')
        
        # Fetch updated content
        fetcher = ServiceNowKBFetcher()
        article = fetcher.fetch_article_by_id(article_id)
        
        # Update vector store
        vector_store.update_document(
            doc_id=f"servicenow_{article_id}",
            content=article['content'],
            metadata=article
        )
        
        return jsonify({'status': 'updated'})
    
    return jsonify({'status': 'ignored'})
```

#### 5. Synchronization Strategy

**Incremental Updates:**

```python
class KBSynchronizer:
    """Handle incremental KB synchronization"""
    
    def __init__(self, kb_manager: UnifiedKBManager):
        self.kb_manager = kb_manager
        self.last_sync_time = None
    
    def sync_incremental(self):
        """Perform incremental sync"""
        current_time = datetime.now()
        
        for source in self.kb_manager.sources:
            try:
                # Fetch only articles modified since last sync
                articles = source.fetch_articles(
                    modified_since=self.last_sync_time
                )
                
                for article in articles:
                    # Update or create in vector store
                    self.kb_manager.vector_store.upsert_document(
                        doc_id=f"{source.get_source_name()}_{article['id']}",
                        content=article['content'],
                        metadata=article
                    )
                
                logger.info(f"Synced {len(articles)} updates from {source.get_source_name()}")
            
            except Exception as e:
                logger.error(f"Error syncing {source.get_source_name()}: {e}")
        
        self.last_sync_time = current_time
    
    def sync_full(self):
        """Perform full sync"""
        self.kb_manager.ingest_all_sources()
        self.last_sync_time = datetime.now()
```

#### 6. Caching Strategy

**Multi-layer Caching:**

```python
from functools import lru_cache
import redis

class CachedKBManager:
    """KB manager with caching"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0
        )
        self.cache_ttl = 3600  # 1 hour
    
    @lru_cache(maxsize=1000)
    def get_article(self, article_id: str) -> Dict[str, Any]:
        """Get article with multi-layer caching"""
        # Check L1 cache (in-memory)
        # Check L2 cache (Redis)
        # Fetch from source if not cached
        pass
    
    def search_with_cache(self, query: str) -> List[Dict[str, Any]]:
        """Search with caching"""
        cache_key = f"search:{query}"
        
        # Check cache
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Perform search
        results = self.vector_store.similarity_search(query)
        
        # Cache results
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(results)
        )
        
        return results
```

---

## System Architecture

### Production Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer                             │
│                  (Nginx/HAProxy)                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  Flask App 1   │ │ Flask App 2 │ │ Flask App 3 │
│  (Worker)      │ │ (Worker)    │ │ (Worker)    │
└───────┬────────┘ └─────┬──────┘ └──────┬──────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  MySQL Master  │ │  MySQL Read │ │ MySQL Read  │
│  (Write)       │ │  Replica 1  │ │  Replica 2  │
└────────────────┘ └────────────┘ └────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  ChromaDB/     │ │  Ollama/    │ │  Redis/     │
│  Pinecone      │ │  OpenAI     │ │  Cache      │
│  (Vector DB)   │ │  (LLM)      │ │  (Cache)    │
└────────────────┘ └────────────┘ └────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  Confluence    │ │ ServiceNow  │ │  Local KB   │
│  (KB Source)   │ │ (KB Source) │ │  (Backup)   │
└────────────────┘ └────────────┘ └────────────┘
```

---

## Deployment Considerations

### 1. Infrastructure Requirements

**Minimum Production Requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 1Gbps

**Recommended Production Requirements:**
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+ SSD
- Network: 10Gbps

### 2. CI/CD Pipeline

**GitHub Actions Example:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: |
          docker build -t incident-triage:${{ github.sha }} .
      - name: Push to registry
        run: |
          docker push incident-triage:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/incident-triage app=incident-triage:${{ github.sha }}
```

### 3. Monitoring Stack

**Recommended Tools:**
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **ELK Stack**: Log aggregation
- **Jaeger**: Distributed tracing

### 4. Backup Strategy

**Backup Checklist:**
- [ ] MySQL daily backups
- [ ] Vector database backups
- [ ] KB article backups
- [ ] Configuration backups
- [ ] Disaster recovery plan

### 5. Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Security headers
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

---

## Quick Reference

### Key Files to Modify for Production

1. **`app.py`** - Add authentication, rate limiting, monitoring
2. **`src/database_manager.py`** - Add connection pooling, retry logic
3. **`src/vector_store.py`** - Switch to server/cloud vector DB
4. **`src/synthesis.py`** - Switch to production LLM API
5. **`.env`** - Production environment variables
6. **`Dockerfile`** - Containerization
7. **`deployment.yaml`** - Kubernetes deployment

### Environment Variables Checklist

```bash
# Database
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=

# Vector Database
CHROMADB_HOST=
CHROMADB_PORT=
# OR
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=

# LLM
OLLAMA_BASE_URL=
# OR
OPENAI_API_KEY=
# OR
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=

# External KB
CONFLUENCE_URL=
CONFLUENCE_USERNAME=
CONFLUENCE_API_TOKEN=
SERVICENOW_URL=
SERVICENOW_USERNAME=
SERVICENOW_PASSWORD=

# Security
JWT_SECRET=
API_KEY=

# Monitoring
SENTRY_DSN=
PROMETHEUS_ENABLED=
```

---

## Summary

This guide provides:

1. **4 Professional Prompt Templates** for different use cases
2. **Complete Production Readiness Guide** with code examples
3. **External KB Integration** for Confluence and ServiceNow
4. **System Architecture** and deployment strategies
5. **Quick Reference** for key production changes

**Next Steps:**
1. Review current system against production requirements
2. Choose external KB integration strategy
3. Implement security enhancements
4. Set up monitoring and logging
5. Plan deployment strategy

---

*Last Updated: 2026-09-21*
*Version: 1.0*