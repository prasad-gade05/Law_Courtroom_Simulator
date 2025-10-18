"""
API Demo Script - PathRAG Court Simulator
Tests the workflow endpoint with a sample case
"""
import requests
import json
import sys

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

def test_api():
    """Test the workflow API endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/stream_workflow"
    
    # Payload
    payload = {
        "user_prompt": SAMPLE_CASE
    }
    
    print("=" * 80)
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
        print("[NOTE] First agent (Kanoon Fetcher) may take 3-5 minutes (external API)")
        print("\n" + "=" * 80)
        print("WORKFLOW EXECUTION:")
        print("=" * 80 + "\n")
        
        event_count = 0
        last_update = ""
        last_event_time = time.time()
        
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
                        content = str(data.get('content', ''))
                        extra_data = data.get('data', '')
                        
                        # Show compact progress
                        print(f"\n[Event #{event_count}] Time: {elapsed:.1f}s (delta: {time_since_last:.1f}s)")
                        print(f"  Status: {status}")
                        
                        if status == "progress":
                            # Extract agent name if present
                            if "Agent '" in content:
                                agent_name = content.split("'")[1] if "'" in content else "unknown"
                                print(f"  Agent: {agent_name}")
                                if extra_data:
                                    print(f"  Info: {extra_data}")
                            else:
                                if content != last_update:
                                    print(f"  Content: {content[:150]}")
                                    last_update = content
                        else:
                            # Display full content for non-progress events
                            if len(content) > 200:
                                print(f"  Content: {content[:200]}...")
                            else:
                                print(f"  Content: {content}")
                        
                        # Check if workflow is complete
                        if status == "done":
                            print("\n" + "=" * 80)
                            print("WORKFLOW COMPLETE")
                            print("=" * 80)
                            break
                        
                        if status == "error":
                            print("\n" + "=" * 80)
                            print("WORKFLOW ERROR")
                            print("=" * 80)
                            break
                        
                        last_event_time = current_time
                        
                    except json.JSONDecodeError as e:
                        print(f"[WARNING] Could not parse JSON: {e}")
                        print(f"Raw line: {line_text[:200]}")
        
        total_time = time.time() - request_start
        print(f"\n[SUMMARY]")
        print(f"  Total events received: {event_count}")
        print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
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
