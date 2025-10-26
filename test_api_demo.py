"""
API Demo Script - PathRAG Court Simulator
Tests the workflow endpoint with a sample case
Enhanced with clear argument display and formatted output
"""
import requests
import json
import sys
import textwrap
from datetime import datetime

# Sample case for testing
SAMPLE_CASE = """Case File

Case Title: State vs. Rohan Malhotra

Case Summary:
Rohan Malhotra, a 28-year-old entrepreneur, is accused of defamation under Section 499 
of the Indian Penal Code (IPC) and cyber harassment under the Information Technology Act, 2000. 
The case pertains to Rohan allegedly posting defamatory and harassing statements about 
Meera Sharma, a 30-year-old journalist, on social media platforms. Rohan denies the charges, 
claiming his account was hacked at the time the posts were made.

Case Details:
1. Date of Incident: December 10, 2023
2. Platform: Twitter/X and Instagram
3. Nature of Posts: Defamatory statements about journalist's integrity and professional conduct
4. Defense Claim: Account was compromised, posts made by unauthorized access
5. Evidence: Login activity logs showing unusual IP addresses

Defense Position:
1. No intent to harm - account was compromised by hackers
2. Technical evidence shows unusual login activity from foreign IP addresses
3. Rohan has good character with no prior offenses or complaints
4. The posts don't match Rohan's typical writing style or tone
5. Rohan immediately reported the incident when discovered
6. Expert testimony available on cybersecurity breach

Prosecution Claims:
1. Posts were made from Rohan's verified account
2. Content specifically targeted the victim's professional reputation
3. Timing coincides with a business dispute between parties
4. No evidence of account compromise at the time

Request:
Please analyze this case from a defense perspective and provide strong legal arguments 
considering IPC Section 499 (Defamation) and IT Act 2000 provisions.
"""

def format_agent_output(agent_name: str, content, iteration: int):
    """Format agent output with visual clarity and proper wrapping"""
    
    # Handle case where content might be a list or other type
    if isinstance(content, list):
        # If it's a list, join the elements
        content = ' '.join(str(item) for item in content)
    elif not isinstance(content, str):
        # Convert to string if it's not already
        content = str(content)
    
    # Agent-specific symbols and colors
    symbols = {
        "judge": "⚖️ ",
        "lawyer": "🛡️ ",
        "prosecutor": "⚔️ ",
        "retriever": "📚",
        "kanoon_fetcher": "🔍",
        "web_searcher": "🌐",
        "verdict": "🏛️ "
    }
    
    symbol = symbols.get(agent_name, "•")
    
    # Check for verdict (now safe since content is a string)
    is_verdict = (agent_name == "verdict" or "Given Verdict" in content or 
                  "VERDICT DELIVERED" in content.upper() or "GUILTY" in content.upper() or 
                  "NOT GUILTY" in content.upper())
    
    print("\n" + "=" * 80)
    if is_verdict or agent_name == "verdict":
        print(f"🏛️  FINAL VERDICT - JUDGE - Iteration {iteration} 🏛️")
    else:
        print(f"{symbol} {agent_name.upper()} - Iteration {iteration}")
    print("=" * 80)
    
    # Wrap and display content
    if content and len(content.strip()) > 0:
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Wrap each paragraph to 78 characters
                wrapped = textwrap.fill(para.strip(), width=78)
                print(wrapped)
                print()  # Add spacing between paragraphs
    else:
        print("(No content to display)")
    
    print("-" * 80)


def print_verdict_summary(verdict_content: str):
    """Print highlighted final verdict"""
    print("\n" + "=" * 80)
    print("🏛️  FINAL COURT VERDICT  🏛️")
    print("=" * 80)
    
    # Wrap verdict text
    wrapped = textwrap.fill(verdict_content, width=78)
    print(wrapped)
    
    print("=" * 80 + "\n")


def format_progress_message(iteration: int, agent_name: str, next_agent: str, elapsed: float):
    """Format compact progress message"""
    return f"[Iter {iteration:2d}] {agent_name:15s} → {next_agent:15s} ({elapsed:6.1f}s)"

