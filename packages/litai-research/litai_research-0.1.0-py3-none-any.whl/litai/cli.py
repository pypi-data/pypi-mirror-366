"""Main CLI entry point for LitAI."""

import asyncio
import click
import aiohttp
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completion, Completer
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from litai.utils.logger import setup_logging, get_logger
from litai.config import Config
from litai.database import Database
from litai.llm import LLMClient
from litai.semantic_scholar import SemanticScholarClient
from litai.models import Paper
from litai.pdf_processor import PDFProcessor
from litai.extraction import PaperExtractor
from litai.synthesis import PaperSynthesizer
from litai.nl_handler import NaturalLanguageHandler

console = Console()
logger = get_logger(__name__)

# Global search results storage (for /add command)
_search_results: list[Paper] = []


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool) -> None:
    """LitAI - AI-powered academic paper synthesis tool."""
    setup_logging(debug=debug)

    # Log application start
    logger.info("litai_start", debug=debug)

    # Initialize configuration and database
    config = Config()
    db = Database(config)

    console.print(
        "[bold green]Welcome to LitAI![/bold green]\n"
        "Start with [cyan]/find <topic>[/cyan] or press [cyan]Tab[/cyan] to see commands."
    )

    chat_loop(db)


class CommandCompleter(Completer):
    """Custom completer for LitAI commands."""

    def __init__(self):
        self.commands = {
            "/find": "Search for papers",
            "/add": "Add paper to library",
            "/list": "Show your library",
            "/remove": "Remove paper from library",
            "/read": "Analyze a specific paper or papers and extract key insights.",
            "/synthesize": "Generate synthesis across papers to answer a question",
            "/results": "Show last search results",
            "/hf-papers": "Browse HF papers",
            "/examples": "Show usage examples",
            "/help": "Show all commands",
            "/test-llm": "Test LLM connection",
            "/cite": "Get BibTeX citation",
            "/clear": "Clear the console",
        }

    def get_completions(self, document, complete_event):
        """Get completions for the current input."""
        text = document.text_before_cursor

        # Only complete if user started typing a command
        if not text.startswith("/"):
            return

        # Get matching commands
        for cmd, description in self.commands.items():
            if cmd.startswith(text):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta=description,
                )


def chat_loop(db: Database) -> None:
    """Main interactive chat loop."""
    global _search_results
    
    # Create minimal style for better readability
    style = Style.from_dict(
        {
            # Ensure completion menu has good contrast
            "completion-menu.completion": "",  # Use terminal defaults
            "completion-menu.completion.current": "reverse",  # Invert colors for selection
            "completion-menu.meta.completion": "fg:ansibrightblack",  # Dimmed description
            "completion-menu.meta.completion.current": "reverse",  # Invert for selection
        }
    )

    # Create command completer and prompt session
    completer = CommandCompleter()
    session = PromptSession(
        completer=completer,
        complete_while_typing=False,  # Only show completions on Tab
        mouse_support=True,
        # Ensure completions appear below the input
        reserve_space_for_menu=0,  # Don't reserve space, show inline
        complete_style="MULTI_COLUMN",
        style=style,
    )
    
    # Create natural language handler with command mappings
    command_handlers = {
        "find_papers": find_papers,
        "add_paper": add_paper,
        "list_papers": list_papers,
        "remove_paper": remove_paper,
        "read_paper": read_paper,
        "synthesize_papers": synthesize_papers,
        "show_search_results": show_search_results,
        "fetch_hf_papers": fetch_hf_papers,
    }
    
    nl_handler = NaturalLanguageHandler(db, command_handlers, _search_results)

    try:
        while True:
            try:
                # Use prompt_toolkit for rich input
                user_input = session.prompt(
                    HTML("<ansicyan><b>></b></ansicyan> "),
                    default="",
                )

                # Log user input
                logger.info("user_input", input=user_input)

                if user_input.lower() in ["exit", "quit", "q"]:
                    logger.info("user_exit", method=user_input.lower())
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.startswith("/"):
                    handle_command(user_input, db)
                else:
                    # Handle natural language query
                    asyncio.run(nl_handler.handle_query(user_input))

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except Exception as e:
                logger.exception("Unexpected error in chat loop")
                from rich.markup import escape

                console.print(f"[red]Error: {escape(str(e))}[/red]")
    finally:
        # Cleanup the NL handler when exiting
        try:
            asyncio.run(nl_handler.close())
        except Exception:
            # Ignore errors during cleanup
            pass


