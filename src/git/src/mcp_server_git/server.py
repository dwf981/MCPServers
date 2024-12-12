import logging
from pathlib import Path
from typing import Sequence
from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    ClientCapabilities,
    TextContent,
    Tool,
    ListRootsResult,
    RootsCapability,
)
from enum import Enum
import git
from pydantic import BaseModel

class GitStatus(BaseModel):
    repo_path: str

class GitDiffUnstaged(BaseModel):
    repo_path: str

class GitDiffStaged(BaseModel):
    repo_path: str

class GitDiff(BaseModel):
    repo_path: str
    target: str

class GitCommit(BaseModel):
    repo_path: str
    message: str

class GitAdd(BaseModel):
    repo_path: str
    files: list[str]

class GitReset(BaseModel):
    repo_path: str

class GitLog(BaseModel):
    repo_path: str
    max_count: int = 10

class GitCreateBranch(BaseModel):
    repo_path: str
    branch_name: str
    base_branch: str | None = None

class GitCheckout(BaseModel):
    repo_path: str
    branch_name: str

class GitPush(BaseModel):
    repo_path: str
    remote: str = "origin"
    branch: str | None = None

class GitPull(BaseModel):
    repo_path: str
    remote: str = "origin"
    branch: str | None = None

class GitFetch(BaseModel):
    repo_path: str
    remote: str = "origin"
    branch: str | None = None

class GitGetConfig(BaseModel):
    repo_path: str

class GitGetRemoteUrl(BaseModel):
    repo_path: str
    remote: str = "origin"

class GitListRemotes(BaseModel):
    repo_path: str

class GitAddRemote(BaseModel):
    repo_path: str
    name: str
    url: str

class GitRemoveRemote(BaseModel):
    repo_path: str
    name: str

class GitListBranches(BaseModel):
    repo_path: str
    remote: bool = True

class GitDeleteBranch(BaseModel):
    repo_path: str
    branch_name: str
    force: bool = False

class GitRenameBranch(BaseModel):
    repo_path: str
    old_name: str
    new_name: str

class GitGetCurrentBranch(BaseModel):
    repo_path: str

class GitTools(str, Enum):
    STATUS = "git_status"
    DIFF_UNSTAGED = "git_diff_unstaged"
    DIFF_STAGED = "git_diff_staged"
    DIFF = "git_diff"
    COMMIT = "git_commit"
    ADD = "git_add"
    RESET = "git_reset"
    LOG = "git_log"
    CREATE_BRANCH = "git_create_branch"
    CHECKOUT = "git_checkout"
    PUSH = "git_push"
    PULL = "git_pull"
    FETCH = "git_fetch"
    GET_CONFIG = "git_get_config"
    GET_REMOTE_URL = "git_get_remote_url"
    LIST_REMOTES = "git_list_remotes"
    ADD_REMOTE = "git_add_remote"
    REMOVE_REMOTE = "git_remove_remote"
    LIST_BRANCHES = "git_list_branches"
    DELETE_BRANCH = "git_delete_branch"
    RENAME_BRANCH = "git_rename_branch"
    GET_CURRENT_BRANCH = "git_get_current_branch"

def git_status(repo: git.Repo) -> str:
    return repo.git.status()

def git_diff_unstaged(repo: git.Repo) -> str:
    return repo.git.diff()

def git_diff_staged(repo: git.Repo) -> str:
    return repo.git.diff("--cached")

def git_diff(repo: git.Repo, target: str) -> str:
    return repo.git.diff(target)

def git_commit(repo: git.Repo, message: str) -> str:
    commit = repo.index.commit(message)
    return f"Changes committed successfully with hash {commit.hexsha}"

def git_add(repo: git.Repo, files: list[str]) -> str:
    repo.index.add(files)
    return "Files staged successfully"

def git_reset(repo: git.Repo) -> str:
    repo.index.reset()
    return "All staged changes reset"

def git_log(repo: git.Repo, max_count: int = 10) -> list[str]:
    commits = list(repo.iter_commits(max_count=max_count))
    log = []
    for commit in commits:
        log.append(
            f"Commit: {commit.hexsha}\n"
            f"Author: {commit.author}\n"
            f"Date: {commit.authored_datetime}\n"
            f"Message: {commit.message}\n"
        )
    return log

