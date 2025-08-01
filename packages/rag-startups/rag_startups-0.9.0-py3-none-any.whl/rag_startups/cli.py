"""Command-line interface for startup idea generation."""

import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from embed_master import calculate_result, initialize_embeddings

from .cli_models import app as models_app
from .config.settings import get_settings
from .core.model_service import ModelService
from .core.startup_metadata import StartupLookup
from .data.loader import load_data
from .idea_generator.generator import StartupIdeaGenerator
from .idea_generator.processors import parse_ideas
from .utils.caching import clear_cache
from .utils.output_formatter import formatter

app = typer.Typer(
    name="rag_startups",
    help="Generate and analyze startup ideas using AI and market data.",
    add_completion=False,
)
console = Console()

# Add model management subcommand
app.add_typer(models_app, name="models")


def validate_token() -> str:
    """Validate HuggingFace token is available."""
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        console.print(
            "[red]Error:[/red] HUGGINGFACE_TOKEN environment variable not set.\n"
            "Please set it with your HuggingFace API token."
        )
        raise typer.Exit(1)
    return token


def display_idea(idea_text: str, market_insights: Optional[dict] = None):
    """Display generated idea with optional market insights."""
    # Display the idea
    console.print(Panel(idea_text, title="Generated Startup Idea", expand=False))

    # Display market insights if available
    if market_insights:
        table = Table(
            title="Market Analysis", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for name, insights in market_insights.items():
            table.add_row("Startup Name", name)
            table.add_row("Market Size", f"${insights.market_size:,.2f}B")
            table.add_row("Growth Rate", f"{insights.growth_rate:.1f}%")
            table.add_row("Competition", insights.competition_level)
            table.add_row("Opportunity Score", f"{insights.opportunity_score:.2f}")
            table.add_row("Confidence Score", f"{insights.confidence_score:.2f}")

            if insights.key_trends:
                table.add_row(
                    "Key Trends",
                    "\n".join(f"• {trend}" for trend in insights.key_trends),
                )

            if insights.risk_factors:
                table.add_row(
                    "Risk Factors",
                    "\n".join(f"• {risk}" for risk in insights.risk_factors),
                )

        console.print(table)


@app.command()
def generate_all(
    topic: str = typer.Argument(..., help="Topic or domain for the startup idea"),
    startup_file: str = typer.Option(
        "yc_startups.json",
        "--file",
        "-f",
        help="Path to startup data file (must be provided by user)",
    ),
    num_ideas: int = typer.Option(
        1, "--num-ideas", "-n", help="Number of startup ideas to generate (1-5)"
    ),
    market_analysis: bool = typer.Option(
        True, "--market/--no-market", help="Include market analysis"
    ),
    temperature: float = typer.Option(
        0.7,
        "--temperature",
        "-t",
        help="Model temperature (0.0-1.0). Higher values make output more creative.",
    ),
    print_examples: bool = typer.Option(
        False, "--print-examples", "-p", help="Print startup examples found in file"
    ),
):
    """Generate startup ideas with optional market analysis.

    Each generated startup name includes a unique identifier (e.g., TechStartup-x7y9z).
    Note: Generated names are suggestions only. Users must verify legal availability
    before use. See README.md for more information about name verification.
    """

    # Validate number of ideas
    if not 1 <= num_ideas <= 5:
        console.print("[red]Error:[/red] num_ideas must be between 1 and 5")
        raise typer.Exit(1)
    # Validate startup data file exists
    if not os.path.exists(startup_file):
        console.print(
            f"[red]Error:[/red] Startup data file '{startup_file}' not found.\n"
            "Please provide a valid startup data file using --file option."
        )
        raise typer.Exit(1)

    """Generate startup ideas with optional market analysis."""

    # Validate token
    token = validate_token()

    # Initialize smart model management
    settings = get_settings()
    model_service = ModelService(settings)

    # Get the best available language model
    language_model = model_service.get_language_model()
    console.print(f"[blue]Using model:[/blue] {language_model.name}", style="dim")

    question = (
        f"Find innovative startup ideas in {topic}"
        if " " in topic  # If it's a compound phrase like "education technology"
        else f"Find innovative startup ideas in the {topic} domain"
    )

    prompt_messages = [
        (
            "system",
            """
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question.
            If you don't know the answer, just say that you don't know.
            Use three sentences maximum and keep the answer concise.
            Question: {question}
            Context: {context}
            Answer:""",
        )
    ]

    # Initialize lookup with the JSON data
    df, json_data = load_data(startup_file)  # no max_lines
    lookup = StartupLookup(json_data)

    with console.status("[bold green]Generating startup ideas..."):
        # Find startups in the file relevant to the topic
        example_startups = find_relevant_startups(
            num_ideas, question, prompt_messages, print_examples, lookup, df, json_data
        )
        example_startups_parsed = parse_ideas(example_startups)

        # Use smart model management instead of hardcoded model
        generator = StartupIdeaGenerator(model_name=language_model.name, token=token)
        response, insights = generator.generate(
            num_ideas=num_ideas,
            example_startups=example_startups_parsed,
            temperature=temperature,
            include_market_analysis=market_analysis,
        )

    if response:
        display_idea(response, insights if market_analysis else None)
    else:
        console.print("[red]Failed to generate startup ideas.[/red]")
        raise typer.Exit(1)


def find_relevant_startups(
    num_ideas, question, prompt_messages, print_examples, lookup, df, json_data
):
    """the code to find startups examples here"""

    # Initialize embeddings and retriever once
    retriever = initialize_embeddings(df)

    # Pass retriever to calculate_result
    result = calculate_result(
        question=question,
        retriever=retriever,
        json_data=json_data,
        prompt_messages=prompt_messages,
        lookup=lookup,
        num_ideas=num_ideas,
    )

    # Print the results in a nicely formatted way

    if print_examples:
        formatter.print_startup_ideas(result)
        formatter.print_summary()

    return result


@app.command()
def analyze(
    idea_name: str = typer.Argument(..., help="Name of the startup to analyze"),
    idea_description: str = typer.Argument(
        ..., help="Brief description of the startup idea"
    ),
    target_market: str = typer.Argument(..., help="Target market for the startup"),
):
    """Analyze market potential for an existing startup idea."""
    token = validate_token()

    with console.status("[bold green]Analyzing market potential..."):
        generator = StartupIdeaGenerator(token=token)
        idea = {
            "name": idea_name,
            "description": idea_description,
            "target_market": target_market,
        }
        _, insights = generator.generate(
            num_ideas=1,
            example_startups=[idea],
            include_market_analysis=True,
        )

    if insights:
        display_idea(
            f"Analysis for: {idea_name}\n\n{idea_description}\nTarget Market: {target_market}",
            insights,
        )
    else:
        console.print("[red]Failed to analyze startup idea.[/red]")
        raise typer.Exit(1)


@app.command()
def clear():
    """Clear cached data and analysis results."""
    try:
        clear_cache()
        console.print("[green]Successfully cleared cache.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to clear cache: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
