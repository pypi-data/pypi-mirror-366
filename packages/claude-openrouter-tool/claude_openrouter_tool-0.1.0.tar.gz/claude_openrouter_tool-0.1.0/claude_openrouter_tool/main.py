import json
import os
import shutil
import subprocess
from typing import Any, Dict, Optional

import click
import inquirer


def get_config_path() -> str:
    """Get the path to the configuration file."""
    return os.path.join(os.path.expanduser("~/.claude-code-router"), "config.json")


def load_config() -> Optional[Dict[str, Any]]:
    """Load the configuration file."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        click.echo(f"Error reading configuration file: {e}")
        return None


def save_config(config_data: Dict[str, Any]) -> bool:
    """Save the configuration file."""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)

    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        return True
    except IOError as e:
        click.echo(f"Error saving configuration file: {e}")
        return False


@click.group()
def app() -> None:
    """A tool to manage OpenRouter integration with Claude Code."""
    pass


@app.command()
@click.argument("name")
def hello(name: str) -> None:
    """Says hello."""
    click.echo(f"Hello {name}")


@app.command()
def check() -> None:
    """Checks the current setup."""
    click.echo("Performing setup checks...")

    all_checks_passed = True

    # 1. Check if npm is installed
    npm_installed = shutil.which("npm") is not None
    status = "✓ PASS" if npm_installed else "✗ FAIL"
    click.echo(f"1. npm is installed: {status}")
    if not npm_installed:
        all_checks_passed = False
        click.echo("   Please install Node.js and npm from: https://nodejs.org/")

    # 2. Check if @musistudio/claude-code-router is installed globally
    router_installed = False
    if npm_installed:
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "@musistudio/claude-code-router"],
                capture_output=True,
                text=True,
            )
            router_installed = result.returncode == 0
        except subprocess.CalledProcessError:
            router_installed = False

    status = "✓ PASS" if router_installed else "✗ FAIL"
    click.echo(f"2. @musistudio/claude-code-router is installed: {status}")
    if not router_installed:
        all_checks_passed = False
        click.echo(
            "   Run 'claude-openrouter-tool setup' or "
            "'npm install -g @musistudio/claude-code-router'"
        )

    # 3. Check if configuration file exists
    config_path = get_config_path()
    config_exists = os.path.exists(config_path)
    status = "✓ PASS" if config_exists else "✗ FAIL"
    click.echo(f"3. Configuration file exists: {status}")
    if not config_exists:
        all_checks_passed = False
        click.echo(f"   Configuration file not found at: {config_path}")
        click.echo("   Run 'claude-openrouter-tool setup' to create it")

        # Exit early if no config file
        click.echo(f"\nOverall Status: {'✓ PASS' if all_checks_passed else '✗ FAIL'}")
        return

    # 4. Validate JSON structure and required keys
    config_data = load_config()
    config_valid = False
    if config_data is not None:
        required_keys = ["Providers", "Router"]
        has_required_keys = all(key in config_data for key in required_keys)

        providers_valid = False
        if has_required_keys and isinstance(config_data.get("Providers"), list):
            if len(config_data["Providers"]) > 0:
                provider = config_data["Providers"][0]
                provider_required_keys = ["name", "api_base_url", "api_key", "models"]
                providers_valid = all(key in provider for key in provider_required_keys)

        router_valid = False
        if has_required_keys and isinstance(config_data.get("Router"), dict):
            router_valid = "default" in config_data["Router"]

        config_valid = has_required_keys and providers_valid and router_valid

    status = "✓ PASS" if config_valid else "✗ FAIL"
    click.echo(f"4. Configuration file is valid: {status}")
    if not config_valid:
        all_checks_passed = False
        click.echo(
            "   Configuration file has invalid structure or missing required keys"
        )
        click.echo("   Run 'claude-openrouter-tool setup' to recreate it")

    # 5. Optional: Test API key validity
    api_key_valid = None
    if config_valid and config_data:
        api_key = config_data["Providers"][0].get("api_key", "")
        if api_key:
            try:
                import requests

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                response = requests.get(
                    "https://openrouter.ai/api/v1/models", headers=headers, timeout=10
                )
                api_key_valid = response.status_code == 200
            except Exception as e:
                api_key_valid = False
                click.echo(f"   API test failed: {str(e)}")

    if api_key_valid is not None:
        status = "✓ PASS" if api_key_valid else "✗ FAIL"
        click.echo(f"5. API key is valid: {status}")
        if not api_key_valid:
            all_checks_passed = False
            click.echo("   API key may be invalid or OpenRouter API is unreachable")
            click.echo("   Check your API key in the configuration")
    else:
        click.echo("5. API key validation: SKIPPED (no valid config or API key)")

    click.echo(f"\nOverall Status: {'✓ PASS' if all_checks_passed else '✗ FAIL'}")
    if all_checks_passed:
        click.echo("All checks passed! Your setup is ready to use.")
    else:
        click.echo("Some checks failed. Please address the issues above.")


@app.command()
def update() -> None:
    """Updates the core dependency."""
    click.echo("Updating @musistudio/claude-code-router...")
    try:
        result = subprocess.run(
            ["npm", "install", "-g", "@musistudio/claude-code-router@latest"],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout)
        click.echo("Update successful!")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error updating: {e.stderr}")
        click.echo("Update failed.")


@app.command()
def setup() -> None:
    """Initiates the setup wizard."""
    click.echo("Starting setup wizard...")

    click.echo("Verifying npm installation...")
    if shutil.which("npm") is None:
        click.echo("Error: npm is not installed. Please install Node.js and npm first.")
        click.echo("You can download it from: https://nodejs.org/en/download/")
        return
    click.echo("npm is installed.")

    click.echo("Installing @musistudio/claude-code-router...")
    try:
        subprocess.run(
            ["npm", "install", "-g", "@musistudio/claude-code-router"],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo("@musistudio/claude-code-router installed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error installing @musistudio/claude-code-router: {e.stderr}")
        click.echo("Installation failed.")
        return

    api_key = inquirer.prompt(
        [
            inquirer.Text(
                "api_key", message="Please enter your OpenRouter API key (sk-or-...)"
            )
        ]
    )["api_key"]
    click.echo(f"API Key: {api_key}")

    # Recommended models from research-report.md
    recommended_models = [
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-v3-0324:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "meta-llama/llama-3.3-70b-multilingual",
        "meta-llama/llama-3.2-3b",
        "meta-llama/llama-3.2-1b",
        "mistralai/mistral-small-latest",
        "mistralai/mixtral-8x7b-instruct-v0.1",
    ]

    questions = [
        inquirer.Checkbox(
            "models",
            message="Select models to use:",
            choices=recommended_models,
            default=["deepseek/deepseek-r1:free"],
        ),
    ]
    answers = inquirer.prompt(questions)
    selected_models = answers["models"]
    click.echo(f"Selected models: {', '.join(selected_models)}")

    default_model_question = [
        inquirer.List(
            "default_model",
            message="Select your default model:",
            choices=selected_models,
            default=selected_models[0] if selected_models else None,
        ),
    ]
    default_model = inquirer.prompt(default_model_question)["default_model"]
    click.echo(f"Default model set to: {default_model}")

    # Create configuration
    config_data = {
        "Providers": [
            {
                "name": "openrouter",
                "api_base_url": "https://openrouter.ai/api/v1/chat/completions",
                "api_key": api_key,
                "models": selected_models,
            }
        ],
        "Router": {"default": f"openrouter,{default_model}"},
    }

    if save_config(config_data):
        click.echo(f"Configuration saved to: {get_config_path()}")
        click.echo("Setup complete!")
    else:
        click.echo("Failed to save configuration.")
        return


@app.command()
def start() -> None:
    """Starts Claude Code with OpenRouter configuration."""
    click.echo("Starting Claude Code with OpenRouter configuration...")

    # Check if claude command is available
    if shutil.which("claude") is None:
        click.echo("Error: 'claude' command not found.")
        click.echo(
            "Please make sure Claude Code is installed and available in your PATH."
        )
        return

    # Load configuration
    config_data = load_config()
    if config_data is None:
        click.echo("Error: No configuration file found.")
        click.echo("Please run 'claude-openrouter-tool setup' first.")
        return

    # Validate configuration structure
    providers = config_data.get("Providers")
    if not isinstance(providers, list) or len(providers) == 0:
        click.echo("Error: Invalid configuration - no providers found.")
        click.echo(
            "Please run 'claude-openrouter-tool setup' to recreate the configuration."
        )
        return

    provider = config_data["Providers"][0]
    api_key = provider.get("api_key", "")
    api_base_url = provider.get("api_base_url", "")

    if not api_key:
        click.echo("Error: No API key found in configuration.")
        click.echo("Please run 'claude-openrouter-tool config' to set your API key.")
        return

    # Get default model from Router configuration
    router_config = config_data.get("Router", {})
    default_model = router_config.get("default", "")

    if not default_model or "," not in default_model:
        click.echo("Error: No default model configured.")
        click.echo("Please run 'claude-openrouter-tool config' to set a default model.")
        return

    # Extract model name from "openrouter,model_name" format
    model_name = default_model.split(",", 1)[1]

    # Set up environment variables for OpenRouter
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = api_key
    env["OPENROUTER_API_BASE"] = api_base_url
    env["OPENROUTER_MODEL"] = model_name

    click.echo(f"Using model: {model_name}")
    click.echo(f"API Base URL: {api_base_url}")
    click.echo("Launching Claude Code...")

    try:
        # Launch Claude Code with OpenRouter environment variables
        # Use exec to replace the current process so signals are handled properly
        os.execvpe("claude", ["claude"], env)
    except OSError as e:
        click.echo(f"Error launching Claude Code: {e}")
        click.echo("Please make sure Claude Code is properly installed.")


@app.command()
def config() -> None:
    """Launches an interactive menu to manage existing configuration."""
    config_data = load_config()
    if config_data is None:
        click.echo(
            "No configuration file found. "
            "Please run 'claude-openrouter-tool setup' first."
        )
        return

    while True:
        menu_options = [
            "View Configuration",
            "Edit API Key",
            "Add Model",
            "Remove Model",
            "Set Default Model",
            "Save and Exit",
        ]

        questions = [
            inquirer.List(
                "action",
                message="Configuration Menu - Select an option:",
                choices=menu_options,
            ),
        ]

        answer = inquirer.prompt(questions)
        if not answer:  # User pressed Ctrl+C
            break

        action = answer["action"]

        if action == "View Configuration":
            view_configuration(config_data)
        elif action == "Edit API Key":
            edit_api_key(config_data)
        elif action == "Add Model":
            add_model(config_data)
        elif action == "Remove Model":
            remove_model(config_data)
        elif action == "Set Default Model":
            set_default_model(config_data)
        elif action == "Save and Exit":
            if save_config(config_data):
                click.echo("Configuration saved successfully!")
            else:
                click.echo("Failed to save configuration.")
            break


def view_configuration(config_data: Dict[str, Any]) -> None:
    """Display the current configuration in a readable format."""
    click.echo("\n=== Current Configuration ===")
    click.echo(json.dumps(config_data, indent=2))
    click.echo("=" * 30)
    input("\nPress Enter to continue...")


def edit_api_key(config_data: Dict[str, Any]) -> None:
    """Allow user to edit the API key."""
    current_key = config_data.get("Providers", [{}])[0].get("api_key", "")
    click.echo(
        f"Current API key: {current_key[:10]}..."
        if current_key
        else "Current API key: Not set"
    )

    questions = [
        inquirer.Text(
            "new_api_key",
            message="Enter new OpenRouter API key (sk-or-...):",
            default=current_key,
        ),
    ]

    answer = inquirer.prompt(questions)
    if answer and answer["new_api_key"]:
        if config_data.get("Providers"):
            config_data["Providers"][0]["api_key"] = answer["new_api_key"]
            click.echo("API key updated successfully!")
        else:
            click.echo("Error: Invalid configuration structure.")


def add_model(config_data: Dict[str, Any]) -> None:
    """Allow user to add a new model to the configuration."""
    questions = [
        inquirer.Text(
            "new_model",
            message="Enter the model name to add (e.g., deepseek/deepseek-r1:free):",
        ),
    ]

    answer = inquirer.prompt(questions)
    if answer and answer["new_model"]:
        model_name = answer["new_model"].strip()
        if model_name:
            if config_data.get("Providers") and isinstance(
                config_data["Providers"][0].get("models"), list
            ):
                if model_name not in config_data["Providers"][0]["models"]:
                    config_data["Providers"][0]["models"].append(model_name)
                    click.echo(f"Model '{model_name}' added successfully!")
                else:
                    click.echo(
                        f"Model '{model_name}' already exists in the configuration."
                    )
            else:
                click.echo("Error: Invalid configuration structure.")


def remove_model(config_data: Dict[str, Any]) -> None:
    """Allow user to remove a model from the configuration."""
    if not config_data.get("Providers") or not isinstance(
        config_data["Providers"][0].get("models"), list
    ):
        click.echo("Error: No models found in configuration.")
        return

    models = config_data["Providers"][0]["models"]
    if not models:
        click.echo("No models available to remove.")
        return

    questions = [
        inquirer.List(
            "model_to_remove",
            message="Select a model to remove:",
            choices=models,
        ),
    ]

    answer = inquirer.prompt(questions)
    if answer and answer["model_to_remove"]:
        model_to_remove = answer["model_to_remove"]
        config_data["Providers"][0]["models"].remove(model_to_remove)
        click.echo(f"Model '{model_to_remove}' removed successfully!")

        # Check if the removed model was the default and prompt to set a new one
        current_default = config_data.get("Router", {}).get("default", "")
        if current_default.endswith(f",{model_to_remove}"):
            if config_data["Providers"][0]["models"]:
                click.echo(
                    "The removed model was the default. "
                    "Please select a new default model."
                )
                set_default_model(config_data)
            else:
                config_data["Router"]["default"] = "openrouter,"
                click.echo("No models left. Default cleared.")


def set_default_model(config_data: Dict[str, Any]) -> None:
    """Allow user to set the default model."""
    if not config_data.get("Providers") or not isinstance(
        config_data["Providers"][0].get("models"), list
    ):
        click.echo("Error: No models found in configuration.")
        return

    models = config_data["Providers"][0]["models"]
    if not models:
        click.echo("No models available to set as default.")
        return

    current_default = config_data.get("Router", {}).get("default", "")
    current_model = current_default.split(",")[-1] if "," in current_default else ""

    questions = [
        inquirer.List(
            "default_model",
            message="Select the default model:",
            choices=models,
            default=current_model if current_model in models else models[0],
        ),
    ]

    answer = inquirer.prompt(questions)
    if answer and answer["default_model"]:
        new_default = f"openrouter,{answer['default_model']}"
        if "Router" not in config_data:
            config_data["Router"] = {}
        config_data["Router"]["default"] = new_default
        click.echo(f"Default model set to: {answer['default_model']}")


if __name__ == "__main__":
    app()
