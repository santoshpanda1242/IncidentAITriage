from typing import List, Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


class OllamaLLMSynthesis:
    """LLM synthesis using Ollama for generating incident solutions"""
    
    def __init__(self, model_name: str = "qwen2.5", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama LLM for synthesis
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.7,  # Balance between creativity and consistency
            num_predict=1000  # Reduced token limit for faster response
        )
        
        # Create prompt template for incident synthesis
        self.prompt_template = """You are an expert incident response specialist. Analyze the following incident and provide a concise resolution guide.

INCIDENT CONTEXT:
{incident_context}

RELEVANT KNOWLEDGE BASE ARTICLES:
{kb_articles}

Provide a brief response with:
1. Problem Summary (1-2 sentences)
2. Immediate Actions (3-5 bullet points)
3. Recommended Solution (2-3 sentences)

Be concise and actionable.
"""
        
        print(f"✓ Ollama LLM initialized with model: {model_name}")
    
    def synthesize_solution(
        self, 
        incident_context: str, 
        kb_articles: List[Dict[str, Any]],
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Synthesize a solution from incident context and KB articles
        
        Args:
            incident_context: Context information about the incident
            kb_articles: List of relevant KB articles from vector search
            custom_prompt: Optional custom prompt template
        
        Returns:
            Generated solution text
        """
        # Format KB articles for the prompt
        kb_content = self._format_kb_articles(kb_articles)
        
        # Use custom prompt if provided, otherwise use default
        prompt_template = custom_prompt if custom_prompt else self.prompt_template
        
        # Format the complete prompt
        full_prompt = prompt_template.format(
            incident_context=incident_context,
            kb_articles=kb_content
        )
        
        # Generate response
        try:
            response = self.llm.invoke(full_prompt)
            return response
        except Exception as e:
            print(f"✗ LLM synthesis error: {e}")
            return self._generate_fallback_solution(incident_context, kb_articles)
    
    def _format_kb_articles(self, kb_articles: List[Dict[str, Any]]) -> str:
        """Format KB articles for the prompt"""
        if not kb_articles:
            return "No relevant knowledge base articles found."
        
        formatted = []
        for i, article in enumerate(kb_articles, 1):
            formatted.append(f"Article {i}:")
            formatted.append(f"Source: {article.get('metadata', {}).get('source_file', 'Unknown')}")
            formatted.append(f"Content: {article.get('content', '')[:500]}...")  # Truncate long content
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _generate_fallback_solution(self, incident_context: str, kb_articles: List[Dict[str, Any]]) -> str:
        """Generate a basic fallback solution if LLM fails"""
        # Try to provide a basic solution based on KB articles
        if kb_articles:
            kb_content = "\n\n".join([f"- {article.get('content', '')[:200]}" for article in kb_articles[:2]])
            fallback = f"""# Incident Resolution Guide (Fallback)

## Problem Summary
Unable to generate detailed solution due to LLM error. However, found relevant knowledge base articles.

## Incident Context
{incident_context[:300]}

## Relevant Knowledge Base Articles
{kb_content}

## Recommended Actions
1. Review the KB articles above
2. Check database connection status
3. Review error logs for specific issues
4. Contact the payments team if urgent
"""
        else:
            fallback = f"""# Incident Resolution Guide (Fallback)

## Problem Summary
Unable to generate detailed solution due to LLM error. Please review the incident context manually.

## Incident Context
{incident_context[:300]}

## Recommended Actions
1. Review the incident context above
2. Check database connection status
3. Contact the appropriate team based on service name
"""
        
        return fallback
    
    def synthesize_with_context(
        self,
        service_name: str,
        error_logs: List[Dict[str, Any]],
        service_profile: Dict[str, Any],
        kb_articles: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesize solution with structured context
        
        Args:
            service_name: Name of the affected service
            error_logs: List of error logs
            service_profile: Service profile information
            kb_articles: List of relevant KB articles
        
        Returns:
            Generated solution text
        """
        # Build structured context
        context_parts = []
        context_parts.append(f"Service: {service_name}")
        
        if service_profile:
            context_parts.append(f"Version: {service_profile.get('version', 'unknown')}")
            context_parts.append(f"Environment: {service_profile.get('environment', 'unknown')}")
            context_parts.append(f"Team: {service_profile.get('team', 'unknown')}")
        
        if error_logs:
            context_parts.append(f"\nRecent Errors:")
            for log in error_logs[:3]:  # Top 3 errors
                context_parts.append(f"- {log.get('error_code', 'N/A')}: {log.get('error_message', 'No message')}")
        
        incident_context = "\n".join(context_parts)
        
        return self.synthesize_solution(incident_context, kb_articles)
    
    def test_connection(self) -> bool:
        """Test if Ollama LLM is accessible"""
        try:
            response = self.llm.invoke("Hello, can you respond with just 'OK'?")
            return "OK" in response or "ok" in response.lower()
        except Exception as e:
            print(f"✗ Ollama connection test failed: {e}")
            return False


class IncidentSolutionGenerator:
    """High-level interface for generating incident solutions"""
    
    def __init__(self, model_name: str = "qwen2.5-coder"):
        """
        Initialize solution generator
        
        Args:
            model_name: Ollama model to use for synthesis
        """
        self.synthesizer = OllamaLLMSynthesis(model_name=model_name)
        self.connection_tested = False
    
    def generate_solution(
        self,
        incident_data: Dict[str, Any],
        kb_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate complete incident solution
        
        Args:
            incident_data: Complete incident data from database
            kb_articles: Relevant KB articles from vector search
        
        Returns:
            Dictionary containing solution and metadata
        """
        # Test connection on first use
        if not self.connection_tested:
            if not self.synthesizer.test_connection():
                return {
                    'success': False,
                    'error': 'Ollama LLM connection failed',
                    'solution': None
                }
            self.connection_tested = True
        
        # Extract incident context
        service_name = incident_data.get('service_name', 'unknown')
        error_logs = incident_data.get('error_logs', [])
        service_profile = incident_data.get('service_profile', {})
        incident_info = incident_data.get('incident_data', {})
        
        # Build context string
        context_builder = []
        context_builder.append(f"Service: {service_name}")
        
        if incident_info:
            context_builder.append(f"Incident: {incident_info.get('title', 'Unknown')}")
            context_builder.append(f"Severity: {incident_info.get('severity', 'UNKNOWN')}")
            context_builder.append(f"Affected Users: {incident_info.get('affected_users', 0)}")
            if incident_info.get('business_impact'):
                context_builder.append(f"Business Impact: {incident_info.get('business_impact')}")
        
        if error_logs:
            context_builder.append(f"\nError Logs:")
            for log in error_logs[:3]:
                context_builder.append(f"- {log.get('error_code', 'N/A')}: {log.get('error_message', 'No message')}")
        
        incident_context = "\n".join(context_builder)
        
        # Generate solution
        try:
            solution = self.synthesizer.synthesize_solution(incident_context, kb_articles)
            
            return {
                'success': True,
                'solution': solution,
                'service_name': service_name,
                'kb_articles_count': len(kb_articles),
                'error_logs_count': len(error_logs),
                'model_used': self.synthesizer.model_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'solution': None
            }
    
    def generate_quick_solution(
        self,
        service_name: str,
        error_message: str,
        kb_articles: List[Dict[str, Any]]
    ) -> str:
        """
        Generate quick solution from minimal information
        
        Args:
            service_name: Name of the service
            error_message: Error message or description
            kb_articles: Relevant KB articles
        
        Returns:
            Generated solution text
        """
        incident_context = f"Service: {service_name}\nError: {error_message}"
        return self.synthesizer.synthesize_solution(incident_context, kb_articles)