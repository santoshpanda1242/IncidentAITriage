#!/usr/bin/env python3
"""
Incident Triage Chatbot - Flask Web Application

Simple web-based chatbot interface for incident resolution.
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database_manager import DatabaseManager
from context_fusion import ContextFusionBuilder
from vector_store import KnowledgeBaseManager
from synthesis import IncidentSolutionGenerator

app = Flask(__name__)

# Initialize system components
db_manager = None
kb_manager = None
solution_generator = None
context_builder = None

# System status
system_status = {
    'initialized': False,
    'initializing': False,
    'error': None,
    'components': {
        'database': False,
        'knowledge_base': False,
        'llm': False
    }
}

# Chat history storage
chat_history = []

def initialize_system():
    """Initialize all system components in background"""
    global db_manager, kb_manager, solution_generator, context_builder, system_status
    
    system_status['initializing'] = True
    print("Initializing system components...")
    
    try:
        # Initialize database manager
        print("1. Connecting to database...")
        db_manager = DatabaseManager()
        system_status['components']['database'] = True
        
        # Initialize knowledge base
        print("2. Initializing knowledge base...")
        kb_manager = KnowledgeBaseManager(kb_directory="./kb")
        kb_manager.initialize_knowledge_base()
        system_status['components']['knowledge_base'] = True
        
        # Initialize solution generator
        print("3. Initializing LLM...")
        solution_generator = IncidentSolutionGenerator(model_name="qwen2.5")
        
        # Initialize context builder
        context_builder = ContextFusionBuilder()
        
        # Test LLM connection
        print("4. Testing LLM connection...")
        if solution_generator.synthesizer.test_connection():
            system_status['components']['llm'] = True
            print("✓ System initialized successfully")
            system_status['initialized'] = True
        else:
            print("✗ Ollama connection failed")
            system_status['error'] = "Ollama connection failed"
    
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        system_status['error'] = str(e)
    
    finally:
        system_status['initializing'] = False

@app.route('/')
def index():
    """Render the chat interface"""
    return render_template('chat.html')

@app.route('/api/init', methods=['POST'])
def initialize():
    """Trigger system initialization"""
    if not system_status['initialized'] and not system_status['initializing']:
        # Start initialization in background thread
        thread = threading.Thread(target=initialize_system)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'initializing'})
    elif system_status['initializing']:
        return jsonify({'status': 'initializing'})
    else:
        return jsonify({'status': 'ready' if not system_status['error'] else 'error'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Add user message to history
    chat_history.append({
        'role': 'user',
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Process the incident
    try:
        print(f"\n{'='*60}")
        print(f"Processing chat request: {user_message[:50]}...")
        print(f"{'='*60}")
        
        # Extract service name from message (simple heuristic)
        service_name = extract_service_name(user_message)
        
        if not service_name:
            service_name = 'payment-service'  # Default fallback
        
        print(f"1. Service name detected: {service_name}")
        
        # Get incident context
        print("2. Getting incident context from database...")
        incident_context = db_manager.get_incident_context(service_name)
        print(f"   ✓ Got {len(incident_context.get('error_logs', []))} error logs")
        
        # Build search query
        print("3. Building search query...")
        search_query = context_builder.build_search_query(incident_context)
        print(f"   ✓ Search query: {search_query[:100]}...")
        
        # Search knowledge base
        print("4. Searching knowledge base...")
        kb_results = kb_manager.search_knowledge_base(search_query, n_results=3)
        print(f"   ✓ Found {len(kb_results)} relevant KB articles")
        
        # Generate solution
        print("5. Generating solution with LLM (this may take 30-60 seconds)...")
        solution_result = solution_generator.generate_solution(incident_context, kb_results)
        
        if solution_result['success']:
            bot_response = solution_result['solution']
            print("   ✓ Solution generated successfully")
        else:
            bot_response = f"I encountered an error: {solution_result.get('error', 'Unknown error')}"
            print(f"   ✗ Solution generation failed: {solution_result.get('error')}")
        
        # Add bot response to history
        chat_history.append({
            'role': 'assistant',
            'message': bot_response,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'service_name': service_name,
                'kb_articles_count': solution_result.get('kb_articles_count', 0),
                'error_logs_count': solution_result.get('error_logs_count', 0)
            }
        })
        
        print(f"{'='*60}\n")
        
        return jsonify({
            'response': bot_response,
            'metadata': {
                'service_name': service_name,
                'kb_articles_count': solution_result.get('kb_articles_count', 0),
                'error_logs_count': solution_result.get('error_logs_count', 0)
            }
        })
    
    except Exception as e:
        print(f"\n✗ Error in chat processing: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_message = f"Error processing your request: {str(e)}"
        chat_history.append({
            'role': 'assistant',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': error_message}), 500

@app.route('/api/history')
def get_history():
    """Get chat history"""
    return jsonify({'history': chat_history})

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear chat history"""
    global chat_history
    chat_history = []
    return jsonify({'status': 'cleared'})

@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify(system_status)

def extract_service_name(message: str) -> str:
    """Extract service name from user message"""
    # Common service names in our system
    services = [
        'payment-service', 'user-service', 'notification-service', 'order-service',
        'analytics-service', 'file-upload-service', 'search-service', 'auth-service',
        'recommendation-service', 'reporting-service', 'api-gateway', 'cache-service',
        'database-service', 'cdn-service', 'workflow-service', 'integration-service'
    ]
    
    message_lower = message.lower()
    
    # Check if any service name is mentioned
    for service in services:
        if service.replace('-', ' ') in message_lower or service in message_lower:
            return service
    
    # If no service found, try to extract common patterns
    if 'payment' in message_lower:
        return 'payment-service'
    elif 'user' in message_lower or 'auth' in message_lower:
        return 'user-service'
    elif 'order' in message_lower:
        return 'order-service'
    elif 'database' in message_lower:
        return 'database-service'
    elif 'cache' in message_lower:
        return 'cache-service'
    
    return None

if __name__ == '__main__':
    print("Starting Flask web server...")
    print("Open your browser to: http://localhost:5001")
    print("System will initialize in background when you click 'Initialize'")
    app.run(debug=True, host='0.0.0.0', port=5001)