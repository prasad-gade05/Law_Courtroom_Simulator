
import asyncio
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from legal_rag.core.workflow import TrialWorkflow
from legal_rag.agents import LawyerAgent, ProsecutorAgent, JudgeAgent, RetrieverAgent
from legal_rag.core.pathway_store import PathwayVectorStore
from legal_rag.tools.retrievers import create_web_retriever
from legal_rag.interface.terminal_display import TrialDisplay

console = Console()

async def process_legal_case(case_details: dict) -> dict:
    display = TrialDisplay()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Initialize components
        init_task = progress.add_task("[cyan]Initializing components...", total=None)
        
        # Initialize vector store
        vector_store = PathwayVectorStore()
        await vector_store.initialize()
        
        # Create web retriever
        web_retriever = create_web_retriever()
        
        # Initialize agents
        lawyer = LawyerAgent()
        prosecutor = ProsecutorAgent()
        judge = JudgeAgent()
        retriever = RetrieverAgent(
            vector_store=vector_store,
            web_search_tool=web_retriever
        )
        
        progress.update(init_task, completed=True)
        
        # Create and initialize workflow
        workflow_task = progress.add_task("[cyan]Setting up trial workflow...", total=None)
        workflow = TrialWorkflow(
            lawyer=lawyer,
            prosecutor=prosecutor,
            judge=judge,
            retriever=retriever
        )
        await workflow.initialize()
        progress.update(workflow_task, completed=True)
        
        # Display case details
        console.print("\n[bold cyan]Case Details:[/bold cyan]")
        console.print(Panel.fit(
            "\n".join([f"{k}: {v}" for k, v in case_details.items()]),
            title="Case Information"
        ))
        
        # Run trial
        console.print("\n[bold green]Starting Trial Process[/bold green]")
        result = await workflow.run(case_details)
        
        # Display final verdict
        console.print("\n[bold yellow]Trial Completed[/bold yellow]")
        console.print(Panel.fit(
            result["verdict"]["content"],
            title="Final Verdict",
            border_style="yellow"
        ))
        
        # Display statistics
        console.print("\n[bold cyan]Trial Statistics:[/bold cyan]")
        console.print(f"Total Messages: {len(result['history'])}")
        console.print(f"Evidence Pieces: {len(result['evidence'])}")
        console.print(f"Fact Checks: {len(result['fact_checks'])}")
        
        return result

if __name__ == "__main__":
    # Example case details
    case = {
        "title": "Example Legal Case",
        "description": "This is a test case to demonstrate the Legal RAG system.",
        "client_name": "John Doe",
        "case_type": "Civil Dispute",
        "key_facts": [
            "Incident occurred on January 1st, 2024",
            "Contract dispute between two parties",
            "Value of dispute: $50,000"
        ]
    }
    
    try:
        console.print("[bold]🏛️ Legal RAG System[/bold]")
        console.print("Starting case processing...\n")
        
        result = asyncio.run(process_legal_case(case))
        
        # Save trial record if needed
        # with open("trial_record.json", "w") as f:
        #     json.dump(result, f, indent=2)
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Process interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1) 


