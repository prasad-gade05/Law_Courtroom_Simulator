import asyncio
import aiohttp
import streamlit as st
import json
import re
from pathlib import Path

# Create private_documents directory if it doesn't exist
UPLOAD_DIR = Path("private_documents")
UPLOAD_DIR.mkdir(exist_ok=True)

async def fetch_stream(user_prompt):
    url = "http://localhost:8000/stream_workflow"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"user_prompt": user_prompt}) as response:
            if response.status != 200:
                st.error(f"Failed to connect: {response.status}")
                return
            async for line in response.content:
                if line:
                    yield line.decode("utf-8")

st.title("🏛️ PathRAG Court Simulator")

uploaded_files = st.file_uploader(
    "Upload case-related documents",
    accept_multiple_files=True,
    type=['pdf', 'txt', 'doc', 'docx']
)

# Handle file uploads
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Create safe filename
        file_path = UPLOAD_DIR / uploaded_file.name
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved: {uploaded_file.name}")

user_prompt = st.text_area("Enter your case details:", """Case File

Case Title
State vs. Rohan Malhotra

Case Summary
Rohan Malhotra, a 28-year-old entrepreneur, is accused of defamation under Section 499 of the Indian Penal Code (IPC) and cyber harassment under the Information Technology Act, 2000. The case pertains to Rohan allegedly posting defamatory and harassing statements about Meera Sharma, a 30-year-old journalist, on social media platforms. Rohan denies the charges, claiming his account was hacked at the time the posts were made.

Case Details
Incident Description:
On May 20, 2024, Meera Sharma filed a complaint with the cybercrime division, alleging that Rohan Malhotra made a series of defamatory posts about her on Twitter and Instagram. The posts accused Meera of biased reporting, bribery, and professional misconduct, damaging her reputation among peers and the public.
Rohan Malhotra has stated that he did not make the posts and believes his accounts were compromised. He claims that he noticed suspicious activity on his accounts around the time the posts were made.
Timeline of Events:
May 19, 2024, 8:00 PM: First defamatory tweet posted.
May 19, 2024, 8:30 PM: Instagram story containing similar allegations shared.
May 20, 2024, 9:00 AM: Meera Sharma files a complaint.
May 20, 2024, 11:00 AM: Rohan reports to the cybercrime division, claiming his accounts were hacked.
Evidence:
Screenshots of Posts: Captured by Meera Sharma before they were deleted.
Digital Forensics Report: Analysis of Rohan's devices shows no direct evidence of his involvement but logs indicate suspicious login activity from an unknown IP address.
Witness Testimony: Ravi Verma, a friend of Rohan, states that Rohan mentioned concerns about his social media accounts prior to the incident.
Impact Statement: Meera Sharma has submitted a statement detailing the professional and emotional impact caused by the defamatory posts.
Charges:
Section 499, IPC (Defamation):
Whoever, by words, either spoken or intended to be read, or by signs or visible representations, makes or publishes any imputation concerning any person intending to harm, or knowing or having reason to believe that such imputation will harm, the reputation of such person, is said to defame that person.

Section 66A, IT Act (Cyber Harassment):
Punishment for sending offensive messages through communication service, etc., which cause annoyance or insult.
""", height=200)


def parse_current_and_message(content: str):
    """
    Extract the current (e.g., prosecutor, judge) and message from the raw `repr` string.
    Infers "current" from the first key in the dictionary representation of the content.
    """
    # Match the first word (key) as the "current"
    current_pattern = r"^\{'(\w+)'"
    message_pattern = r"content=['\"](.*?)['\"], additional_kwargs"

    current_match = re.search(current_pattern, content)
    message_match = re.search(message_pattern, content, re.DOTALL)

    # Extract current and message
    current = current_match.group(1) if current_match else "N/A"
    message = message_match.group(1) if message_match else "N/A"

    return current, message

if st.button("Run Workflow"):    
    # Placeholders for streaming animation and results
    animation_placeholder = st.empty()
    agent_placeholder = st.empty()
    message_placeholder = st.empty()

    async def animate_loading():
        """
        Cycles through . .. ... to create a loading animation.
        """
        while True:
            for dots in [".", "..", "..."]:
                animation_placeholder.write(f"Streaming results{dots}")
                await asyncio.sleep(0.5)

    async def fetch_and_process_stream():
        animation_task = asyncio.create_task(animate_loading())
        try:
            async for event in fetch_stream(user_prompt=user_prompt):
                if event.startswith("data: "):
                    # Remove `data: ` prefix and parse JSON
                    raw_data = event[6:].strip()
                    try:
                        parsed_data = json.loads(raw_data)
                        content = parsed_data.get("content", "")

                        # Parse the "Agent" (current) and message
                        current, message = parse_current_and_message(content)
                        agent_placeholder.write(f"Agent: {current}")
                        
                        # Convert raw \n into <br> for HTML rendering
                        formatted_message = message.replace(r'\n', '\n').replace('\n', '<br>')
                        
                        # Render using st.markdown with unsafe_allow_html=True
                        message_placeholder.markdown(formatted_message, unsafe_allow_html=True)
                    except json.JSONDecodeError as e:
                        st.error(f"Error decoding JSON: {e}")
                else:
                    pass
        except Exception as e:
            st.error(f"Error streaming workflow: {e}")
        finally:
            animation_task.cancel()  # Stop the animation once streaming is complete

    asyncio.run(fetch_and_process_stream())