def handle_command(command: str, db: Database) -> None:
    """Handle slash commands."""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Log command execution
    logger.info("command_executed", command=cmd, args=args)

    if cmd == "/help":
        show_help()
    elif cmd == "/find":
        if not args:
            console.print(
                "[red]Please provide a search query. Usage: /find <query>[/red]"
            )
            return
        asyncio.run(find_papers(args))
    elif cmd == "/add":
        add_paper(args, db)
    elif cmd == "/list":
        list_papers(db)
    elif cmd == "/remove":
        remove_paper(args, db)
    elif cmd == "/results":
        show_search_results()
    elif cmd == "/read":
        asyncio.run(read_paper(args, db))
    elif cmd == "/synthesize":
        asyncio.run(synthesize_papers(args, db))
    elif cmd == "/hf-papers":
        asyncio.run(fetch_hf_papers())
    elif cmd == "/cite":
        console.print(f"[yellow]Citing paper: '{args}' (not implemented)[/yellow]")
    elif cmd == "/test-llm":
        asyncio.run(test_llm())
    elif cmd == "/examples":
        show_examples(args)
    elif cmd == "/clear":
        console.clear()
    else:
        logger.warning("unknown_command", command=cmd, args=args)
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print("Type '/help' for available commands.")


async def find_papers(query: str) -> str:
    """Search for papers using Semantic Scholar.
    
    Returns:
        A summary string describing the search results for LLM context.
    """
    global _search_results

    try:
        logger.info("find_papers_start", query=query)
        with console.status(
            f"[yellow]Searching for papers matching '{query}'...[/yellow]"
        ):
            async with SemanticScholarClient() as client:
                papers = await client.search(query, limit=10)

        if not papers:
            logger.info("find_papers_no_results", query=query)
            console.print(f"[yellow]No papers found matching '{query}'[/yellow]")
            return f"No papers found matching '{query}'"

        # Store results for /add command
        _search_results = papers
        logger.info("find_papers_success", query=query, result_count=len(papers))

        # Create a table for results
        table = Table(title=f"Search Results for '{query}'", show_header=True)
        table.add_column("No.", style="cyan", width=4)
        table.add_column("Title", style="bold")
        table.add_column(
            "Authors", style="dim", width=25
        )  # Increased width to prevent wrapping
        table.add_column("Year", width=6)
        table.add_column("Citations", width=10)

        for i, paper in enumerate(papers, 1):
            # Truncate title if too long
            title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

            # Format authors
            if len(paper.authors) > 2:
                authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
            else:
                authors = ", ".join(paper.authors)

            table.add_row(
                str(i),
                title,
                authors,
                str(paper.year) if paper.year else "N/A",
                str(paper.citation_count),
            )

        console.print(table)
        console.print("\n[dim]Use /add <number> to add a paper to your library[/dim]")
        
        # Return summary for LLM
        paper_summaries = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors_str += " et al."
            paper_summaries.append(
                f"{i}. \"{paper.title}\" by {authors_str} ({paper.year}, {paper.citation_count} citations)"
            )
        
        return f"Found {len(papers)} papers matching '{query}':\n" + "\n".join(paper_summaries)

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        logger.exception("Search failed", query=query)
        return f"Search failed: {str(e)}"


