[Setup]
AppName=TP1 Algoritmos CG
AppVersion=1.0
DefaultDirName={autopf}\TP1AlgoritmosCG
DefaultGroupName=TP1 Algoritmos CG
OutputDir=installer_output
OutputBaseFilename=TP1AlgoritmosCG-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\TP1AlgoritmosCG\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TP1 Algoritmos CG"; Filename: "{app}\TP1AlgoritmosCG.exe"
Name: "{autodesktop}\TP1 Algoritmos CG"; Filename: "{app}\TP1AlgoritmosCG.exe"
