import os
from crewai import Crew, Process
from textwrap import dedent
from .agents import DataRetrieverAgents
from .tasks import RetrievalTasks

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataRetrievalCrew:
    def __init__(self, argument, llm):
        self.argument = argument
        self.llm = llm
   

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = DataRetrieverAgents(llm=self.llm)
        tasks = RetrievalTasks()

        # Define your custom agents and tasks here
        legal_researcher = agents.legal_researcher()
        legal_assistant = agents.legal_assistant()

        # Define tasks
        search_queries_task = tasks.generate_search_queries(legal_researcher, self.argument)
        retrieve_info_task = tasks.retrieve_information(legal_researcher, self.argument)
        formulate_counterargument_task = tasks.formulate_counterargument(legal_researcher, self.argument)
        # evaluate_counterargument_task = tasks.evaluate_counterargument(legal_assistant, self.argument)

        # Create the crew with sequential processing
        crew1 = Crew(
            agents=[legal_researcher, legal_assistant],
            tasks=[
                search_queries_task,
                retrieve_info_task,
                formulate_counterargument_task,
                # evaluate_counterargument_task
            ],
            process=Process.sequential,
        )

        result = crew1.kickoff_async()
        return result

# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Counter-Arguement Generator")
    print("-------------------------------")
    argument = str(input(dedent("""Enter argument: """)))

    info_gatherer_crew = DataRetrievalCrew(argument)
    counter_argument = info_gatherer_crew.run()
    print("\n\n########################")
    print("## Here is your information gatherer crew run result:")
    print("########################\n")
    print(counter_argument)
