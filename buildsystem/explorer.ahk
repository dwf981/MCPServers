#SingleInstance, Force
#NoTrayIcon
#Include <AuxLib>

    AuxLibLoad()

    SetRegView 64
    RegRead, DeveloperDir, HKCU\Software\Developer, DeveloperDir
    ProjectDir := GetProjectDir()

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
