import typer
from delo_mcp_client.load_app import app


def load_env():
    from delo_mcp_client.configuration import load_config
    from delo_mcp_client.utils import setup_mcp_client
    import os

    config = load_config()

    DELO_KEY_ID = os.getenv("DELO_KEY_ID", config["ENV_VARS"]["DECEPTION LOGIC KEY ID"])
    DELO_SECRET = os.getenv(
        "DELO_SECRET", config["ENV_VARS"]["DECEPTION LOGIC SECRET KEY"]
    )
    URL = config["Hidden"]["URL"]
    SSH_PATH = config["ENV_VARS"]["SSH CONFIG FILE"]

    return setup_mcp_client(URL, DELO_KEY_ID, DELO_SECRET), SSH_PATH


@app.command(name="deploy_agent", help="Deploy an agent to a remote host.")
def deploy_agent(
    remote_host: str = typer.Option(
        "127.0.0.1",
        "--remote-host",
        "-r",
        help="The remote host to deploy the agent to.",
    )
):
    import asyncio

    description = "Temp Key for Agent Deployment 123"

    asyncio.run(deploy(remote_host, description))


async def deploy(remote_host, description):
    from delo_mcp_client.utils import get_guid
    import subprocess

    # Load environment variables
    mcp_client, ssh_key_path = load_env()

    async with mcp_client:
        await mcp_client.call_tool(
            "put_auto_config_key",
            {
                "expire_quantity": 0,
                "expire_unit": "hours",
                "description": description,
            },
        )
        resp = await mcp_client.call_tool("get_auto_config_keys", {})
        guid = get_guid(resp.content, description).strip()
        print(guid)

    cmd = [
        "ssh",
        "-t",
        "-i",
        ssh_key_path,
        remote_host,
        f"curl -sL https://api.deceptionlogic.net/install | sudo bash -s {guid}",
    ]

    subprocess.run(cmd, check=True)

    async with mcp_client:
        resp = await mcp_client.call_tool("delete_auto_config_key", {"guid": guid})