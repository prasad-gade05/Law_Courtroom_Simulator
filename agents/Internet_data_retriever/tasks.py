from crewai import Task
from textwrap import dedent
from .tools.search_tool import SearchTools

class RetrievalTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def generate_search_queries(self, agent, argument):
        return Task(description=dedent(f'''
        **Task**: Generate Search Queries  
        **Description**: Formulate precise and relevant search queries to find counterarguments, examples, and supporting information
                         to counter the provided argument using internet resources. Your final output must be a list of search queries 
                         that can be used to retrieve relevant information.

        **Parameters**:  
        - Argument: {argument}

        **Note**: Focus on accuracy and relevance while creating queries. Ensure the queries are designed to fetch 
                  legal examples, laws, or precedents. {self.__tip_section()}
        '''),
        agent=agent,
        expected_output=dedent('''
                A list of 3-4 distinct search queries, each designed to 
                uncover a different angle or perspective on the argument. 
                Format the output as a python list of search queries.
            '''))

    def retrieve_information(self, agent,argument):
        return Task(description=dedent(f'''
        **Task**: Retrieve Relevant Information from the internet using Search Queries 
        **Description**: Use the output of previous agent to extract data from the internet. Use the tool output to collect examples,
                         legal statutes, case precedents, and other supporting materials for the counterargument. Your final output must be
                         well-cited with website links and a comprehensive report of relevant information retrieved from the internet.

        **Parameters**:
        - Argument to be countered: {argument}

        **Note**: Ensure all retrieved information is accurate, well-documented, and credible. If you do your BEST WORK and CITE sources
                  with actual links from tool output, I will give you a $10,000 commission!.
        '''),
        tools=[SearchTools.search_internet],  
        agent=agent,
        expected_output=dedent('''
                A comprehensive report containing all relevant information retrieved from the internet with website links. 
                The report should be well-cited and include examples, legal statutes, case precedents, and other supporting materials 
                for the counterargument. Format the output as a multi-paragraph text report with citations.
            '''))

    def formulate_counterargument(self, agent, argument):
        return Task(description=dedent(f'''
        **Task**: Formulate Counterargument  
        **Description**: Use the retrieved information to construct a comprehensive counterargument. Include examples and 
                         cite sources to support your argument effectively. Your final output must be a well-structured, logical
                         and factually correct (with citation) counterargument that directly addresses the original argument provided.
                                       
        **Parameters**:
        - Argument to be countered: {argument}

        **Note**: Ensure the counterargument is logical, clear, real and directly addresses the original argument provided. {self.__tip_section()}
        '''), 
        agent=agent,
        expected_output=dedent('''A well-structured, logical, and factually correct counterargument that directly addresses the original argument. 
                The counterargument should include examples and cite sources to support the argument effectively. Provide a references section with
                 website links which were used to formulate the counterargument.
            '''))


    def evaluate_counterargument(self, agent, argument):
        return Task(description=dedent(f'''
        **Task**: Evaluate Counterargument  
        **Objective**: Determine the validity of a counterargument provided by the Legal Researcher.  

        **Steps**:  
        1. Analyze the original argument for any explicit or implicit need for user-specific information.
        - If user-specific information is required to address the argument effectively, mark the counterargument as INVALID.
        - Otherwise, proceed to step 2.
                                       
        2. Verify the logical soundness and comprehensiveness of the counterargument:
        -Does the counterargument address the original argument effectively?
        -Is it supported by credible sources or logical reasoning?
                                       
        3. Final decision:
        -Return "NO" if the counterargument fails to address the argument comprehensively or relies on missing user-specific information.
        -Return "YES" only if the counterargument is both logically valid and independent of user-specific information. 

        **Parameters**:  
        - **Argument to be Countered**: {argument}  

        **Important Notes**:  
        - Your final output must be a SINGLE word: **"YES"** or **"NO"**.  
        - Always ensure the decision aligns strictly with the provided evaluation criteria.  
        '''),
        agent=agent,
        expected_output=dedent('''return a SINGLE word as output: "YES" if valid, "NO" if invalid.'''))


    def request_additional_information(self, agent, argument,counter_argument):
        return Task(description=dedent(f'''
        **Task**: Request Additional Information  
        **Description**: Identify information needed from the user to counter the input argument and request additional specifics from the user to address these gaps.
                         Use the askUser tool to ask user specific questions to gather the necessary information. Clearly communicate what 
                         information is needed and ask specific question to user to improve the counterargument. You may or may not use the
                         incomplete or incorrect counter argument. Your final output must be the additional information provided by the user.

        **Parameters**:  
        - Input Argument to be countered: {argument}
        - Incomplete or incorrect counter argument: {counter_argument}

        **Note**:{self.__tip_section()}
        '''),
        tools=[AskUserTools.ask_user], 
        agent=agent,
        expected_output=dedent('''The additional information provided by the user to improve the counterargument. '''))

    def refine_counterargument(self, agent, argument,counter_argument):
        return Task(description=dedent(f'''
        **Task**: Refine/Reformulate the Counterargument  
        **Description**: MODIFY or REFORMULATE the provided counterargument using additional specifics or feedback from the user to ensure it is 
                         legally sound and tailored to the case. You may or may not use the incomplete or incorrect counter argument. Your final output 
                         must be a refined counterargument that addresses all aspects of the original argument.

        **Parameters**:  
        - Argument to be countered: {argument}
        - Incomplete or incorrect counterargument: {counter_argument}

        **Note**: Strive for precision and clarity in the refined argument. Ensure it meets all case-specific requirements. {self.__tip_section()}
        '''),
        agent=agent,
        expected_output=dedent('''A refined counterargument that addresses all aspects of the original argument. Ensure the argument is legally sound 
                and tailored to the case.'''))



