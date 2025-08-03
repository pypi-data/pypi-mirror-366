# cmdmark

A CLI tool for managing commands like bookmarks. This Python script provides a simple way to manage and execute frequently used commands via YAML configuration files. Think of it like a bookmark manager, but for your terminal commands.

## Features

*   **Categorized Commands:** Organize your commands into categories stored in subfolders.
*   **YAML Configuration:** Define commands and their descriptions in easy-to-read YAML files.
*   **Interactive Selection:** Choose categories, files, and commands interactively from the terminal.
*   **Direct Execution:** Execute selected commands directly within the script.
*   **Git-Aware:** Git metadata files (e.g., `.git` folders) are ignored when listing categories and YAML files.
*   **Verbose Mode:** Pass `-v` to show each command's description when listing commands.


## Setup

1.  **Installation:**

    The preferred way to install `cmdmark` is via pipx (recommended) or pip:
    ```bash
    pipx install cmdmark # recommended way.
    # OR
    pip install cmdmark
    ```
    This will install `cmdmark` and its dependency, `PyYAML`. This project requires Python 3.12 or higher.

2.  **Configuration Directory:** The script uses a configuration directory located at `~/.command_bookmarks`. Make sure that the directory exists. You may create some sub-directories in `~/.command_bookmarks` to categorize your commands, and create yml files to store the relative commands. You can override this location by setting the environment variable `CMDMARK_CONFIG_DIR`.

    For example, in your shell configuration (e.g. `~/.bashrc` or `~/.zshrc`):

    ```bash
    export CMDMARK_CONFIG_DIR="$HOME/my_cmdmarks"
    ```

3.  **YAML Files:** Create YAML files within the configuration directory (or its subdirectories) to define your commands.  The structure of the YAML file is as follows:

    ```yaml
    commands:
      alias1:
        command: "your_command_here"
        description: "A short description of the command"
      alias2:
        command: "another_command"
        description: "Another description"
    ```

    *   `commands`: The top-level key.
    *   `alias1`, `alias2`, etc.:  Short, user-friendly aliases for your commands.  These are displayed in the selection menu.
    *   `command`: The actual command to be executed.
    *   `description`:  (Optional) A brief description of the command.

## Usage

1.  **Run the script:**

    ```bash
    cmdmark
    ```
    Use `-v` or `--verbose` to also show each command's description when listing commands.

2.  **Interactive Navigation:**

    *   The script will first list the available categories (subfolders) within `~/.command_bookmarks`.
    *   Select a category by entering its number.
    *   The script will then list the YAML files within the selected category.
    *   Select a YAML file by entering its number.
    *   Finally, the script will list the commands defined in the selected YAML file. When `-v` is used, each command's description is shown alongside the command itself.
    *   Select a command by entering its number.

3.  **Command Execution:** The selected command will be executed in your terminal.

## Example

Let's say you have the following structure (see tests/samples).
For example, the directory might look like:

```
~/.command_bookmarks/
├── git/
│   ├── basic.yml
│   └── branch.yml
└── sys/
    └── disk.yml
```

The files under `tests/sample/` provide ready-made examples you can copy into your configuration directory.

`tests/sample/git/basic.yml` includes common git commands:

```yaml
commands:
  status:
    command: "git status"
    description: "Show the working tree status"
  add_all:
    command: "git add ."
    description: "Add all changes to staging"
  commit:
    command: "git commit -m"
    description: "Commit changes (requires message)"
```

`tests/sample/sys/disk.yml` defines a couple of useful system commands:

```yaml
commands:
  check_disk:
    command: "df -h"
    description: "Check disk space usage"
  disk_usage:
    command: "du -sh ~"
    description: "Show disk usage of home directory"
```

### Quick demo

```bash
cp -r tests/sample/* ~/.command_bookmarks/
cmdmark
```

Select a category (e.g. `git`), choose a YAML file such as `basic.yml`, and then pick a command like `status`. `cmdmark` will run `git status` right away.

## Docker

The repository includes a `Dockerfile` so you can build a containerized
environment for running the tests or invoking the CLI.

```bash
# Build the image
docker build -t cmdmark .

# Run the test suite
docker run --rm cmdmark

# Or start the CLI (override the default command)
docker run --rm -it cmdmark cmdmark
```
