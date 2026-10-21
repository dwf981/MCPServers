#SingleInstance Off
#NoTrayIcon
#Include <AuxLib>

    AuxLibLoad()

    ScriptInit()
    {
        Global
    }
    ; Project Menu

    AddMenuItemEditor("ProjectMenu")
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&README.md...`tR", "OnReadme", BrowserPath )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&Local Git...`tL", "OnLocalGit", ResDir "github.ico" )
    AddMenu( "ProjectMenu", "REA&DME.md...`tD", "OnLocalGitReadme", BrowserPath )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&GitHub Server...`tG", "OnGitHubServer", ResDir "github.ico" )
    AddMenu( "ProjectMenu", "RE&ADME.md...`tA", "OnGitHubReadme", BrowserPath )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "Ge&nerate Claude Config...`tN", "OnGenerateClaudeConfig", ComSpec )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&Sync with Upstream`tS", "OnSyncWithUpstream", ConEmuPath )
    AddMenu( "ProjectMenu" )
    AddMenuItemEditProjectMenu( "ProjectMenu" )
    ShowMenu("ProjectMenu")
    ExitApp
return ; end of script's auto-execute section

MenuHandler:
    MsgBox % "MenuHandler was called."
return

OnSyncWithUpstream:
    ProjectDir := GetProjectDir(0, -1, true)
    SyncWithUpstream(ProjectDir, "https://github.com/modelcontextprotocol/servers.git")
return

OnGenerateClaudeConfig:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    ShiftPressed := GetKeyState("Shift","P")
    StringReplace, MCPServersPath, GitRootDir, \, \\, All
    BatchScript =
    (

        set "DEST_JSON=!APPDATA!\Claude\claude_desktop_config.json"
        if "%ShiftPressed%" equ "1" `(
            echo Removing !yellow!!DEST_JSON!!nc! ...
            if exist "!DEST_JSON!" del "!DEST_JSON!"
            echo.
        `)
        if exist "!DEST_JSON!" `(
            echo !yellow!!DEST_JSON!!nc! already exists.
            echo.
            type "!DEST_JSON!"
        `) else `(
            if not defined GITHUB_PERSONAL_ACCESS_TOKEN call :ReadPassword "Enter GITHUB_PERSONAL_ACCESS_TOKEN" GITHUB_PERSONAL_ACCESS_TOKEN
            if not defined GITHUB_PERSONAL_ACCESS_TOKEN goto :error
            set "TEMP_JSON=!TEMP!\config_!RANDOM!.json"
            `(
            echo {
            echo   "mcpServers": {
            echo     "git": {
            echo       "command": "uv",
            echo       "args": ["--directory", "%MCPServersPath%\\src\\git", "run", "mcp-server-git"]
            echo     },
            echo     "github": {
            echo       "command": "node",
            echo       "args": ["%MCPServersPath%\\src\\github\\dist\\index.js"],
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
    )
    Run_Bat({ Visible: "cmd", Pause: true, Admin: false, UseReadPassword: true, Colors: true }, StripBat(BatchScript))
return

OnGitHubServer:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    RunBash({ Visible: "ConEmu" }, "", "node /home/ubuntu/MCPServers/src/github/dist/index.js", "", 1, 1)
    return
    ShiftPressed := GetKeyState("Shift","P")
    BatchScript =
    (

        if "%ShiftPressed%" equ "1" `(
            echo Removing !yellow!node_modules!nc! and !yellow!dist!nc! ...
            if exist "%GitRootDir%\src\github\dist" rd /s /q "%GitRootDir%\src\github\dist"
            if exist "%GitRootDir%\src\github\node_modules" rd /s /q "%GitRootDir%\src\github\node_modules"
            echo.
        `)
        if not exist "%GitRootDir%\src\github\dist\index.js" `(
            echo Installing dependencies ...
            cd "%GitRootDir%\src\github" || goto :error
            call npm.cmd install || goto :error
            cd "%GitRootDir%\src\github" || goto :error
            call npm.cmd run build
            echo.
        `) 
        cd "%GitRootDir%\src\github" || goto :error
        echo Running !yellow!node dist\index.js!nc! in !green!%GitRootDir%\src\github!nc! ...
        echo.
        node dist\index.js
    )
    Options := { Visible: "ConEmu", Pause: true, Admin: true, Colors: true }
    Run_Bat( Options, StripBat(BatchScript) )
return

OnGitHubReadme:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    Try Run chrome.exe "%GitRootDir%\src\github\README.md",, Max
return

OnLocalGit:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    RunBash({ Visible: "ConEmu" }, "", "source /home/ubuntu/MCPServers/src/git/.venv/bin/activate && echo Git MCP Server running && mcp-server-git -r /home/ubuntu/MCPServers", "", 1, 1)
    return
    ShiftPressed := GetKeyState("Shift","P")
    BatchScript =
    (

        if "%ShiftPressed%" equ "1" `(
            echo Removing !yellow!.venv!nc! ...
            if exist "%GitRootDir%\src\git\.venv" rd /s /q "%GitRootDir%\src\git\.venv"
            echo.
        `)
        if not exist "%GitRootDir%\src\git\.venv\Scripts\activate.bat" `(
            echo Installing dependencies ...
            cd "%GitRootDir%\src\git" || goto :error
            uv venv || goto :error
            call .venv\Scripts\activate.bat || goto :error
            uv pip install -e . || goto :error
            call .venv\Scripts\deactivate.bat || goto :error
            echo.
        `) 
        cd "%GitRootDir%\src\git" || goto :error
        echo Running !yellow!mcp-server-git -r ..\..!nc! in !green!%GitRootDir%\src\git!nc! ...
        call .venv\Scripts\activate.bat || goto :error
        echo.
        mcp-server-git -r ..\..
    )
    Options := { Visible: "ConEmu", Pause: true, Admin: true, Colors: true }
    Run_Bat( Options, StripBat(BatchScript) )
return

OnLocalGitReadme:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    Try Run chrome.exe "%GitRootDir%\src\git\README.md",, Max
return
