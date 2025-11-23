
[Setup]
AppName=学习工具箱
AppVersion=1.0
DefaultDirName={pf}\学习工具箱
DefaultGroupName=学习工具箱
UninstallDisplayIcon={app}\学习工具箱.exe
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\学习工具箱.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion; Check: not IsUpgrade
Source: "theme.json"; DestDir: "{app}"; Flags: ignoreversion; Check: not IsUpgrade

[Icons]
Name: "{group}\学习工具箱"; Filename: "{app}\学习工具箱.exe"
Name: "{group}\卸载学习工具箱"; Filename: "{uninstallexe}"
Name: "{commondesktop}\学习工具箱"; Filename: "{app}\学习工具箱.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Code]
var
  IsUpgrade: Boolean;

function InitializeSetup(): Boolean;
begin
  IsUpgrade := FileExists(ExpandConstant('{app}\学习工具箱.exe'));
  Result := True;
end;
