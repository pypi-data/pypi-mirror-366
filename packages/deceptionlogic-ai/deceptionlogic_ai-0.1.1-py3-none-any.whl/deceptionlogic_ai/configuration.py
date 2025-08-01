import os
import typer
from deceptionlogic_ai.load_app import app


@app.command(
    name="configure",
    help="Configure settings and environment variables for the MCP Client.",
)
def config(
    env_vars: bool = typer.Option(
        False,
        "--environment",
        "-e",
        help="Edit your environment variables",
        rich_help_panel="🔧 Optional Settings",
    ),
    settings: bool = typer.Option(
        False,
        "--settings",
        "-s",
        help="Edit user settings like text color",
        rich_help_panel="🔧 Optional Settings",
    ),
):
    config_file = os.path.expanduser("~/.config/deceptionlogic/mcp.conf")
    config = load_config(config_file)

    change_locs = []
    change_locs.append("Settings") if settings else None
    change_locs.append("ENV_VARS") if env_vars or not change_locs else None

    print(
        "To change a value, type the new value and press enter. To keep the current value, just press enter."
    )

    for loc in reversed(change_locs):
        for key, value in config[loc].items():
            if loc == "ENV_VARS" and len(value) > 4:
                input_text = input(f"{str.upper(key)} [**********{value[-4:]}]: ")
            else:
                input_text = input(f"{str.upper(key)} [{value}]: ")
            config[loc][key] = value if not input_text else input_text

        with open(config_file, "w") as f:
            config.write(f)


def load_config(config_file=os.path.expanduser("~/.config/deceptionlogic/mcp.conf")):
    import configparser
    from pathlib import Path

    config = configparser.ConfigParser()
    config_file = Path(config_file)
    if os.path.exists(config_file):
        config.read(config_file)
        config = validate_config(config)
    else:
        config["ENV_VARS"] = {
            "DECEPTION LOGIC KEY ID": "",
            "DECEPTION LOGIC SECRET KEY": "",
            "OPENAI API KEY": "",
            "GEMINI API KEY": "",
            "ANTHROPIC API KEY": "",
            "SSH CONFIG FILE": "",
        }

        config["Settings"] = {"USER COLOR": "ansiwhite", "ASSISTANT COLOR": "ansiblue"}

        config["Hidden"] = {
            "URL": os.getenv("MCP_URL", "https://deceptionlogic.ai/sse")
        }

        config_file.parent.mkdir(exist_ok=True)

    with open(config_file, "w") as f:
        config.write(f)

    return config


def validate_config(config):
    required_sections = ["ENV_VARS", "Settings", "Hidden"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    required_keys = {
        "ENV_VARS": [
            "DECEPTION LOGIC KEY ID",
            "DECEPTION LOGIC SECRET KEY",
            "OPENAI API KEY",
            "GEMINI API KEY",
            "ANTHROPIC API KEY",
        ],
        "Settings": ["USER COLOR", "ASSISTANT COLOR"],
        "Hidden": ["URL"],
    }

    for section, keys in required_keys.items():
        for key in keys:
            if section == "Settings" and key not in config[section]:
                if key == "USER COLOR":
                    config[section][key] = "ansiwhite"
                else:
                    config[section][key] = "ansiblue"
            elif key not in config[section]:
                config[section][key] = (
                    "" if key != "URL" else "https://deceptionlogic.ai/sse"
                )

    return config


if __name__ == "__main__":
    config()
