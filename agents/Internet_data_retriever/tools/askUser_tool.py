# from langchain.tools import tool
from crewai.tools import tool
# from pydantic import BaseModel, Field

# class AskSchema(BaseModel):
#     question: str = Field(
#         description="The specific question to ask the user to gather information for counter arguments"
#         )

class AskUserTools():

    # @tool("Ask the user", args_schema=AskSchema, return_direct=True)
    @tool("Ask the user")
    def ask_user(question: str) -> str:

        """
        Prompt the user with a specific question and return their input.

        This tool is designed to interactively gather information from the user
        by presenting a specific question and capturing their response.

        Args:
            question (str): The precise question to be asked to the user.

        Returns:
            str: The user's textual response to the prompted question.

        Note:
            This method uses the standard input() function to collect 
            user input directly during the execution of the tool.
            
        """

        return str(input(f"{question} "))