def git_create_branch(repo: git.Repo, branch_name: str, base_branch: str | None = None) -> str:
    if base_branch:
        base = repo.refs[base_branch]
    else:
        base = repo.active_branch

    repo.create_head(branch_name, base)
    return f"Created branch '{branch_name}' from '{base.name}'"

def git_checkout(repo: git.Repo, branch_name: str) -> str:
    repo.git.checkout(branch_name)
    return f"Switched to branch '{branch_name}'"

def git_push(repo: git.Repo, remote: str = "origin", branch: str | None = None) -> str:
    remote_obj = repo.remote(remote)
    refspec = f"{branch}:{branch}" if branch else None
    push_info = remote_obj.push(refspec=refspec)
    return f"Push to {remote} successful"

def git_pull(repo: git.Repo, remote: str = "origin", branch: str | None = None) -> str:
    remote_obj = repo.remote(remote)
    remote_obj.pull(refspec=branch)
    return f"Pull from {remote} successful"

def git_fetch(repo: git.Repo, remote: str = "origin", branch: str | None = None) -> str:
    remote_obj = repo.remote(remote)
    remote_obj.fetch(refspec=branch)
    return f"Fetch from {remote} successful"

def git_get_config(repo: git.Repo) -> str:
    """Returns the contents of the repository's .git/config file."""
    config_path = Path(repo.git_dir) / "config"  # Use Path for proper path joining
    with open(config_path, "r") as f:
        return f.read()

def git_get_remote_url(repo: git.Repo, remote: str = "origin") -> str:
    """Gets the URL of a specific remote."""
    try:
        remote_obj = repo.remote(remote)
        return next(remote_obj.urls)
    except (git.exc.GitCommandError, StopIteration):
        raise ValueError(f"Remote '{remote}' not found or has no URL configured")

def git_list_remotes(repo: git.Repo) -> list[dict[str, str]]:
    """Lists all configured remotes with their URLs."""
    remotes = []
    for remote in repo.remotes:
        urls = list(remote.urls)
        remotes.append({
            "name": remote.name,
            "urls": urls
        })
    return remotes

def git_add_remote(repo: git.Repo, name: str, url: str) -> str:
    """Adds a new remote."""
    try:
        remote = repo.create_remote(name, url)
        return f"Remote '{name}' added successfully with URL: {url}"
    except git.exc.GitCommandError as e:
        raise ValueError(f"Failed to add remote: {e}")

def git_remove_remote(repo: git.Repo, name: str) -> str:
    """Removes a remote."""
    try:
        repo.delete_remote(name)
        return f"Remote '{name}' removed successfully"
    except git.exc.GitCommandError as e:
        raise ValueError(f"Failed to remove remote: {e}")

def git_list_branches(repo: git.Repo, remote: bool = True) -> list[dict[str, str]]:
    """Lists all branches, optionally including remote branches."""
    branches = []
    
    # Add local branches
    for branch in repo.heads:
        branches.append({
            "name": branch.name,
            "type": "local",
            "commit": branch.commit.hexsha,
            "is_active": branch.name == repo.active_branch.name
        })
    
    # Add remote branches if requested
    if remote:
        for ref in repo.remote().refs:
            if not ref.name.endswith('/HEAD'):  # Skip remote HEAD refs
                branches.append({
                    "name": ref.name,
                    "type": "remote",
                    "commit": ref.commit.hexsha,
                    "is_active": False
                })
    
    return branches

def git_delete_branch(repo: git.Repo, branch_name: str, force: bool = False) -> str:
    """Deletes a branch."""
    try:
        repo.delete_head(branch_name, force=force)
        return f"Branch '{branch_name}' deleted successfully"
    except git.exc.GitCommandError as e:
        raise ValueError(f"Failed to delete branch: {e}")

def git_rename_branch(repo: git.Repo, old_name: str, new_name: str) -> str:
    """Renames a branch."""
    try:
        branch = repo.heads[old_name]
        branch.rename(new_name)
        return f"Branch renamed from '{old_name}' to '{new_name}' successfully"
    except (IndexError, git.exc.GitCommandError) as e:
        raise ValueError(f"Failed to rename branch: {e}")

def git_get_current_branch(repo: git.Repo) -> str:
    """Gets the name of the current branch."""
    try:
        return repo.active_branch.name
    except TypeError:
        # Handle detached HEAD state
        return f"HEAD detached at {repo.head.commit.hexsha[:8]}"

