from enum import Enum
import typer
from delo_mcp_client.load_app import app


MODEL_API_KEY = ""
DELO_KEY_ID = ""
DELO_SECRET = ""
URL = ""
MCP_CLIENT = None
TOOLS_AVAIL = [{}]


class ModelClient(Enum):
    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"


def load_env_vars(client: ModelClient):
    from delo_mcp_client.configuration import load_config
    from delo_mcp_client.utils import setup_mcp_client
    import os

    config = load_config()

    global MODEL_API_KEY, DELO_KEY_ID, DELO_SECRET, URL, MCP_CLIENT
    client_name = str.upper(client.value)
    MODEL_API_KEY = os.getenv(
        f"{client_name}_API_KEY", config["ENV_VARS"][f"{client_name} API KEY"]
    )
    DELO_KEY_ID = os.getenv("DELO_KEY_ID", config["ENV_VARS"]["DECEPTION LOGIC KEY ID"])
    DELO_SECRET = os.getenv(
        "DELO_SECRET", config["ENV_VARS"]["DECEPTION LOGIC SECRET KEY"]
    )
    URL = config["Hidden"]["URL"]

    for key, value in {
        f"{client_name}_API_KEY": MODEL_API_KEY,
        "DELO_KEY_ID": DELO_KEY_ID,
        "DELO_SECRET": DELO_SECRET,
    }.items():
        if value == "":
            raise ValueError(
                f"{key} is missing a value, make sure relevant values are either configured or in environment!"
            )

    if client == ModelClient.gemini:
        MCP_CLIENT = setup_mcp_client(URL, DELO_KEY_ID, DELO_SECRET)


def load_colors():
    from delo_mcp_client.configuration import load_config
    from prompt_toolkit.styles import Style

    config = load_config()
    
    style = Style.from_dict({
        "user": config['Settings'].get('USER COLOR', 'ansiwhite'),
        '': config['Settings'].get('USER COLOR', 'ansiwhite'),
        "assistant": config['Settings'].get('ASSISTANT COLOR', 'ansiblue')
    })

    return style

@app.command(help="Chat with an LLM. To exit, type exit, quit, q, or kill into the terminal.")
def chat(
    client: ModelClient = typer.Option(
        ModelClient.openai,
        "--client",
        "-c",
        help="The model to use when running the client",
        rich_help_panel="🔧 Optional Settings",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Specific model to use, ex: gpt-4.1",
        rich_help_panel="🔧 Optional Settings",
    ),
):
    import asyncio
    from prompt_toolkit import prompt
    from prompt_toolkit.formatted_text import FormattedText
    from prompt_toolkit import print_formatted_text

    functions = {
        ModelClient.openai: chat_with_openai,
        ModelClient.gemini: chat_with_gemini,
        ModelClient.anthropic: chat_with_anthropic,
    }

    load_env_vars(client)
    style = load_colors()

    chat_log = []
    while True:
        user_input = prompt([('class:user', "You: ")], style=style)
        if user_input.lower() in ["exit", "quit", "q", "kill"]:
            print("Exiting chat...")
            break
        ai_response, chat_log = asyncio.run(
            functions[client](user_input, chat_log, model)
        )
        print_formatted_text(
            FormattedText([("class:assistant", "Deception Logic: " + ai_response)]),
            style=style,
        )


async def chat_with_gemini(prompt, chat_log=None, model=None):
    from google import genai as gemini

    client = gemini.Client(api_key=MODEL_API_KEY)
    if chat_log is None:
        chat_log = []
    if model is None:
        model = "gemini-2.0-flash"

    chat_log.append({"role": "user", "parts": [{"text": prompt}]})

    async with MCP_CLIENT:
        response = await client.aio.models.generate_content(
            model=model,
            config=gemini.types.GenerateContentConfig(tools=[MCP_CLIENT.session]),
            contents=chat_log,
        )

        ai_response = response.text
    chat_log.append({"role": "model", "parts": [{"text": ai_response}]})
    return ai_response, chat_log


async def chat_with_openai(prompt, chat_log=None, model=None):
    from openai import OpenAI

    client = OpenAI(api_key=MODEL_API_KEY)
    if chat_log is None:
        chat_log = []
    if model is None:
        model = "gpt-4.1-mini"

    chat_log.append({"role": "user", "content": prompt})
    response = client.responses.create(
        model=model,
        tools=[
            {
                "type": "mcp",
                "server_label": "delo_mcp",
                "server_url": f"{URL}",
                "require_approval": "never",
                "headers": {
                    "X-DeceptionLogic-KeyId": DELO_KEY_ID,
                    "X-DeceptionLogic-SecretKey": DELO_SECRET,
                },
            },
        ],
        input=chat_log,
    )

    ai_response = response.output_text
    chat_log.append({"role": "assistant", "content": ai_response})
    return ai_response, chat_log


async def chat_with_anthropic(prompt, chat_log=None, model=None):
    import anthropic

    global TOOLS_AVAIL
    client = anthropic.Anthropic(api_key=MODEL_API_KEY)

    if chat_log is None:
        chat_log = []
    if model is None:
        model = "claude-sonnet-4-20250514"

    chat_log.append({"role": "user", "content": prompt})
    response = client.beta.messages.create(
        model=model,
        max_tokens=1000,
        messages=chat_log,
        mcp_servers=[
            {
                "type": "url",
                "url": f"{URL}",
                "name": "delo_mcp",
                "authorization_token": "DELO%sDELO%s" % (DELO_KEY_ID, DELO_SECRET),
            }
        ],
        extra_headers={"anthropic-beta": "mcp-client-2025-04-04"},
    )

    ai_response = ""
    count = 0
    for content in response.content:
        if content.type == "text":
            ai_response = (
                content.text if count == 0 else (ai_response + "\n" + content.text)
            )
            count += 1
    chat_log.append({"role": "assistant", "content": ai_response})
    return ai_response, chat_log


if __name__ == "__main__":
    app()
