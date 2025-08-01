import os
import typer
from honeydb_mcp_client.load_app import app

@app.command(name="configure", help="Configure settings and environment variables for the MCP Client.")
def config(
        env_vars: bool = typer.Option(False, "--environment", "-e", help="Edit your environment variables", rich_help_panel="🔧 Optional Settings"),
        settings: bool = typer.Option(False, "--settings", "-s", help="Edit user settings like text color", rich_help_panel="🔧 Optional Settings")):
    config_file = os.path.expanduser('~/.config/honeydb/mcp.conf')
    config = load_config(config_file)

    change_locs = []
    change_locs.append('Settings') if settings else None
    change_locs.append('ENV_VARS') if env_vars or not change_locs else None


    for loc in reversed(change_locs):
        for key, value in config[loc].items():
            if (loc == 'ENV_VARS' and len(value) > 4):
                input_text = input(f"{str.upper(key)} [**********{value[-4:]}]: ")
            else:
                input_text = input(f"{str.upper(key)} [{value}]: ")
            config[loc][key] = value if not input_text else input_text

        with open(config_file, 'w') as f:
            config.write(f)

def load_config(config_file = os.path.expanduser('~/.config/honeydb/mcp.conf')):
    import configparser, dotenv
    from pathlib import Path

    config = configparser.ConfigParser()
    config_file = Path(config_file)
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        dotenv.load_dotenv()
        config['ENV_VARS'] = {
            'HONEYDB API ID': "",
            'HONEYDB API KEY': "",
            'OPENAI API KEY': "",
            'GEMINI API KEY': "",
            'ANTHROPIC API KEY': ""
        }

        config['Settings'] = {
            'USER COLOR': "red",
            "ASSISTANT COLOR": "cyan"
        }

        config['Hidden'] = {
            'URL': os.getenv("MCP_URL", "https://honeydb-mcp.net/sse")
        }

        config_file.parent.mkdir(exist_ok=True)

        with open(config_file, 'w') as f:
            config.write(f)

    return config

if __name__ == '__main__':
    config()