def test_api():
    """Test the workflow API endpoint with enhanced output display"""
    
    # API endpoint
    url = "http://localhost:8000/stream_workflow"
    
    # Payload
    payload = {
        "user_prompt": SAMPLE_CASE
    }
    
    print("\n" + "=" * 80)
    print("PathRAG Court Simulator - API Demo")
    print("=" * 80)
    print("\nCase Summary:")
    print("-" * 80)
    print("Defendant: Rohan Malhotra (28, Entrepreneur)")
    print("Charges: Defamation (IPC 499) + Cyber Harassment (IT Act 2000)")
    print("Defense: Account hacking/compromise")
    print("-" * 80)
    
    print("\n[CLIENT] Sending case to API...")
    print(f"[CLIENT] Endpoint: {url}")
    print(f"[CLIENT] Payload size: {len(json.dumps(payload))} bytes")
    print(f"[CLIENT] Maximum iterations: 25")
    print(f"[CLIENT] Timeout: 1800 seconds (30 minutes)")
    
    try:
        import time
        request_start = time.time()
        
        # Send request with streaming enabled
        print("\n[CLIENT] Establishing connection...")
        response = requests.post(url, json=payload, stream=True, timeout=1800)
        
        if response.status_code != 200:
            print(f"\n[ERROR] API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        connection_time = time.time() - request_start
        print(f"[CLIENT] Connection established in {connection_time:.2f}s")
        print("[CLIENT] Streaming workflow responses...")
        print("[NOTE] First agent (Kanoon Fetcher) may take 3-5 minutes")
        print("\n" + "=" * 80)
        print("COURTROOM SIMULATION BEGINS")
        print("=" * 80 + "\n")
        
        event_count = 0
        last_event_time = time.time()
        displayed_agents = set()  # Track which agents we've displayed
        final_verdict = None
        
        # Stream responses
        for line in response.iter_lines():
            if line:
                current_time = time.time()
                time_since_last = current_time - last_event_time
                
                # Decode the line
                line_text = line.decode('utf-8')
                
                # Parse SSE format (data: {...})
                if line_text.startswith('data: '):
                    event_count += 1
                    elapsed = current_time - request_start
                    
                    try:
                        # Parse JSON data
                        data = json.loads(line_text[6:])
                        
                        status = data.get('status', 'unknown')
                        agent_name = data.get('agent_name', 'unknown')
                        iteration = data.get('iteration', event_count)
                        next_agent = data.get('next_agent', 'unknown')
                        agent_message = data.get('agent_message', '')
                        
                        # Handle agent_message being a list or other types
                        if isinstance(agent_message, list):
                            agent_message = ' '.join(str(item) for item in agent_message)
                        elif not isinstance(agent_message, str):
                            agent_message = str(agent_message) if agent_message else ''
                        
                        # Display agent arguments (main feature!)
                        if status == "progress" and agent_message and len(agent_message.strip()) > 0:
                            # Show ALL main courtroom actors (judge, lawyer, prosecutor, verdict)
                            if agent_name in ['judge', 'lawyer', 'prosecutor', 'verdict']:
                                format_agent_output(agent_name, agent_message, iteration)
                                displayed_agents.add(agent_name)
                                
                                # DEBUG: Log lawyer visibility
                                if agent_name == 'lawyer':
                                    print(f"\n[DEBUG] Lawyer message displayed at iteration {iteration}")
                                    print(f"[DEBUG] Message length: {len(agent_message)} characters")
                            else:
                                # Show compact progress for support agents
                                print(format_progress_message(iteration, agent_name, next_agent, elapsed))
                        elif status == "progress":
                            # Show compact progress if no message content
                            print(format_progress_message(iteration, agent_name, next_agent, elapsed))
                            
                            # DEBUG: Check if lawyer had empty content
                            if agent_name == 'lawyer':
                                print(f"\n[DEBUG WARNING] Lawyer at iteration {iteration} had empty/no message!")
                                print(f"[DEBUG] agent_message value: '{agent_message}'")
                        
                        # Store verdict when we see it
                        if status == "progress" and agent_name == "verdict" and agent_message:
                            final_verdict = agent_message
                            # Already displayed above via format_agent_output
                        
                        # Check if workflow is complete
                        if status == "done":
                            # Display final verdict if available
                            if final_verdict:
                                print_verdict_summary(final_verdict)
                            elif agent_message and ("verdict" in agent_message.lower() or "GUILTY" in agent_message.upper() or "NOT GUILTY" in agent_message.upper()):
                                final_verdict = agent_message
                                print_verdict_summary(final_verdict)
                            
                            print("\n" + "=" * 80)
                            print("WORKFLOW COMPLETE")
                            print("=" * 80)
                            break
                        
                        if status == "error":
                            print("\n" + "=" * 80)
                            print("WORKFLOW ERROR")
                            print("=" * 80)
                            print(f"Error: {data.get('content', 'Unknown error')}")
                            break
                        
                        last_event_time = current_time
                        
                    except json.JSONDecodeError as e:
                        print(f"[WARNING] Could not parse JSON: {e}")
                        print(f"Raw line: {line_text[:200]}")
                    except Exception as e:
                        print(f"[WARNING] Error processing event: {e}")
                        print(f"Event data: {line_text[:200]}")
        
        total_time = time.time() - request_start
        print(f"\n[SUMMARY]")
        print(f"  Total iterations: {event_count}")
        print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"  Agents displayed: {', '.join(sorted(displayed_agents))}")
        print("\n[CLIENT] Demo completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server")
        print("Make sure the server is running:")
        print("  python app.py")
        sys.exit(1)
        
    except requests.exceptions.Timeout:
        print("\n[WARNING] Request timed out after 30 minutes")
        print("The workflow might still be running on the server.")
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Demo interrupted by user (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main function"""
    print("\n[CLIENT] Starting API Demo...\n")
    
    # Check if user wants to use custom case file
    if len(sys.argv) > 1:
        case_file = sys.argv[1]
        print(f"[CLIENT] Loading case from file: {case_file}")
        
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                global SAMPLE_CASE
                SAMPLE_CASE = f.read()
            print(f"[CLIENT] Loaded {len(SAMPLE_CASE)} characters from file\n")
        except FileNotFoundError:
            print(f"[ERROR] File '{case_file}' not found")
            print("[CLIENT] Using default sample case instead\n")
        except Exception as e:
            print(f"[ERROR] Error reading file: {e}")
            print("[CLIENT] Using default sample case instead\n")
    
    # Run the test
    test_api()

if __name__ == "__main__":
    main()
