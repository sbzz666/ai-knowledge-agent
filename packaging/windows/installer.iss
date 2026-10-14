#define AppName "Knowledge Agent"
#define AppVersion "0.1.0"
#define AppExe "KnowledgeAgent.exe"

[Setup]
AppId={{0CC44652-1CD7-49A5-B1E5-61B6488AE241}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\Knowledge Agent
DefaultGroupName={#AppName}
OutputDir=..\..\release
OutputBaseFilename=Knowledge-Agent-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\..\dist\KnowledgeAgent\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标："

[Run]
Filename: "{app}\{#AppExe}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent
