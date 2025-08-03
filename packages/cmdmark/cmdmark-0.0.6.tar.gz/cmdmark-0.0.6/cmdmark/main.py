import argparse
import os
import subprocess
import yaml
from . import __version__

DEFAULT_CONFIG_DIR = os.path.expanduser("~/.command_bookmarks")
ENV_CONFIG_DIR = "CMDMARK_CONFIG_DIR"


IGNORED_PREFIX = ".git"


def list_items(path):
    """List folders and YAML files while skipping git metadata."""
    items = [item for item in os.listdir(path) if not item.startswith(IGNORED_PREFIX)]
    items = sorted(items)
    for idx, item in enumerate(items, 1):
        print(f"{idx}. {item}")
    return items


def list_commands(data, verbose: bool = False):
    """List available commands from a parsed YAML file.

    When ``verbose`` is ``True``, each command's description is printed
    alongside the command itself.
    """
    if "commands" not in data or not isinstance(data["commands"], dict):
        print("No valid commands found in the YAML file.")
        return []

    commands = []
    header = "id. command"
    if verbose:
        header += " - description"
    print(header)
    for idx, (alias, cmd_data) in enumerate(data["commands"].items(), 1):
        if isinstance(cmd_data, dict) and "command" in cmd_data:
            cmd = cmd_data["command"]
            if verbose and "description" in cmd_data:
                desc = cmd_data["description"]
                print(f"{idx}. {cmd} - {desc}")
            else:
                print(f"{idx}. {cmd}")
            commands.append(cmd)
        else:
            print(f"Invalid command format for {alias}")
    return commands


def select_item(items):
    """Prompt user to select an item by number."""
    while True:
        try:
            choice = int(input("Select a number: ")) - 1
            if 0 <= choice < len(items):
                return items[choice]
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def load_yaml(filepath):
    """Load commands from a YAML file."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def parse_args(argv: list[str] | None = None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Manage command bookmarks stored in YAML files."
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-c",
        "--config-dir",
        default=os.environ.get(ENV_CONFIG_DIR, DEFAULT_CONFIG_DIR),
        help="Path to configuration directory (default: %(default)s)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    return parser.parse_args(argv)


def run_command(command: str) -> None:
    """Execute the given command with ``subprocess.run``.

    Parameters
    ----------
    command:
        Command string to execute.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non-zero status.
    """
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        raise


def main() -> None:
    args = parse_args()
    config_dir = os.path.expanduser(args.config_dir)

    if not os.path.exists(config_dir):
        print(f"Config folder not found: {config_dir}")
        return

    print("=== Categories ===")
    categories = list_items(config_dir)
    selected_category = select_item(categories)
    category_path = os.path.join(config_dir, selected_category)

    print(f"\n=== {selected_category} Files ===")
    files = [f for f in list_items(category_path) if f.endswith(".yml")]
    if not files:
        print("No YAML files found.")
        return

    selected_file = select_item(files)
    file_path = os.path.join(category_path, selected_file)

    print(f"\n=== {selected_file} Commands ===")
    data = load_yaml(file_path)
    if "commands" not in data:
        print("Invalid YAML format.")
        return

    command_keys = list_commands(data, verbose=args.verbose)
    command = select_item(command_keys)

    print(f"\nExecuting: {command}\n")
    run_command(command)


if __name__ == "__main__":
    main()
