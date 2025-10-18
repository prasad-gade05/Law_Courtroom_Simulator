from typing import Dict, Any, Optional
from datetime import datetime
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from core.state import TrialPhase

class TrialDisplay:
    """Handles real-time display of trial proceedings in the terminal"""
    
    PHASE_HEADERS = {
        TrialPhase.INITIALIZATION: "🏛️  TRIAL INITIALIZATION",
        TrialPhase.EVIDENCE_COLLECTION: "🔍 EVIDENCE COLLECTION",
        TrialPhase.ARGUMENT_EXCHANGE: "⚖️  ARGUMENT EXCHANGE",
        TrialPhase.VERDICT: "📜 VERDICT",
        TrialPhase.COMPLETED: "✅ TRIAL COMPLETED"
    }
    
    def __init__(self):
        self.console = Console()
        self.current_phase: Optional[TrialPhase] = None
        self.last_speaker: Optional[str] = None
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
    
    def display_phase_change(self, phase: TrialPhase) -> None:
        """Display phase transition"""
        self.current_phase = phase
        self.console.print("\n")
        self.console.rule(style="bright_blue")
        self.console.print(
            f"[bold blue]{self.PHASE_HEADERS.get(phase, str(phase))}[/bold blue]",
            justify="center"
        )
        self.console.rule(style="bright_blue")
        self.console.print("\n")
    
    def display_message(self, agent_id: str, message: Dict[str, Any]) -> None:
        """Display an agent's message"""
        agent_name = agent_id.replace("_", " ").title()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create panel for the message
        content = message.get("content", str(message))
        reasoning = message.get("reasoning", [])
        
        if reasoning:
            thought_table = Table(show_header=False, box=None)
            for thought in reasoning:
                thought_table.add_row(
                    f"[dim]• {thought.get('step', '')}: {thought.get('thought', '')}[/dim]"
                )
        
        panel = Panel(
            Markdown(content) if content else "",
            title=f"[bold]{agent_name}[/bold] [{timestamp}]",
            subtitle="[dim]Chain of Thought[/dim]" if reasoning else None,
            title_align="left",
            border_style=self._get_agent_color(agent_id)
        )
        
        self.console.print(panel)
        if reasoning:
            self.console.print(thought_table)
    
    def display_evidence(self, evidence: Dict[str, Any]) -> None:
        """Display retrieved evidence"""
        table = Table(
            title="📄 Retrieved Evidence",
            show_header=True,
            header_style="bold blue"
        )
        table.add_column("Source", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Relevance", style="green")
        
        for doc in evidence.get("results", []):
            table.add_row(
                doc.get("source", "Unknown"),
                doc.get("content", "")[:200] + "...",
                f"{doc.get('relevance_score', 0):.2f}"
            )
        
        self.console.print(table)
    
    def display_retrieval_progress(self, query: str) -> None:
        """Display retrieval progress"""
        with self.progress:
            task = self.progress.add_task(
                f"[cyan]Searching for: {query}...",
                total=None
            )
            return task
    
    def display_error(self, error: str) -> None:
        """Display error messages"""
        self.console.print(
            Panel(
                f"[red]{error}[/red]",
                title="❌ Error",
                border_style="red"
            )
        )
    
    def display_summary(self, summary: Dict[str, Any]) -> None:
        """Display trial summary"""
        table = Table(title="📋 Trial Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in summary.items():
            if key != "content":
                table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(table)
        if "content" in summary:
            self.console.print(
                Panel(
                    Markdown(summary["content"]),
                    title="Summary",
                    border_style="blue"
                )
            )
    
    def _get_agent_color(self, agent_id: str) -> str:
        """Get color for agent messages"""
        colors = {
            "lawyer": "green",
            "prosecutor": "red",
            "judge": "yellow",
            "retriever": "blue"
        }
        return colors.get(agent_id, "white")
    
    def _clear_line(self) -> None:
        """Clear the current terminal line"""
        self.console.clear_line() 