def show_search_results() -> None:
    """Show the currently cached search results."""
    global _search_results

    logger.info("show_results_start")

    if not _search_results:
        logger.info("show_results_empty")
        console.print(
            "[yellow]No search results cached. Use /find to search for papers.[/yellow]"
        )
        return

    logger.info("show_results_success", result_count=len(_search_results))

    # Create a table for cached results
    table = Table(title="Cached Search Results", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Authors", style="dim", width=25)
    table.add_column("Year", width=6)
    table.add_column("Citations", width=10)

    for i, paper in enumerate(_search_results, 1):
        # Truncate title if too long
        title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

        # Format authors
        if len(paper.authors) > 2:
            authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
        else:
            authors = ", ".join(paper.authors)

        table.add_row(
            str(i),
            title,
            authors,
            str(paper.year) if paper.year else "N/A",
            str(paper.citation_count),
        )

    console.print(table)
    console.print("\n[dim]Use /add <number> to add a paper to your library[/dim]")


def remove_paper(args: str, db: Database) -> None:
    """Remove a paper from the library."""
    logger.info("remove_paper_start", args=args)
    
    papers = db.list_papers()
    if not papers:
        logger.warning("remove_paper_no_papers")
        console.print(
            "[red]No papers in your library to remove.[/red]"
        )
        return
    
    if not args:
        logger.warning("remove_paper_no_args")
        console.print("[red]Please specify a paper number. Usage: /remove <number>[/red]")
        return
    
    try:
        paper_num = int(args.strip())
        if paper_num < 1 or paper_num > len(papers):
            logger.warning(
                "remove_paper_invalid_number",
                paper_num=paper_num,
                max_num=len(papers),
            )
            console.print(
                f"[red]Invalid paper number. Please choose between 1 and {len(papers)}[/red]"
            )
            return
        
        paper = papers[paper_num - 1]
        
        # Confirm deletion
        console.print("\n[yellow]Are you sure you want to remove this paper?[/yellow]")
        console.print(f"Title: {paper.title}")
        console.print(f"Authors: {', '.join(paper.authors[:3])}")
        if len(paper.authors) > 3:
            console.print(f"... and {len(paper.authors) - 3} more")
        
        confirmation = Prompt.ask(
            "\nConfirm removal?", 
            choices=["yes", "y", "no", "n"], 
            default="no"
        )
        
        if confirmation in ['yes', 'y']:
            success = db.delete_paper(paper.paper_id)
            if success:
                logger.info("remove_paper_success", paper_id=paper.paper_id, title=paper.title)
                console.print(f"[green]✓ Removed from library: '{paper.title}'[/green]")
            else:
                logger.error("remove_paper_failed", paper_id=paper.paper_id, title=paper.title)
                console.print("[red]Failed to remove paper from library[/red]")
        else:
            logger.info("remove_paper_cancelled", paper_id=paper.paper_id)
            console.print("[yellow]Removal cancelled.[/yellow]")
            
    except ValueError:
        console.print(
            "[red]Invalid paper number. Please provide a numeric value.[/red]"
        )
    except Exception as e:
        console.print(f"[red]Error removing paper: {e}[/red]")
        logger.exception("Failed to remove paper", args=args)


def add_paper(args: str, db: Database) -> None:
    """Add a paper from search results to the library."""
    global _search_results

    logger.info("add_paper_start", args=args)

    if not _search_results:
        logger.warning("add_paper_no_results")
        console.print(
            "[red]No search results available. Use /find first to search for papers.[/red]"
        )
        return

    try:
       if not args.strip():
           # Empty input - add all papers
           console.print(f"[yellow]Add all {len(_search_results)} papers to library?[/yellow]")
           confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
           if confirm.lower() != 'yes':
               console.print("[red]Cancelled[/red]")
               return
           
           paper_indices = list(range(len(_search_results)))
       else:
           # Parse comma-delimited paper numbers
           paper_indices = []
           for num_str in args.split(','):
               num_str = num_str.strip()
               if not num_str:
                   continue
               try:
                   paper_num = int(num_str)
                   if paper_num < 1 or paper_num > len(_search_results):
                       console.print(f"[red]Invalid paper number: {paper_num}. Must be between 1 and {len(_search_results)}[/red]")
                       return
                   paper_indices.append(paper_num - 1)
               except ValueError:
                   console.print(f"[red]Invalid number: '{num_str}'[/red]")
                   return
       
       # Add papers
       added_count = 0
       duplicate_count = 0
       
       for idx in paper_indices:
           paper = _search_results[idx]
           existing = db.get_paper(paper.paper_id)
           
           if existing:
               logger.info("add_paper_duplicate", paper_id=paper.paper_id, title=paper.title)
               duplicate_count += 1
               continue
           
           success = db.add_paper(paper)
           if success:
               logger.info("add_paper_success", paper_id=paper.paper_id, title=paper.title)
               added_count += 1
               console.print(f"[green]✓ Added: '{paper.title}'[/green]")
           else:
               logger.error("add_paper_failed", paper_id=paper.paper_id, title=paper.title)
               console.print(f"[red]Failed to add: '{paper.title}'[/red]")
       
       # Summary
       console.print(f"\n[green]Added {added_count} papers[/green]")
       if duplicate_count:
           console.print(f"[yellow]Skipped {duplicate_count} duplicates[/yellow]")
           
    except Exception as e:
       console.print(f"[red]Error adding papers: {e}[/red]")
       logger.exception("Failed to add papers", args=args)


def list_papers(db: Database) -> str:
    """List all papers in the library.
    
    Returns:
        A summary string describing the papers in the library for LLM context.
    """
    logger.info("list_papers_start")
    papers = db.list_papers()

    if not papers:
        logger.info("list_papers_empty")
        console.print(
            "[yellow]No papers in your library yet. Use /find to search for papers.[/yellow]"
        )
        return "Your library is empty. No papers found."

    # Get total count for pagination info
    total_count = db.count_papers()
    logger.info("list_papers_success", paper_count=len(papers), total_count=total_count)

    # Create a table for library papers
    table = Table(title=f"Your Library ({total_count} papers)", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("Title", style="bold")
    table.add_column(
        "Authors", style="dim", width=25
    )  # Increased width to prevent wrapping
    table.add_column("Year", width=6)
    table.add_column("Citations", width=10)
    table.add_column("ID", style="dim", width=15)
    table.add_column("Venue", style="dim", width=15)

    for i, paper in enumerate(papers, 1):
        # Truncate title if too long
        title = paper.title[:70] + "..." if len(paper.title) > 70 else paper.title

        # Format authors
        if len(paper.authors) > 2:
            authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
        else:
            authors = ", ".join(paper.authors)

        # Truncate paper ID for display
        paper_id_display = (
            paper.paper_id[:12] + "..." if len(paper.paper_id) > 12 else paper.paper_id
        )

        table.add_row(
            str(i),
            title,
            authors,
            str(paper.year) if paper.year else "N/A",
            str(paper.citation_count),
            paper_id_display,
            paper.venue if paper.venue else "N/A",
        )

    console.print(table)

    if total_count > len(papers):
        console.print(
            f"\n[dim]Showing first {len(papers)} papers. Total: {total_count}[/dim]"
        )

    console.print("\n[dim]Use /read <number> to extract key points from a paper[/dim]")
    
    # Return summary for LLM
    paper_summaries = []
    for i, paper in enumerate(papers[:10], 1):  # Include top 10 for LLM context
        authors_str = ", ".join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors_str += " et al."
        paper_summaries.append(f"{i}. \"{paper.title}\" by {authors_str} ({paper.year})")
    
    result = f"Found {total_count} papers in your library."
    if paper_summaries:
        result += " Top papers:\n" + "\n".join(paper_summaries)
    return result


async def test_llm() -> None:
    """Test the LLM connection."""
    logger.info("test_llm_start")

    try:
        with console.status("[yellow]Testing LLM connection...[/yellow]"):
            client = LLMClient()
            response_text, usage = await client.test_connection()

        logger.info(
            "test_llm_success",
            provider=client.provider,
            model=client.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=usage.estimated_cost,
        )

        console.print(
            f"[green]✓ LLM connection successful[/green] ({client.provider} {client.model})"
        )
        console.print(f"  Response: {response_text}")
        console.print(f"  Test prompt: {usage.prompt_tokens} tokens")
        console.print(f"  Response: {usage.completion_tokens} tokens")
        console.print(
            f"  Total: {usage.total_tokens} tokens (~${usage.estimated_cost:.4f})"
        )

    except ValueError as e:
        logger.error("test_llm_config_error", error=str(e))
        console.print(f"[red]✗ LLM connection failed: {e}[/red]")
        console.print(
            "\nTo use LitAI, you need to set one of these environment variables:"
        )
        console.print("  - OPENAI_API_KEY for OpenAI GPT-4")
        console.print("  - ANTHROPIC_API_KEY for Anthropic Claude")
    except Exception as e:
        console.print(f"[red]✗ LLM test failed: {e}[/red]")
        logger.exception("LLM test failed")


async def read_paper(args: str, db: Database) -> None:
   """Extract and display key points from paper(s) in the library."""
   logger.info("read_paper_start", args=args)
   papers = db.list_papers()
   
   if not papers:
       logger.warning("read_paper_no_papers")
       console.print("[red]No papers in your library. Use /find and /add to add papers first.[/red]")
       return
   
   try:
       # Parse input
       if not args.strip():
           # Empty input - read all papers
           console.print(f"[yellow]Extract key points from all {len(papers)} papers?[/yellow]")
           confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
           if confirm.lower() != 'yes':
               console.print("[red]Cancelled[/red]")
               return
           paper_indices = list(range(len(papers)))
       else:
           # Parse comma-delimited paper numbers
           paper_indices = []
           for num_str in args.split(','):
               num_str = num_str.strip()
               if not num_str:
                   continue
               try:
                   paper_num = int(num_str)
                   if paper_num < 1 or paper_num > len(papers):
                       console.print(f"[red]Invalid paper number: {paper_num}. Must be between 1 and {len(papers)}[/red]")
                       return
                   paper_indices.append(paper_num - 1)
               except ValueError:
                   console.print(f"[red]Invalid number: '{num_str}'[/red]")
                   return
       
       # Initialize components once
       config = Config()
       llm_client = LLMClient()
       pdf_processor = PDFProcessor(db, config.base_dir)
       extractor = PaperExtractor(db, llm_client, pdf_processor)
       
       # Process papers concurrently
       async def process_paper(idx: int) -> tuple[int, bool, str]:
           paper = papers[idx]
           try:
               # Check cache first
               cached = db.get_extraction(paper.paper_id, "key_points")
               cache_msg = " (cached)" if cached else ""
               
               key_points = await extractor.extract_key_points(paper.paper_id)
               
               if not key_points:
                   return idx, False, f"No key points extracted{cache_msg}"
               
               # For single paper, show full output
               if len(paper_indices) == 1:
                   console.print(f"\n[bold]Extracting key points from:[/bold] {paper.title}")
                   console.print(f"[dim]Authors: {', '.join(paper.authors[:3])}")
                   if len(paper.authors) > 3:
                       console.print(f"[dim]... and {len(paper.authors) - 3} more[/dim]")
                   console.print(f"[dim]{cache_msg}[/dim]\n" if cache_msg else "\n")
                   
                   console.print("[bold green]Key Points:[/bold green]\n")
                   for i, point in enumerate(key_points, 1):
                       console.print(f"[bold cyan]{i}. Claim:[/bold cyan] {point.claim}")
                       console.print(f'   [bold]Evidence:[/bold] "{point.evidence}"')
                       console.print(f"   [dim]Section: {point.section}[/dim]\n")
               
               return idx, True, f"{len(key_points)} points{cache_msg}"
               
           except Exception as e:
               logger.exception("Key point extraction failed", paper_id=paper.paper_id)
               return idx, False, str(e)
       
       # Run extractions
       if len(paper_indices) == 1:
           # Single paper - run directly
           await process_paper(paper_indices[0])
       else:
           # Multiple papers - show progress
           console.print(f"\n[bold]Extracting key points from {len(paper_indices)} papers...[/bold]\n")
           
           # Concurrent execution with progress tracking
           semaphore = asyncio.Semaphore(5)  # Limit concurrent LLM calls
           
           async def process_with_limit(idx: int) -> tuple[int, bool, str]:
               async with semaphore:
                   return await process_paper(idx)
           
           tasks = [process_with_limit(idx) for idx in paper_indices]
           results = []
           
           with console.status("[bold green]Processing papers...") as status:
               for coro in asyncio.as_completed(tasks):
                   idx, success, msg = await coro
                   paper = papers[idx]
                   results.append((idx, success, msg))
                   
                   if success:
                       console.print(f"[green]✓[/green] {paper.title[:60]}... - {msg}")
                   else:
                       console.print(f"[red]✗[/red] {paper.title[:60]}... - {msg}")
                   
                   status.update(f"[bold green]Processing papers... ({len(results)}/{len(paper_indices)})")
           
           # Summary
           successful = sum(1 for _, success, _ in results if success)
           console.print(f"\n[green]Successfully extracted from {successful}/{len(paper_indices)} papers[/green]")
           
           cached_count = sum(1 for _, success, msg in results if success and "(cached)" in msg)
           if cached_count:
               console.print(f"[dim]{cached_count} from cache[/dim]")
               
   except Exception as e:
       console.print(f"[red]Error reading papers: {e}[/red]")
       logger.exception("Failed to read papers", args=args)


async def synthesize_papers(question: str, db: Database) -> str:
    """Generate a synthesis across papers to answer a research question.
    
    Returns:
        String containing the synthesis result and relevant papers information.
    """
    logger.info("synthesize_start", question=question)

    if not question.strip():
        logger.warning("synthesize_no_question")
        error_msg = "Please provide a research question. Usage: /synthesize <question>"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

    papers = db.list_papers(limit=100)  # Get more papers for synthesis
    if not papers:
        logger.warning("synthesize_no_papers")
        error_msg = "No papers in your library. Use /find and /add to add papers first."
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

    try:
        # Initialize components
        config = Config()
        llm_client = LLMClient()
        pdf_processor = PDFProcessor(db, config.base_dir)
        extractor = PaperExtractor(db, llm_client, pdf_processor)
        synthesizer = PaperSynthesizer(db, llm_client, extractor)

        # Show status
        console.print(f"\n[bold]Synthesizing answer to:[/bold] {question}")
        console.print(f"[dim]Analyzing {len(papers)} papers in your library...[/dim]\n")

        # Generate synthesis
        with console.status("[yellow]Selecting relevant papers...[/yellow]"):
            result = await synthesizer.synthesize(question)

        logger.info(
            "synthesize_success",
            question=question,
            papers_analyzed=len(papers),
            papers_selected=len(result.relevant_papers),
        )

        # Build result string
        result_text = []
        result_text.append(f"Synthesis for '{question}':\n")
        result_text.append(result.synthesis)
        result_text.append(f"\n\nRelevant Papers ({len(result.relevant_papers)} selected):\n")
        
        for i, rp in enumerate(result.relevant_papers, 1):
            result_text.append(f"\n[{i}] \"{rp.paper.title}\" ({rp.paper.year})")
            authors_str = f"Authors: {', '.join(rp.paper.authors[:3])}"
            if len(rp.paper.authors) > 3:
                authors_str += f" ... and {len(rp.paper.authors) - 3} more"
            result_text.append(f"    {authors_str}")
            result_text.append(f"    Relevance: {rp.relevance_score:.1f}/1.0")
            result_text.append(f"    Why relevant: {rp.relevance_reason}")
            if rp.key_points:
                result_text.append(f"    Key points extracted: {len(rp.key_points)}")
        
        # Display results to console (keep existing display)
        console.print("[bold green]Synthesis:[/bold green]\n")
        console.print(result.synthesis)
        console.print("\n" + "─" * 80 + "\n")

        # Show relevant papers with explanations
        console.print(
            f"[bold]Relevant Papers ({len(result.relevant_papers)} selected):[/bold]\n"
        )

        for i, rp in enumerate(result.relevant_papers, 1):
            console.print(
                f'[bold cyan][{i}][/bold cyan] "{rp.paper.title}" ({rp.paper.year})'
            )
            authors_str = f"Authors: {', '.join(rp.paper.authors[:3])}"
            if len(rp.paper.authors) > 3:
                authors_str += f" ... and {len(rp.paper.authors) - 3} more"
            console.print(f"    [dim]{authors_str}[/dim]")
            console.print(f"    [bold]Relevance:[/bold] {rp.relevance_score:.1f}/1.0")
            console.print(f"    [bold]Why relevant:[/bold] {rp.relevance_reason}")
            if rp.key_points:
                console.print(
                    f"    [dim]Key points extracted: {len(rp.key_points)}[/dim]"
                )
            console.print()

        # Show papers that were considered but not selected
        selected_ids = {rp.paper.paper_id for rp in result.relevant_papers}
        not_selected = [p for p in papers if p.paper_id not in selected_ids]

        if not_selected:
            console.print(
                f"\n[dim]Papers not selected ({len(not_selected)} papers):[/dim]"
            )
            for paper in not_selected[:5]:  # Show first 5
                console.print(f'[dim]- "{paper.title}"[/dim]')
            if len(not_selected) > 5:
                console.print(f"[dim]  ... and {len(not_selected) - 5} more[/dim]")
        
        # Return the synthesis result
        return "\n".join(result_text)

    except ValueError as e:
        from rich.markup import escape
        error_msg = f"Synthesis failed: {str(e)}"
        console.print(f"[red]{escape(error_msg)}[/red]")
        return error_msg
    except Exception as e:
        from rich.markup import escape
        error_msg = f"Error during synthesis: {str(e)}"
        console.print(f"[red]{escape(error_msg)}[/red]")
        logger.exception("Synthesis failed", question=question)
        return error_msg


async def fetch_hf_papers() -> None:
    """Fetch and display papers from Hugging Face RSS feed."""
    hf_feed_url = "https://jamesg.blog/hf-papers.json"

    logger.info("fetch_hf_papers_start")

    try:
        with console.status("[yellow]Fetching papers from Hugging Face...[/yellow]"):
            async with aiohttp.ClientSession() as session:
                async with session.get(hf_feed_url) as response:
                    if response.status != 200:
                        console.print(
                            f"[red]Failed to fetch HF papers. Status: {response.status}[/red]"
                        )
                        return

                    data = await response.json()
                    papers = data.get("items", [])

        if not papers:
            logger.info("fetch_hf_papers_empty")
            console.print("[yellow]No papers found in the feed.[/yellow]")
            return

        logger.info("fetch_hf_papers_success", paper_count=len(papers))

        # Create a table for HF papers
        table = Table(title="Hugging Face Papers (View Only)", show_header=True)
        table.add_column("No.", style="cyan", width=4)
        table.add_column("Title", style="bold")
        table.add_column("Date", style="dim", width=12)
        table.add_column("HF ID", style="dim", width=15)

        for i, paper in enumerate(papers[:20], 1):  # Show only first 20 papers
            # Extract paper ID from URL
            paper_id = paper["url"].split("/")[-1] if "url" in paper else "N/A"

            # Parse and format date
            date_str = paper.get("date_published", "N/A")
            if date_str != "N/A":
                try:
                    date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    date_str = "N/A"

            # Truncate title if too long
            title = paper.get("title", "Untitled")
            title = title[:80] + "..." if len(title) > 80 else title

            table.add_row(str(i), title, date_str, paper_id)

        console.print(table)
        console.print(
            "\n[dim]These papers are view-only. Use /find <query> to search and add papers to your library.[/dim]"
        )

    except aiohttp.ClientError as e:
        console.print(f"[red]Network error fetching HF papers: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error fetching HF papers: {e}[/red]")
        logger.exception("Failed to fetch HF papers")


def show_examples(command: str = "") -> None:
    """Show usage examples for different commands."""
    logger.info("show_examples", command=command)

    # If a specific command is provided, show examples for that command
    if command:
        command = command.strip().lower()
        if command.startswith("/"):
            command = command[1:]  # Remove leading slash

        examples = get_command_examples()
        if command in examples:
            console.print(f"\n[bold]Examples for /{command}:[/bold]\n")
            console.print(examples[command])
        else:
            console.print(f"[red]No examples found for '{command}'[/red]")
            console.print("Use '/examples' without arguments to see all examples.")
        return

    # Show all examples
    console.print("\n[bold]Usage Examples:[/bold]\n")

    examples = get_command_examples()
    for cmd, example_text in examples.items():
        console.print(f"[bold cyan]/{cmd}[/bold cyan]")
        console.print(example_text)
        console.print()  # Add spacing between examples


def get_command_examples() -> dict[str, str]:
    """Get example usage for each command."""
    return {
        "find": """[dim]Search for papers on a specific topic:[/dim]
  /find attention mechanisms
  /find transformer architecture
  /find "deep learning optimization"
  /find COVID-19 wastewater surveillance""",
        "add": """[dim]Add a paper from search results:[/dim]
  /add 1          [dim]# Add the first paper from search results[/dim]
  /add 3          [dim]# Add the third paper[/dim]
  
[dim]Note: You must use /find first to get search results[/dim]""",
        "list": """[dim]List papers in your library:[/dim]
  /list           [dim]# Shows all papers with numbers for easy reference[/dim]""",
        "remove": """[dim]Remove a paper from your library:[/dim]
  /remove 1       [dim]# Remove the first paper from your library[/dim]
  /remove 5       [dim]# Remove the fifth paper[/dim]
  
[dim]Note: Use /list first to see paper numbers[/dim]
[dim]You will be asked to confirm before deletion[/dim]""",
        "read": """[dim]Extract key points from a paper:[/dim]
  /read 1         [dim]# Read the first paper from your library[/dim]
  /read 5         [dim]# Read the fifth paper[/dim]
  
[dim]Note: Use /list first to see paper numbers[/dim]""",
        "synthesize": """[dim]Generate synthesis to answer research questions:[/dim]
  /synthesize What are the main benefits of attention mechanisms?
  /synthesize How do transformers compare to RNNs for sequence modeling?
  /synthesize What optimization techniques work best for large language models?
  /synthesize Compare different approaches to early disease detection
  
[dim]Tips:[/dim]
  - Ask specific, focused questions
  - The synthesis will use papers in your library
  - Add relevant papers first with /find and /add""",
        "results": """[dim]Show cached search results:[/dim]
  /results        [dim]# Display results from your last /find command[/dim]""",
        "hf-papers": """[dim]Browse recent papers from Hugging Face:[/dim]
  /hf-papers      [dim]# Shows latest papers (view only)[/dim]""",
        "examples": """[dim]Show examples for specific commands:[/dim]
  /examples               [dim]# Show all examples[/dim]
  /examples synthesize    [dim]# Show examples for /synthesize[/dim]
  /examples find          [dim]# Show examples for /find[/dim]""",
    }


def show_help() -> None:
    """Display help information."""
    logger.info("show_help")
    help_text = """
[bold]Available Commands (adding quotation marks is not necessary):[/bold]

[cyan]/find <query>[/cyan] - Search for papers on Semantic Scholar
[cyan]/results[/cyan] - Show cached search results from last /find
[cyan]/add <number>[/cyan] - Add a paper from search results to your library
[cyan]/list[/cyan] - List all papers in your library
[cyan]/remove <number>[/cyan] - Remove a paper from your library
[cyan]/read <number>[/cyan] - Analyze a specific paper or papers and extract key insights.
[cyan]/synthesize <question>[/cyan] - Generate synthesis across papers to answer a question
[cyan]/hf-papers[/cyan] - Show recent papers from Hugging Face (view only)
[cyan]/cite <number>[/cyan] - Get BibTeX citation for a paper
[cyan]/examples[/cyan] - Show usage examples for different commands
[cyan]/clear[/cyan] - Clear the console screen
[cyan]/help[/cyan] - Show this help message

[bold]Natural Language:[/bold]
You can also ask questions about your papers in plain English.
Example: "What do the papers say about attention mechanisms?"
"""
    console.print(help_text)


if __name__ == "__main__":
    main()
