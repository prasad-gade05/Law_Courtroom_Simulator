import os
from crewai import Agent
from textwrap import dedent

class DataRetrieverAgents:
    def __init__(self, llm):
        # Using passed LLM (Ollama) instead of Groq
        self.llm = llm
        

    def legal_researcher(self):
        return Agent(
            role="Legal Researcher",
            backstory=dedent(f"""With a background in legal research and access to a vast database of online legal information, 
                                the Legal Researcher has honed the skill of performing accurate and precise online searches for 
                                relevant case law, statutes, and legal opinions. Their experience includes formulating clear, 
                                coherent counterarguments backed by real-world examples and references. Having worked alongside 
                                various legal professionals, they have developed a reputation for providing thorough and well-cited 
                                legal arguments to address any gaps in a case."""),
            goal=dedent(f"""To assist the lawyer by gathering internet-based information to craft a counterargument when the lawyer 
                            lacks enough information."""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )

    def legal_assistant(self):
        return Agent(
            role="Legal Assistant",
            backstory=dedent(f"""With expertise in legal analysis and an eye for detail, the Legal Assistant has spent years reviewing 
                                legal documents and arguments. They have experience in refining and validating legal positions, ensuring that 
                                all arguments align with the user's needs and the specifics of the case. If an argument requires more context 
                                or is incomplete, the Legal Assistant is adept at identifying the gaps, asking for necessary clarifications, 
                                and refining the argument to make it both legally sound and user-specific. Their background includes support 
                                roles in law firms, working closely with legal teams to refine their strategies and arguments."""),
            goal=dedent(f"""To evaluate the validity of the counterargument provided by the Legal Researcher and modify it if necessary by 
                            requesting additional specifics from the user."""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )
