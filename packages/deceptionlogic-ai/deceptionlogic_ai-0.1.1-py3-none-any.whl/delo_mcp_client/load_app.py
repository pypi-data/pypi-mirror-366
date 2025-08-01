import typer

app = typer.Typer(pretty_exceptions_show_locals=False, invoke_without_command=True,
                  help="The Deception Logic MCP Client Package.\nAn interface to run an LLM client with the Deception Logic API MCP server.",
                  context_settings={"help_option_names": ["-h", "--help"]})
