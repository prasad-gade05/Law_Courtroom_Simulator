#!/usr/bin/env python3
"""
API Demo Test Script for Lex Simulacra Courtroom Simulator

This script demonstrates how to test the courtroom simulation via terminal
without using the UI. It connects to the FastAPI backend and streams the
workflow execution.

Usage:
    python test_api_demo.py [case_file.txt]
    
    If no case file is provided, uses sample_case.txt by default.
"""

import sys
import json
import time
import requests
from pathlib import Path


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text, char="="):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{char * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{char * 80}{Colors.ENDC}\n")


def print_agent(agent_name, iteration, text):
    """Print agent output with formatting"""
    agent_colors = {
        "lawyer": Colors.OKBLUE,
        "prosecutor": Colors.FAIL,
        "judge": Colors.WARNING,
        "verdict": Colors.OKGREEN,
        "initial_retriever": Colors.OKCYAN,
        "kanoon_fetcher": Colors.OKCYAN,
        "document_summarizer": Colors.OKCYAN
    }
    
    agent_emojis = {
        "lawyer": "🛡️  DEFENSE LAWYER",
        "prosecutor": "⚔️  PROSECUTOR",
        "judge": "⚖️  JUDGE",
        "verdict": "🏛️  FINAL VERDICT",
        "initial_retriever": "📚 INITIAL RETRIEVER",
        "kanoon_fetcher": "⚖️  KANOON FETCHER",
        "document_summarizer": "📄 DOCUMENT SUMMARIZER"
    }
    
    color = agent_colors.get(agent_name, Colors.ENDC)
    emoji = agent_emojis.get(agent_name, agent_name.upper())
    
    print(f"\n{color}{'=' * 80}{Colors.ENDC}")
    print(f"{color}{emoji} - Iteration {iteration}{Colors.ENDC}")
    print(f"{color}{'=' * 80}{Colors.ENDC}")
    print(text)
    print(f"{color}{'-' * 80}{Colors.ENDC}\n")


def load_case_file(filepath):
    """Load case description from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: Case file '{filepath}' not found!{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error reading case file: {e}{Colors.ENDC}")
        sys.exit(1)


def stream_workflow(case_description, max_iterations=25, timeout=1800):
    """
    Stream the courtroom workflow from the API
    
    Args:
        case_description: The case details as string
        max_iterations: Maximum number of iterations (default: 25)
        timeout: Request timeout in seconds (default: 1800 = 30 minutes)
    """
    
    url = "http://localhost:8000/stream_workflow"
    
    payload = {
        "case_description": case_description,
        "max_iterations": max_iterations
    }
    
    print(f"{Colors.OKCYAN}[CLIENT] Starting API Demo...{Colors.ENDC}\n")
    print(f"{Colors.OKCYAN}[CLIENT] Loading case from file{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[CLIENT] Loaded {len(case_description)} characters from file{Colors.ENDC}\n")
    
    # Print case summary
    lines = case_description.split('\n')
    if len(lines) > 5:
        summary = '\n'.join(lines[:5])
        print_header("Lex Simulacra - Law Courtroom Simulator - API Demo")
        print("Case Summary:")
        print("-" * 80)
        print(summary)
        if len(lines) > 5:
            print(f"... ({len(lines) - 5} more lines)")
        print("-" * 80)
    
    print(f"\n{Colors.OKCYAN}[CLIENT] Sending case to API...{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[CLIENT] Endpoint: {url}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[CLIENT] Payload size: {len(json.dumps(payload))} bytes{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[CLIENT] Maximum iterations: {max_iterations}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[CLIENT] Timeout: {timeout} seconds ({timeout // 60} minutes){Colors.ENDC}\n")
    
    try:
        print(f"{Colors.OKCYAN}[CLIENT] Establishing connection...{Colors.ENDC}")
        start_time = time.time()
        
        response = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=timeout
        )
        
        connection_time = time.time() - start_time
        print(f"{Colors.OKGREEN}[CLIENT] Connection established in {connection_time:.2f}s{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[CLIENT] Streaming workflow responses...{Colors.ENDC}")
        print(f"{Colors.WARNING}[NOTE] First agent (Kanoon Fetcher) may take 3-5 minutes{Colors.ENDC}\n")
        
        print_header("COURTROOM SIMULATION BEGINS")
        
        iteration_count = 0
        agents_seen = set()
        last_time = start_time
        
        # Track progress
        progress_markers = []
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                # Skip SSE prefixes
                if line.startswith('data: '):
                    line = line[6:]
                
                # Skip empty lines or metadata
                if not line or line.startswith('[DONE]'):
                    continue
                
                try:
                    event = json.loads(line)
                    
                    # Handle different event types
                    if event.get('type') == 'agent_response':
                        agent_name = event.get('agent', 'unknown')
                        iteration = event.get('iteration', 0)
                        content = event.get('content', '')
                        next_agent = event.get('next', 'unknown')
                        
                        current_time = time.time()
                        elapsed = current_time - last_time
                        last_time = current_time
                        
                        # Print progress marker
                        progress_markers.append(f"[Iter {iteration:2d}] {agent_name:15s} → {next_agent:15s} ({elapsed:6.1f}s)")
                        
                        # Only show last 10 progress markers
                        if len(progress_markers) <= 10:
                            print(progress_markers[-1])
                        
                        iteration_count = max(iteration_count, iteration)
                        agents_seen.add(agent_name)
                        
                        # Print full agent response for important agents
                        if agent_name in ['lawyer', 'prosecutor', 'judge', 'verdict']:
                            print_agent(agent_name, iteration, content)
                    
                    elif event.get('type') == 'progress':
                        # Progress updates
                        message = event.get('message', '')
                        if message:
                            print(f"{Colors.OKCYAN}[PROGRESS] {message}{Colors.ENDC}")
                    
                    elif event.get('type') == 'error':
                        error_msg = event.get('message', 'Unknown error')
                        print(f"{Colors.FAIL}[ERROR] {error_msg}{Colors.ENDC}")
                        break
                    
                    elif event.get('type') == 'complete':
                        print_header("WORKFLOW COMPLETE")
                        print(f"{Colors.OKGREEN}[SUCCESS] Simulation completed successfully!{Colors.ENDC}")
                        
                except json.JSONDecodeError:
                    # Skip non-JSON lines
                    continue
        
        total_time = time.time() - start_time
        
        # Print summary
        print_header("SUMMARY", "=")
        print(f"  Total iterations: {iteration_count}")
        print(f"  Total time: {total_time:.1f}s ({total_time / 60:.1f} minutes)")
        print(f"  Agents displayed: {', '.join(sorted(agents_seen))}")
        print()
        
        print(f"{Colors.OKGREEN}[CLIENT] Demo completed successfully!{Colors.ENDC}")
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}[ERROR] Cannot connect to backend API at {url}{Colors.ENDC}")
        print(f"{Colors.WARNING}[HINT] Make sure the backend is running: python app.py{Colors.ENDC}")
        sys.exit(1)
    
    except requests.exceptions.Timeout:
        print(f"{Colors.FAIL}[ERROR] Request timed out after {timeout} seconds{Colors.ENDC}")
        print(f"{Colors.WARNING}[HINT] Try increasing the timeout or check backend logs{Colors.ENDC}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[INTERRUPTED] Simulation interrupted by user{Colors.ENDC}")
        sys.exit(0)
    
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point"""
    
    # Get case file from command line or use default
    if len(sys.argv) > 1:
        case_file = sys.argv[1]
    else:
        case_file = "sample_case.txt"
        print(f"{Colors.WARNING}[INFO] No case file specified, using default: {case_file}{Colors.ENDC}")
    
    # Load case description
    case_description = load_case_file(case_file)
    
    # Stream the workflow
    stream_workflow(case_description)


if __name__ == "__main__":
    main()
