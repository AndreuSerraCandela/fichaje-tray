#define MyAppName "FichajeTray"
#define MyAppVersion "1.2.2"
#define MyAppPublisher "Malla"
#define MyAppExeName "FichajeTray.exe"

[Setup]
AppId={{CF1F9E88-7C5C-4A2E-9F9E-7E9F1B8D1A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename={#MyAppName}_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
DisableDirPage=no
DisableProgramGroupPage=yes
; Configuraciones para manejar mejor el cierre de aplicaciones
CloseApplications=no
CloseApplicationsFilter=FichajeTray.exe,FichajeTray.dll
RestartApplications=no
; Evitar problemas de permisos
PrivilegesRequired=admin
; Configuración de reinicio
RestartIfNeededByRun=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Función para verificar si FichajeTray está ejecutándose
function IsFichajeTrayRunning: Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('tasklist', '/FI "IMAGENAME eq FichajeTray.exe" /FO CSV', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := True;
  end;
end;

// Función para cerrar FichajeTray
function CloseFichajeTray: Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('taskkill', '/F /IM FichajeTray.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := True;
  end;
end;

// Función que se ejecuta antes de la instalación
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    // Verificar si FichajeTray está ejecutándose
    if IsFichajeTrayRunning then
    begin
      if MsgBox('Se detectó que FichajeTray está ejecutándose. ¿Desea cerrarlo automáticamente antes de continuar con la instalación?' + #13#10 + #13#10 + 
                'Esto evitará errores durante la instalación y se reiniciará automáticamente al finalizar.', mbConfirmation, MB_YESNO) = IDYES then
      begin
        // Cerrar FichajeTray de forma forzada
        if CloseFichajeTray then
        begin
          // Esperar un momento para que se cierre completamente
          Sleep(2000);
          MsgBox('FichajeTray ha sido cerrado exitosamente. Continuando con la instalación...', mbInformation, MB_OK);
        end
        else
        begin
          MsgBox('No se pudo cerrar FichajeTray automáticamente. Por favor, ciérrelo manualmente y continúe con la instalación.', mbError, MB_OK);
          Abort; // Detener la instalación
        end;
      end
      else
      begin
        MsgBox('Debe cerrar FichajeTray manualmente antes de continuar con la instalación.', mbError, MB_OK);
        Abort; // Detener la instalación
      end;
    end;
  end
  else if CurStep = ssPostInstall then
  begin
    // Función para ejecutar después de la instalación
    MsgBox('La instalación se ha completado exitosamente.' + #13#10 + #13#10 + 
           'FichajeTray se reiniciará automáticamente en unos segundos...', mbInformation, MB_OK);
    
    // Esperar un momento y luego ejecutar FichajeTray
    Sleep(3000);
    Exec('{app}\{#MyAppExeName}', '', '', SW_SHOW, ewNoWait, ResultCode);
  end;
end;