async def serve(repository: Path | None) -> None:
    logger = logging.getLogger(__name__)

    if repository is not None:
        try:
            git.Repo(repository)
            logger.info(f"Using repository at {repository}")
        except git.InvalidGitRepositoryError:
            logger.error(f"{repository} is not a valid Git repository")
            return

    server = Server("mcp-git")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=GitTools.STATUS,
                description="Shows the working tree status",
                inputSchema=GitStatus.schema(),
            ),
            Tool(
                name=GitTools.DIFF_UNSTAGED,
                description="Shows changes in the working directory that are not yet staged",
                inputSchema=GitDiffUnstaged.schema(),
            ),
            Tool(
                name=GitTools.DIFF_STAGED,
                description="Shows changes that are staged for commit",
                inputSchema=GitDiffStaged.schema(),
            ),
            Tool(
                name=GitTools.DIFF,
                description="Shows differences between branches or commits",
                inputSchema=GitDiff.schema(),
            ),
            Tool(
                name=GitTools.COMMIT,
                description="Records changes to the repository",
                inputSchema=GitCommit.schema(),
            ),
            Tool(
                name=GitTools.ADD,
                description="Adds file contents to the staging area",
                inputSchema=GitAdd.schema(),
            ),
            Tool(
                name=GitTools.RESET,
                description="Unstages all staged changes",
                inputSchema=GitReset.schema(),
            ),
            Tool(
                name=GitTools.LOG,
                description="Shows the commit logs",
                inputSchema=GitLog.schema(),
            ),
            Tool(
                name=GitTools.CREATE_BRANCH,
                description="Creates a new branch from an optional base branch",
                inputSchema=GitCreateBranch.schema(),
            ),
            Tool(
                name=GitTools.CHECKOUT,
                description="Switches branches",
                inputSchema=GitCheckout.schema(),
            ),
            Tool(
                name=GitTools.PUSH,
                description="Pushes changes to a remote repository",
                inputSchema=GitPush.schema(),
            ),
            Tool(
                name=GitTools.PULL,
                description="Pulls changes from a remote repository",
                inputSchema=GitPull.schema(),
            ),
            Tool(
                name=GitTools.FETCH,
                description="Fetches changes from a remote repository",
                inputSchema=GitFetch.schema(),
            ),
            Tool(
                name=GitTools.GET_CONFIG,
                description="Returns the Git repository configuration",
                inputSchema=GitGetConfig.schema(),
            ),
            Tool(
                name=GitTools.GET_REMOTE_URL,
                description="Gets the URL of a specific remote",
                inputSchema=GitGetRemoteUrl.schema(),
            ),
            Tool(
                name=GitTools.LIST_REMOTES,
                description="Lists all configured remotes",
                inputSchema=GitListRemotes.schema(),
            ),
            Tool(
                name=GitTools.ADD_REMOTE,
                description="Adds a new remote",
                inputSchema=GitAddRemote.schema(),
            ),
            Tool(
                name=GitTools.REMOVE_REMOTE,
                description="Removes a remote",
                inputSchema=GitRemoveRemote.schema(),
            ),
            Tool(
                name=GitTools.LIST_BRANCHES,
                description="Lists all branches",
                inputSchema=GitListBranches.schema(),
            ),
            Tool(
                name=GitTools.DELETE_BRANCH,
                description="Deletes a branch",
                inputSchema=GitDeleteBranch.schema(),
            ),
            Tool(
                name=GitTools.RENAME_BRANCH,
                description="Renames a branch",
                inputSchema=GitRenameBranch.schema(),
            ),
            Tool(
                name=GitTools.GET_CURRENT_BRANCH,
                description="Gets the name of the current branch",
                inputSchema=GitGetCurrentBranch.schema(),
            ),
        ]

    async def list_repos() -> Sequence[str]:
        async def by_roots() -> Sequence[str]:
            if not isinstance(server.request_context.session, ServerSession):
                raise TypeError("server.request_context.session must be a ServerSession")

            if not server.request_context.session.check_client_capability(
                ClientCapabilities(roots=RootsCapability())
            ):
                return []

            roots_result: ListRootsResult = await server.request_context.session.list_roots()
            logger.debug(f"Roots result: {roots_result}")
            repo_paths = []
            for root in roots_result.roots:
                path = root.uri.path
                try:
                    git.Repo(path)
                    repo_paths.append(str(path))
                except git.InvalidGitRepositoryError:
                    pass
            return repo_paths

        def by_commandline() -> Sequence[str]:
            return [str(repository)] if repository is not None else []

        cmd_repos = by_commandline()
        root_repos = await by_roots()
        return [*root_repos, *cmd_repos]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        repo_path = Path(arguments["repo_path"])
        repo = git.Repo(repo_path)

        match name:
            case GitTools.STATUS:
                status = git_status(repo)
                return [TextContent(
                    type="text",
                    text=f"Repository status:\n{status}"
                )]

            case GitTools.DIFF_UNSTAGED:
                diff = git_diff_unstaged(repo)
                return [TextContent(
                    type="text",
                    text=f"Unstaged changes:\n{diff}"
                )]

            case GitTools.DIFF_STAGED:
                diff = git_diff_staged(repo)
                return [TextContent(
                    type="text",
                    text=f"Staged changes:\n{diff}"
                )]

            case GitTools.DIFF:
                diff = git_diff(repo, arguments["target"])
                return [TextContent(
                    type="text",
                    text=f"Diff with {arguments['target']}:\n{diff}"
                )]

            case GitTools.COMMIT:
                result = git_commit(repo, arguments["message"])
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.ADD:
                result = git_add(repo, arguments["files"])
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.RESET:
                result = git_reset(repo)
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.LOG:
                log = git_log(repo, arguments.get("max_count", 10))
                return [TextContent(
                    type="text",
                    text="Commit history:\n" + "\n".join(log)
                )]

            case GitTools.CREATE_BRANCH:
                result = git_create_branch(
                    repo,
                    arguments["branch_name"],
                    arguments.get("base_branch")
                )
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.CHECKOUT:
                result = git_checkout(repo, arguments["branch_name"])
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.PUSH:
                result = git_push(
                    repo,
                    arguments.get("remote", "origin"),
                    arguments.get("branch")
                )
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.PULL:
                result = git_pull(
                    repo,
                    arguments.get("remote", "origin"),
                    arguments.get("branch")
                )
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.FETCH:
                result = git_fetch(
                    repo,
                    arguments.get("remote", "origin"),
                    arguments.get("branch")
                )
                return [TextContent(
                    type="text",
                    text=result
                )]

            case GitTools.GET_CONFIG:
                config = git_get_config(repo)
                return [TextContent(
                    type="text",
                    text=f"Git config:\n{config}"
                )]

            case GitTools.GET_REMOTE_URL:
                url = git_get_remote_url(repo, arguments.get("remote", "origin"))
                return [TextContent(
                    type="text",
                    text=f"Remote URL: {url}"
                )]
            
            case GitTools.LIST_REMOTES:
                remotes = git_list_remotes(repo)
                return [TextContent(
                    type="text",
                    text="Configured remotes:\n" + 
                         "\n".join(f"{r['name']}: {', '.join(r['urls'])}" for r in remotes)
                )]
            
            case GitTools.ADD_REMOTE:
                result = git_add_remote(repo, arguments["name"], arguments["url"])
                return [TextContent(
                    type="text",
                    text=result
                )]
            
            case GitTools.REMOVE_REMOTE:
                result = git_remove_remote(repo, arguments["name"])
                return [TextContent(
                    type="text",
                    text=result
                )]
            
            case GitTools.LIST_BRANCHES:
                branches = git_list_branches(repo, arguments.get("remote", True))
                return [TextContent(
                    type="text",
                    text="Branches:\n" + "\n".join(
                        f"{'* ' if b['is_active'] else '  '}{b['name']} ({b['type']}) - {b['commit'][:8]}"
                        for b in branches
                    )
                )]
            
            case GitTools.DELETE_BRANCH:
                result = git_delete_branch(
                    repo, 
                    arguments["branch_name"],
                    arguments.get("force", False)
                )
                return [TextContent(
                    type="text",
                    text=result
                )]
            
            case GitTools.RENAME_BRANCH:
                result = git_rename_branch(
                    repo,
                    arguments["old_name"],
                    arguments["new_name"]
                )
                return [TextContent(
                    type="text",
                    text=result
                )]
            
            case GitTools.GET_CURRENT_BRANCH:
                branch = git_get_current_branch(repo)
                return [TextContent(
                    type="text",
                    text=f"Current branch: {branch}"
                )]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
