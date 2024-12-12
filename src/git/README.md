# mcp-server-git: A git MCP server

## Overview

A Model Context Protocol server for Git repository interaction and automation. This server provides tools to read, search, and manipulate Git repositories via Large Language Models.

Please note that mcp-server-git is currently in early development. The functionality and available tools are subject to change and expansion as we continue to develop and improve the server.

### Tools

1. `git_status`
   - Shows the working tree status
   - Input:
     - `repo_path` (string): Path to Git repository
   - Returns: Current status of working directory as text output

2. `git_diff_unstaged`
   - Shows changes in working directory not yet staged
   - Input:
     - `repo_path` (string): Path to Git repository
   - Returns: Diff output of unstaged changes

3. `git_diff_staged`
   - Shows changes that are staged for commit
   - Input:
     - `repo_path` (string): Path to Git repository
   - Returns: Diff output of staged changes

4. `git_diff`
   - Shows differences between branches or commits
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `target` (string): Target branch or commit to compare with
   - Returns: Diff output comparing current state with target

5. `git_commit`
   - Records changes to the repository
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `message` (string): Commit message
   - Returns: Confirmation with new commit hash

6. `git_add`
   - Adds file contents to the staging area
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `files` (string[]): Array of file paths to stage
   - Returns: Confirmation of staged files

7. `git_reset`
   - Unstages all staged changes
   - Input:
     - `repo_path` (string): Path to Git repository
   - Returns: Confirmation of reset operation

8. `git_log`
   - Shows the commit logs
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `max_count` (number, optional): Maximum number of commits to show (default: 10)
   - Returns: Array of commit entries with hash, author, date, and message

9. `git_create_branch`
   - Creates a new branch
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `branch_name` (string): Name of the new branch
     - `start_point` (string, optional): Starting point for the new branch
   - Returns: Confirmation of branch creation
10. `git_checkout`
   - Switches branches
   - Inputs:
     - `repo_path` (string): Path to Git repository
     - `branch_name` (string): Name of branch to checkout
   - Returns: Confirmation of branch switch

11. `git_push`
    - Pushes changes to a remote repository
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `remote` (string, optional): Remote name (default: "origin")
      - `branch` (string, optional): Branch to push
    - Returns: Confirmation of push operation

12. `git_pull`
    - Pulls changes from a remote repository
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `remote` (string, optional): Remote name (default: "origin")
      - `branch` (string, optional): Branch to pull
    - Returns: Confirmation of pull operation

13. `git_fetch`
    - Fetches changes from a remote repository
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `remote` (string, optional): Remote name (default: "origin")
      - `branch` (string, optional): Branch to fetch
    - Returns: Confirmation of fetch operation

14. `git_get_config`
    - Returns the Git repository configuration
    - Input:
      - `repo_path` (string): Path to Git repository
    - Returns: Contents of the repository's .git/config file

15. `git_get_remote_url`
    - Gets the URL of a specific remote
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `remote` (string): Name of the remote (default: "origin")
    - Returns: URL of the specified remote

16. `git_list_remotes`
    - Lists all configured remotes
    - Input:
      - `repo_path` (string): Path to Git repository
    - Returns: List of remotes with their URLs

17. `git_add_remote`
    - Adds a new remote
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `name` (string): Name for the new remote
      - `url` (string): URL of the remote repository
    - Returns: Confirmation of remote addition

18. `git_remove_remote`
    - Removes a remote
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `name` (string): Name of the remote to remove
    - Returns: Confirmation of remote removal

19. `git_list_branches`
    - Lists all local and remote branches
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `remote` (boolean): Include remote branches (default: true)
    - Returns: List of branches

20. `git_delete_branch`
    - Deletes a branch
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `branch_name` (string): Name of branch to delete
      - `force` (boolean): Force deletion (default: false)
    - Returns: Confirmation of branch deletion

21. `git_rename_branch`
    - Renames a branch
    - Inputs:
      - `repo_path` (string): Path to Git repository
      - `old_name` (string): Current name of the branch
      - `new_name` (string): New name for the branch
    - Returns: Confirmation of branch rename

22. `git_get_current_branch`
    - Gets the name of the current branch
    - Input:
      - `repo_path` (string): Path to Git repository
    - Returns: Name of the current branch

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-git*.

### Using PIP

Alternatively you can install `mcp-server-git` via pip:

```
pip install mcp-server-git
```

After installation, you can run it as a script using:

```
python -m mcp_server_git
```

## Configuration

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "git": {
    "command": "uvx",
    "args": ["mcp-server-git", "--repository", "path/to/git/repo"]
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "git": {
    "command": "python",
    "args": ["-m", "mcp_server_git", "--repository", "path/to/git/repo"]
  }
}
```
</details>

### Usage with [Zed](https://github.com/zed-industries/zed)

Add to your Zed settings.json:

<details>
<summary>Using uvx</summary>

```json
"context_servers": [
  "mcp-server-git": {
    "command": {
      "path": "uvx",
      "args": ["mcp-server-git"]
    }
  }
],
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"context_servers": {
  "mcp-server-git": {
    "command": {
      "path": "python",
      "args": ["-m", "mcp_server_git"]
    }
  }
},
```
</details>

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-git
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/git
npx @modelcontextprotocol/inspector uv run mcp-server-git
```

Running `tail -n 20 -f ~/Library/Logs/Claude/mcp*.log` will show the logs from the server and may
help you debug any issues.

## Development

If you are doing local development, there are two ways to test your changes:

1. Run the MCP inspector to test your changes. See [Debugging](#debugging) for run instructions.

2. Test using the Claude desktop app. Add the following to your `claude_desktop_config.json`:

```json
"git": {
  "command": "uv",
  "args": [
    "--directory",
    "/<path to mcp-servers>/mcp-servers/src/git",
    "run",
    "mcp-server-git"
  ]
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
