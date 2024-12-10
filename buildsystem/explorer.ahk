#SingleInstance, Force
#NoTrayIcon
#Include <AuxLib>

    AuxLibLoad()

    SetRegView 64
    RegRead, DeveloperDir, HKCU\Software\Developer, DeveloperDir
    ProjectDir := GetProjectDir()
    global BrowserPath

    if (A_Args.Length() > 0) {
        label := A_Args[1]
        if IsLabel(label) {
            Gosub %label%
        }
        ExitApp
    }

    ; Project Menu
    AddMenuItemEditor("ProjectMenu")
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&README.md...`tR", "OnReadme", BrowserPath )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&GitHub Server...`tG", "OnGitHubServer", ResDir "github.ico" )
    AddMenu( "ProjectMenu", "RE&ADME.md...`tA", "OnGitHubReadme", BrowserPath )
    AddMenu( "ProjectMenu" )
    AddMenu( "ProjectMenu", "&Sync with Upstream`tS", "OnSyncWithUpstream", ConEmuPath )
    AddMenu( "ProjectMenu" )
    AddMenuItemEditProjectMenu("ProjectMenu")
    ShowMenu( "ProjectMenu" )
    ExitApp
return ; end of script's auto-execute section

MenuHandler:
    MsgBox % "MenuHandler was called."
return

OnSyncWithUpstream:
    ProjectDir := GetProjectDir()
    SyncWithUpstream(ProjectDir, "https://github.com/modelcontextprotocol/servers.git")
return

OnGitHubServer:
    Subcommand := GetKeyState("Shift","P") ? "chat" : "code"
    ProjectDir := GetProjectDir()
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
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
    RunBat( Options, StripBat(BatchScript) )
return

OnGitHubReadme:
    SplitPath, A_LineFile,, GitRootDir
    SplitPath, GitRootDir,, GitRootDir
    Try Run chrome.exe "%GitRootDir%\src\github\README.md",, Max
return
