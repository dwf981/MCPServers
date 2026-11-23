#Requires AutoHotkey v2.0
#SingleInstance Off
#Warn All, OutputDebug

#Include <Explorer>

ProjectMenu() {
    items := ProjectMenu_Editor(false)
    items.Push("-", ProjectMenu_Readme(), "-")
    items.Push({ text: "&Local Git...`tL", id: "OnLocalGit", run: OnLocalGit, icon: "github.ico" })
    items.Push({ text: "REA&DME.md...`tD", id: "OnLocalGitReadme", run: OnLocalGitReadme, icon: "@BrowserPath" })
    items.Push("-")
    items.Push({ text: "&GitHub Server...`tG", id: "OnGitHubServer", run: OnGitHubServer, icon: "github.ico" })
    items.Push({ text: "RE&ADME.md...`tA", id: "OnGitHubReadme", run: OnGitHubReadme, icon: "@BrowserPath" })
    items.Push("-")
    items.Push({ text: "Ge&nerate Claude Config...`tN", id: "OnGenerateClaudeConfig", run: OnGenerateClaudeConfig, icon: "@ComSpec" })
    items.Push("-")
    items.Push({ text: "&Sync with Upstream`tS", id: "OnSyncWithUpstream", run: OnSyncWithUpstream, icon: "@ConEmuPath" })
    items.Push("-")
    items.Push(ProjectMenu_EditMenu()*)
    return items
}

; This script lives in <repo>\buildsystem.
ScriptRepo() => RegExReplace(A_ScriptDir, "\\[^\\]+$")

OnSyncWithUpstream() => SyncWithUpstream(Explorer2_ProjectDir(), "https://github.com/modelcontextprotocol/servers.git")

; Writes %APPDATA%\Claude\claude_desktop_config.json for the git and github servers of this checkout (asks for the GitHub token when
; GITHUB_PERSONAL_ACCESS_TOKEN is not set). Shift deletes the existing file first.
OnGenerateClaudeConfig() {
    servers := StrReplace(ScriptRepo(), "\", "\\")
    Run_Bat({ Visible: "cmd", Pause: true, Admin: false, UseReadPassword: true, Colors: true, Vars: { Remove: Cli_Shift() ? "1" : "0", ServersPath: servers } }, "
(
set "DEST_JSON=!APPDATA!\Claude\claude_desktop_config.json"
if "!Remove!" equ "1" (
    echo Removing !yellow!!DEST_JSON!!nc! ...
    if exist "!DEST_JSON!" del "!DEST_JSON!"
    echo.
`)
if exist "!DEST_JSON!" (
    echo !yellow!!DEST_JSON!!nc! already exists.
    echo.
    type "!DEST_JSON!"
`) else (
    if not defined GITHUB_PERSONAL_ACCESS_TOKEN call :ReadPassword "Enter GITHUB_PERSONAL_ACCESS_TOKEN" GITHUB_PERSONAL_ACCESS_TOKEN
    if not defined GITHUB_PERSONAL_ACCESS_TOKEN goto :error
    set "TEMP_JSON=!TEMP!\config_!RANDOM!.json"
    (
    echo {
    echo   "mcpServers": {
    echo     "git": {
    echo       "command": "uv",
    echo       "args": ["--directory", "!ServersPath!\\src\\git", "run", "mcp-server-git"]
    echo     },
    echo     "github": {
    echo       "command": "node",
    echo       "args": ["!ServersPath!\\src\\github\\dist\\index.js"],
    echo       "env": {
    echo         "GITHUB_PERSONAL_ACCESS_TOKEN": "!GITHUB_PERSONAL_ACCESS_TOKEN!"
    echo       }
    echo     }
    echo   }
    echo }
    `) > "!TEMP_JSON!"
    jq "." "!TEMP_JSON!" > "!DEST_JSON!"
    del "!TEMP_JSON!"
    echo JSON file generated successfully as !yellow!!DEST_JSON!!nc!
`)
echo.
)")
}

; The MCP servers run in WSL, from the checkout under /home/ubuntu/MCPServers.
OnGitHubServer() => Run_Bash({ Visible: "ConEmu" }, "", "node /home/ubuntu/MCPServers/src/github/dist/index.js", true, true)

OnLocalGit() => Run_Bash({ Visible: "ConEmu" }, "", "source /home/ubuntu/MCPServers/src/git/.venv/bin/activate && echo Git MCP Server running && mcp-server-git -r /home/ubuntu/MCPServers", true, true)

OnGitHubReadme() => OpenServerReadme("github")

OnLocalGitReadme() => OpenServerReadme("git")

OpenServerReadme(server) {
    try Run('chrome.exe "' ScriptRepo() '\src\' server '\README.md"', , "Max")
}

Explorer2_Main(ProjectMenu)
