#!/usr/bin/env python3
"""
Incident Triage System - Main Entry Point

This system integrates MySQL data, ChromaDB vector search, and Ollama LLM
to provide intelligent incident resolution suggestions.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database_manager import DatabaseManager, SAMPLE_INCIDENTS
from context_fusion import ContextFusionBuilder
from vector_store import KnowledgeBaseManager
from synthesis import IncidentSolutionGenerator


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def initialize_system():
    """Initialize all system components"""
    print_section("INITIALIZING INCIDENT TRIAGE SYSTEM")
    
    # Initialize database manager
    print("Connecting to databases...")
    db_manager = DatabaseManager()
    
    # Initialize knowledge base
    print("Initializing knowledge base...")
    kb_manager = KnowledgeBaseManager(kb_directory="./kb")
    kb_success = kb_manager.initialize_knowledge_base()
    
    if not kb_success:
        print("✗ Failed to initialize knowledge base")
        return None, None, None
    
    # Initialize solution generator
    print("Initializing LLM solution generator...")
    solution_generator = IncidentSolutionGenerator(model_name="qwen2.5-coder")
    
    # Test LLM connection
    print("Testing Ollama connection...")
    if not solution_generator.synthesizer.test_connection():
        print("✗ Ollama connection failed. Please ensure Ollama is running.")
        return None, None, None
    
    print("✓ System initialized successfully")
    return db_manager, kb_manager, solution_generator


def process_incident(
    service_name: str, 
    incident_id: str = None,
    db_manager = None,
    kb_manager = None,
    solution_generator = None
):
    """Process a single incident and generate solution"""
    print_section(f"PROCESSING INCIDENT: {service_name}")
    
    # Get incident context from database
    print("Gathering incident context...")
    incident_context = db_manager.get_incident_context(service_name, incident_id)
    
    # Display incident information
    print(f"\nService: {incident_context['service_name']}")
    if incident_context['incident_data']:
        print(f"Incident: {incident_context['incident_data']['title']}")
        print(f"Severity: {incident_context['incident_data']['severity']}")
        print(f"Affected Users: {incident_context['incident_data']['affected_users']}")
    
    print(f"Error Logs Found: {len(incident_context['error_logs'])}")
    for i, log in enumerate(incident_context['error_logs'][:3], 1):
        print(f"  {i}. {log['error_code']}: {log['error_message']}")
    
    # Build search query
    print("\nBuilding search query...")
    context_builder = ContextFusionBuilder()
    search_query = context_builder.build_search_query(incident_context)
    print(f"Search Query: {search_query[:100]}...")
    
    # Search knowledge base
    print("Searching knowledge base...")
    kb_results = kb_manager.search_knowledge_base(search_query, n_results=3)
    print(f"Found {len(kb_results)} relevant KB articles")
    
    for i, result in enumerate(kb_results, 1):
        source = result.get('metadata', {}).get('source_file', 'Unknown')
        print(f"  {i}. {source}")
    
    # Generate solution
    print("\nGenerating solution with LLM...")
    solution_result = solution_generator.generate_solution(incident_context, kb_results)
    
    if solution_result['success']:
        print("✓ Solution generated successfully")
        return solution_result['solution']
    else:
        print(f"✗ Solution generation failed: {solution_result.get('error', 'Unknown error')}")
        return None


def interactive_mode(db_manager, kb_manager, solution_generator):
    """Run the system in interactive mode"""
    print_section("INTERACTIVE MODE")
    print("Enter service names to process incidents (or 'quit' to exit)")
    
    while True:
        try:
            service_name = input("\nEnter service name: ").strip()
            
            if service_name.lower() in ['quit', 'exit', 'q']:
                print("Exiting interactive mode...")
                break
            
            if not service_name:
                print("Please enter a service name")
                continue
            
            # Process the incident
            solution = process_incident(
                service_name, 
                db_manager=db_manager,
                kb_manager=kb_manager,
                solution_generator=solution_generator
            )
            
            if solution:
                print_section("GENERATED SOLUTION")
                print(solution)
                print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error processing incident: {e}")


def demo_mode(db_manager, kb_manager, solution_generator):
    """Run the system in demo mode with sample incidents"""
    print_section("DEMO MODE - SAMPLE INCIDENTS")
    
    for i, sample in enumerate(SAMPLE_INCIDENTS, 1):
        print(f"\n--- Sample Incident {i}/{len(SAMPLE_INCIDENTS)} ---")
        print(f"Service: {sample['service_name']}")
        print(f"Description: {sample['description']}")
        
        # Process the sample incident
        solution = process_incident(
            sample['service_name'],
            db_manager=db_manager,
            kb_manager=kb_manager,
            solution_generator=solution_generator
        )
        
        if solution:
            print_section("GENERATED SOLUTION")
            print(solution)
            print("\n" + "=" * 60)
        
        # Ask user if they want to continue
        if i < len(SAMPLE_INCIDENTS):
            continue_demo = input("\nContinue to next sample? (y/n): ").strip().lower()
            if continue_demo != 'y':
                break


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  INCIDENT TRIAGE SYSTEM                           ║
║         MySQL + ChromaDB + Ollama LLM Integration                 ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize system components
    db_manager, kb_manager, solution_generator = initialize_system()
    
    if not all([db_manager, kb_manager, solution_generator]):
        print("✗ System initialization failed. Please check the errors above.")
        return
    
    # Display system status
    print_section("SYSTEM STATUS")
    kb_stats = kb_manager.get_stats()
    print(f"Knowledge Base: {kb_stats['total_documents']} documents")
    print(f"Collection: {kb_stats['collection_name']}")
    print(f"LLM Model: {solution_generator.synthesizer.model_name}")
    
    # Choose mode
    print_section("SELECT MODE")
    print("1. Demo Mode (process sample incidents)")
    print("2. Interactive Mode (enter custom incidents)")
    print("3. Quick Test (single incident)")
    
    try:
        choice = input("\nSelect mode (1-3): ").strip()
        
        if choice == '1':
            demo_mode(db_manager, kb_manager, solution_generator)
        elif choice == '2':
            interactive_mode(db_manager, kb_manager, solution_generator)
        elif choice == '3':
            service_name = input("Enter service name: ").strip()
            if service_name:
                solution = process_incident(
                    service_name,
                    db_manager=db_manager,
                    kb_manager=kb_manager,
                    solution_generator=solution_generator
                )
                if solution:
                    print_section("GENERATED SOLUTION")
                    print(solution)
            else:
                print("No service name provided")
        else:
            print("Invalid choice. Please run the program again.")
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        if db_manager:
            db_manager.close()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()