import json
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional

import click
import inquirer
import requests


def install_completion() -> None:
    """Install shell completion for the CLI."""
    import subprocess
    import sys

    # Get the shell type
    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell in ["bash", "zsh", "fish"]:
        # Use Click's built-in completion installation
        cmd = [
            sys.executable,
            "-c",
            f"import click; "
            f"from claude_openrouter_tool.main import app; "
            f'print(app.get_completion("{shell}")',
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            completion_script = result.stdout.strip()

            # Determine completion file path
            home = os.path.expanduser("~")
            if shell == "bash":
                completion_file = os.path.join(home, ".bash_completion")
            elif shell == "zsh":
                completion_file = os.path.join(home, ".zshrc")
            elif shell == "fish":
                completion_dir = os.path.join(home, ".config", "fish", "completions")
                os.makedirs(completion_dir, exist_ok=True)
                completion_file = os.path.join(
                    completion_dir, "claude-openrouter-tool.fish"
                )

            # Write completion script
            with open(completion_file, "a") as f:
                if shell != "fish":
                    f.write("\n# Claude OpenRouter Tool completion\n")
                f.write(completion_script)
                f.write("\n")
    else:
        raise Exception(f"Unsupported shell: {shell}")


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
@click.pass_context
def app(ctx: click.Context) -> None:
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

    # 6. Check if shell completion is installed
    completion_installed = check_completion_installed()
    status = "✓ PASS" if completion_installed else "✗ FAIL"
    click.echo(f"6. Shell completion is installed: {status}")
    if not completion_installed:
        click.echo(
            "   Run 'claude-openrouter-tool --install-completion' "
            "to enable tab completion"
        )

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

    # Load existing configuration if available
    existing_config = load_config()
    existing_api_key = ""
    existing_models = []
    existing_default = ""

    if existing_config:
        click.echo("Found existing configuration. Current values will be pre-filled.")
        providers = existing_config.get("Providers", [])
        if providers:
            existing_api_key = providers[0].get("api_key", "")
            existing_models = providers[0].get("models", [])

        router_config = existing_config.get("Router", {})
        existing_default_full = router_config.get("default", "")
        if "," in existing_default_full:
            existing_default = existing_default_full.split(",", 1)[1]

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

    # Pre-fill API key if it exists
    api_key_message = "Please enter your OpenRouter API key (sk-or-...)"
    if existing_api_key:
        api_key_message += f" [current: {existing_api_key[:10]}...]"

    api_key = inquirer.prompt(
        [inquirer.Text("api_key", message=api_key_message, default=existing_api_key)]
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

    # Merge existing models with recommended ones, keeping existing selection as default
    # Remove duplicates, preserve order
    all_models = list(dict.fromkeys(existing_models + recommended_models))
    default_models = (
        existing_models if existing_models else ["deepseek/deepseek-r1:free"]
    )

    questions = [
        inquirer.Checkbox(
            "models",
            message="Select models to use:",
            choices=all_models,
            default=default_models,
        ),
    ]
    answers = inquirer.prompt(questions)
    selected_models = answers["models"]
    click.echo(f"Selected models: {', '.join(selected_models)}")

    # Determine default model selection
    default_model_choice = None
    if existing_default and existing_default in selected_models:
        default_model_choice = existing_default
    elif selected_models:
        default_model_choice = selected_models[0]

    default_model_question = [
        inquirer.List(
            "default_model",
            message="Select your default model:",
            choices=selected_models,
            default=default_model_choice,
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

        # Install shell completion
        click.echo("\nInstalling shell completion...")
        try:
            install_completion()
            click.echo("Shell completion installed successfully!")
            click.echo(
                "Please restart your shell or run: source ~/.bashrc (or equivalent)"
            )
        except Exception as e:
            click.echo(f"Warning: Could not install shell completion: {e}")
            click.echo(
                "You can install it manually later with: "
                "claude-openrouter-tool --install-completion"
            )

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
@click.option("--category", help="Filter models by category (e.g., programming)")
@click.option("--limit", type=int, help="Limit number of models displayed")
@click.option("--free", is_flag=True, help="Show only free models")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def models(
    category: Optional[str], limit: Optional[int], free: bool, output_json: bool
) -> None:
    """Fetch and display available models from OpenRouter."""
    try:
        models_data = fetch_openrouter_models(category)
        if not models_data:
            click.echo("Failed to fetch models from OpenRouter API")
            return

        filtered_models = filter_models(models_data, free_only=free)

        if limit:
            filtered_models = filtered_models[:limit]

        if output_json:
            click.echo(json.dumps(filtered_models, indent=2))
        else:
            display_models_table(filtered_models)

    except Exception as e:
        click.echo(f"Error fetching models: {e}")


def fetch_openrouter_models(
    category: Optional[str] = None,
) -> Optional[List[Dict[str, Any]]]:
    """Fetch available models from OpenRouter API."""
    url = "https://openrouter.ai/api/v1/models"
    params = {}
    if category:
        params["category"] = category

    config_data = load_config()
    headers = {"Content-Type": "application/json"}

    if config_data and config_data.get("Providers"):
        api_key = config_data["Providers"][0].get("api_key", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        models_list = data.get("data", [])
        return models_list if isinstance(models_list, list) else []
    except Exception as e:
        click.echo(f"API request failed: {e}")
        return None


def fetch_openrouter_categories() -> Optional[List[str]]:
    """Fetch realistic categories from OpenRouter models."""
    models_data = fetch_openrouter_models()
    if not models_data:
        return None

    # Count occurrences to filter out categories with too few models
    provider_counts: Dict[str, int] = {}
    capabilities = set()

    for model in models_data:
        # Extract provider/organization
        model_id = model.get("id", "")
        if "/" in model_id:
            provider = model_id.split("/")[0]
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        # Extract capabilities from architecture
        architecture = model.get("architecture", {})
        if isinstance(architecture, dict):
            # Add multimodal capability
            modality = architecture.get("modality", "")
            if modality == "text+image->text":
                capabilities.add("multimodal")
            elif modality == "text->text":
                capabilities.add("text-only")

            # Add input capabilities
            input_modalities = architecture.get("input_modalities", [])
            if isinstance(input_modalities, list):
                if "image" in input_modalities:
                    capabilities.add("vision")
                if "file" in input_modalities:
                    capabilities.add("file-processing")

        # Check if model is free
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")
        try:
            if float(prompt_price) == 0.0 and float(completion_price) == 0.0:
                capabilities.add("free")
        except (ValueError, TypeError):
            pass

    # Only include providers with 3+ models and add capabilities
    categories = []

    # Add major providers (3+ models)
    major_providers = [
        provider for provider, count in provider_counts.items() if count >= 3
    ]
    categories.extend(sorted(major_providers))

    # Add capability categories
    categories.extend(sorted(capabilities))

    return categories if categories else []


def display_categories_table(categories: List[str]) -> None:
    """Display categories in a formatted list."""
    if not categories:
        click.echo("No categories found.")
        return

    # Separate providers from capabilities
    capability_list = ["file-processing", "free", "multimodal", "text-only", "vision"]
    providers = [c for c in categories if c not in capability_list]
    capabilities = [c for c in categories if c in capability_list]

    click.echo(f"\nFound {len(categories)} categories:\n")

    if providers:
        click.echo("Providers (major ones with 3+ models):")
        for i, provider in enumerate(providers, 1):
            click.echo(f"  {i:2d}. {provider}")
        click.echo()

    if capabilities:
        click.echo("Capabilities:")
        for i, capability in enumerate(capabilities, len(providers) + 1):
            click.echo(f"  {i:2d}. {capability}")

    click.echo(f"\nTotal: {len(categories)} categories")
    click.echo("\nNote: OpenRouter API doesn't support filtering by provider names.")
    click.echo(
        "You can use capabilities like 'free', 'multimodal', 'vision' for filtering."
    )


def filter_models(
    models: List[Dict[str, Any]], free_only: bool = False
) -> List[Dict[str, Any]]:
    """Filter models based on criteria."""
    if not free_only:
        return models

    filtered = []
    for model in models:
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")

        try:
            if float(prompt_price) == 0.0 and float(completion_price) == 0.0:
                filtered.append(model)
        except (ValueError, TypeError):
            continue

    return filtered


def check_completion_installed() -> bool:
    """Check if shell completion is installed."""
    shell = os.environ.get("SHELL", "").split("/")[-1]
    home = os.path.expanduser("~")

    if shell == "bash":
        completion_file = os.path.join(home, ".bash_completion")
        if os.path.exists(completion_file):
            with open(completion_file, "r") as f:
                return "claude-openrouter-tool" in f.read()
    elif shell == "zsh":
        zshrc_file = os.path.join(home, ".zshrc")
        if os.path.exists(zshrc_file):
            with open(zshrc_file, "r") as f:
                return "claude-openrouter-tool" in f.read()
    elif shell == "fish":
        completion_file = os.path.join(
            home, ".config", "fish", "completions", "claude-openrouter-tool.fish"
        )
        return os.path.exists(completion_file)

    return False


def display_models_table(models: List[Dict[str, Any]]) -> None:
    """Display models in a formatted table."""
    if not models:
        click.echo("No models found matching the criteria.")
        return

    click.echo(f"\nFound {len(models)} models:\n")
    click.echo(f"{'Model ID':<40} {'Name':<30} {'Context':<10} {'Pricing':<15}")
    click.echo("-" * 100)

    for model in models:
        model_id = model.get("id", "N/A")[:39]
        name = model.get("name", "N/A")[:29]
        context_length = str(model.get("context_length", "N/A"))[:9]

        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")

        try:
            if float(prompt_price) == 0.0 and float(completion_price) == 0.0:
                price_str = "FREE"
            else:
                price_str = f"${prompt_price}"
        except (ValueError, TypeError):
            price_str = "N/A"

        click.echo(f"{model_id:<40} {name:<30} {context_length:<10} {price_str:<15}")

    click.echo(f"\nTotal: {len(models)} models")


@app.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def categories(output_json: bool) -> None:
    """Fetch and display available model categories from OpenRouter."""
    try:
        categories_data = fetch_openrouter_categories()
        if not categories_data:
            click.echo("Failed to fetch categories from OpenRouter API")
            return

        if output_json:
            click.echo(json.dumps(categories_data, indent=2))
        else:
            display_categories_table(categories_data)
    except Exception as e:
        click.echo(f"Error fetching categories: {e}")


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
