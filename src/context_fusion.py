from typing import Dict, Any, List
from datetime import datetime


class ContextFusionBuilder:
    """Builds unified context from multiple data sources for semantic search"""
    
    def __init__(self):
        self.fusion_templates = {
            'standard': self._standard_fusion,
            'detailed': self._detailed_fusion,
            'compact': self._compact_fusion
        }
    
    def build_context(self, incident_data: Dict[str, Any], fusion_type: str = 'standard') -> str:
        """
        Build unified context string from incident data
        
        Args:
            incident_data: Dictionary containing error_logs and service_profile
            fusion_type: Type of fusion template ('standard', 'detailed', 'compact')
        
        Returns:
            Unified context string for semantic search
        """
        fusion_func = self.fusion_templates.get(fusion_type, self._standard_fusion)
        return fusion_func(incident_data)
    
    def _standard_fusion(self, incident_data: Dict[str, Any]) -> str:
        """Standard fusion template - balanced detail level"""
        service_name = incident_data.get('service_name', 'unknown')
        error_logs = incident_data.get('error_logs', [])
        service_profile = incident_data.get('service_profile', {})
        incident_info = incident_data.get('incident_data', {})
        
        context_parts = []
        
        # Service information
        if service_profile:
            context_parts.append(f"Service: {service_profile.get('name', service_name)}")
            context_parts.append(f"Version: {service_profile.get('version', 'unknown')}")
            context_parts.append(f"Environment: {service_profile.get('environment', 'unknown')}")
            context_parts.append(f"Team: {service_profile.get('team', 'unknown')}")
            context_parts.append(f"Criticality: {service_profile.get('criticality', 'unknown')}")
            
            deps = service_profile.get('dependencies', [])
            if deps:
                context_parts.append(f"Dependencies: {', '.join(deps)}")
        
        # Incident information
        if incident_info:
            context_parts.append(f"\nIncident: {incident_info.get('title', 'Unknown incident')}")
            context_parts.append(f"Severity: {incident_info.get('severity', 'UNKNOWN')}")
            context_parts.append(f"Affected Users: {incident_info.get('affected_users', 0)}")
            if incident_info.get('business_impact'):
                context_parts.append(f"Business Impact: {incident_info['business_impact']}")
        
        # Error information
        if error_logs:
            context_parts.append(f"\nRecent Errors ({len(error_logs)} found):")
            for i, log in enumerate(error_logs[:5], 1):  # Limit to 5 most recent
                context_parts.append(f"{i}. {log.get('error_code', 'N/A')}: {log.get('error_message', 'No message')}")
                context_parts.append(f"   Severity: {log.get('severity', 'UNKNOWN')}")
                if log.get('timestamp'):
                    context_parts.append(f"   Time: {log.get('timestamp')}")
        
        return "\n".join(context_parts)
    
    def _detailed_fusion(self, incident_data: Dict[str, Any]) -> str:
        """Detailed fusion template - includes all available information"""
        service_name = incident_data.get('service_name', 'unknown')
        error_logs = incident_data.get('error_logs', [])
        service_profile = incident_data.get('service_profile', {})
        incident_info = incident_data.get('incident_data', {})
        
        context_parts = []
        
        # Detailed service information
        context_parts.append("=" * 60)
        context_parts.append("SERVICE PROFILE")
        context_parts.append("=" * 60)
        
        if service_profile:
            for key, value in service_profile.items():
                if isinstance(value, list):
                    context_parts.append(f"{key.upper()}: {', '.join(str(v) for v in value)}")
                else:
                    context_parts.append(f"{key.upper()}: {value}")
        else:
            context_parts.append(f"Service Name: {service_name}")
            context_parts.append("No detailed profile available")
        
        # Detailed incident information
        if incident_info:
            context_parts.append("\n" + "=" * 60)
            context_parts.append("INCIDENT DETAILS")
            context_parts.append("=" * 60)
            for key, value in incident_info.items():
                if value:  # Only include non-empty values
                    context_parts.append(f"{key.upper()}: {value}")
        
        # Detailed error information
        context_parts.append("\n" + "=" * 60)
        context_parts.append("ERROR LOGS")
        context_parts.append("=" * 60)
        
        if error_logs:
            for i, log in enumerate(error_logs, 1):
                context_parts.append(f"\nError #{i}:")
                for key, value in log.items():
                    if key != 'log_id':  # Skip internal ID
                        context_parts.append(f"  {key.upper()}: {value}")
        else:
            context_parts.append("No error logs available")
        
        # Metadata
        context_parts.append("\n" + "=" * 60)
        context_parts.append("METADATA")
        context_parts.append("=" * 60)
        context_parts.append(f"Query Timestamp: {incident_data.get('query_timestamp', 'unknown')}")
        context_parts.append(f"Total Errors: {len(error_logs)}")
        
        return "\n".join(context_parts)
    
    def _compact_fusion(self, incident_data: Dict[str, Any]) -> str:
        """Compact fusion template - minimal information for quick search"""
        service_name = incident_data.get('service_name', 'unknown')
        error_logs = incident_data.get('error_logs', [])
        service_profile = incident_data.get('service_profile', {})
        incident_info = incident_data.get('incident_data', {})
        
        # Extract key error patterns
        error_messages = [log.get('error_message', '') for log in error_logs]
        error_codes = [log.get('error_code', '') for log in error_logs]
        
        context_parts = []
        
        # Service summary
        if service_profile:
            context_parts.append(f"{service_profile.get('name', service_name)} {service_profile.get('version', '')} {service_profile.get('environment', '')}")
        else:
            context_parts.append(service_name)
        
        # Incident summary
        if incident_info:
            context_parts.append(f"{incident_info.get('severity', '')} {incident_info.get('title', '')}")
        
        # Error summary
        if error_messages:
            context_parts.append("Errors: " + "; ".join(error_messages[:3]))
        
        if error_codes:
            context_parts.append("Codes: " + ", ".join(error_codes[:3]))
        
        return " | ".join(context_parts)
    
    def build_search_query(self, incident_data: Dict[str, Any], additional_keywords: List[str] = None) -> str:
        """
        Build optimized search query for vector similarity search
        
        Args:
            incident_data: Dictionary containing error_logs and service_profile
            additional_keywords: Additional keywords to include in search
        
        Returns:
            Optimized search query string
        """
        service_name = incident_data.get('service_name', 'unknown')
        error_logs = incident_data.get('error_logs', [])
        service_profile = incident_data.get('service_profile', {})
        incident_info = incident_data.get('incident_data', {})
        
        # Extract key terms for search
        search_terms = []
        
        # Service-related terms
        search_terms.append(service_name)
        if service_profile:
            search_terms.append(service_profile.get('team', ''))
            search_terms.extend(service_profile.get('dependencies', []))
        
        # Incident-related terms
        if incident_info:
            search_terms.append(incident_info.get('title', ''))
            search_terms.append(incident_info.get('description', ''))
        
        # Error-related terms
        for log in error_logs[:3]:  # Focus on most recent errors
            search_terms.append(log.get('error_message', ''))
            search_terms.append(log.get('error_code', ''))
        
        # Add additional keywords if provided
        if additional_keywords:
            search_terms.extend(additional_keywords)
        
        # Clean and deduplicate terms
        search_terms = [term.strip().lower() for term in search_terms if term and term.strip()]
        search_terms = list(set(search_terms))  # Remove duplicates
        
        return " ".join(search_terms)
    
    def enrich_with_incident_metadata(self, context: str, incident_metadata: Dict[str, Any]) -> str:
        """
        Enrich context with additional incident metadata
        
        Args:
            context: Existing context string
            incident_metadata: Additional incident information
        
        Returns:
            Enriched context string
        """
        enrichment_parts = [context]
        
        if incident_metadata.get('severity'):
            enrichment_parts.append(f"Incident Severity: {incident_metadata['severity']}")
        
        if incident_metadata.get('affected_users'):
            enrichment_parts.append(f"Affected Users: {incident_metadata['affected_users']}")
        
        if incident_metadata.get('business_impact'):
            enrichment_parts.append(f"Business Impact: {incident_metadata['business_impact']}")
        
        return "\n".join(enrichment_parts)


# Convenience function for quick context building
def build_incident_context(incident_data: Dict[str, Any], fusion_type: str = 'standard') -> str:
    """
    Convenience function to build incident context
    
    Args:
        incident_data: Dictionary containing error_logs and service_profile
        fusion_type: Type of fusion template
    
    Returns:
        Unified context string
    """
    builder = ContextFusionBuilder()
    return builder.build_context(incident_data, fusion_type)