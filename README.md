# TP1 Algoritmos CG

Trabalho pratico de Computacao Grafica (Unidade 1): transformacoes 2D,
rasterizacao (DDA, Bresenham), recorte (Cohen-Sutherland, Liang-Barsky) e
preenchimento (Boundary-Fill, Flood-Fill, conectividade 4 e 8). Entrada
apenas por mouse/toque na area de desenho e na barra de ferramentas
lateral.

## Rodar a partir do codigo-fonte

```bash
pip install -r requirements.txt
python -m src.app
```

## Gerar o executavel e o instalador Windows

A forma recomendada e via GitHub Actions (roda em uma maquina Windows real
na nuvem, sem precisar de Windows local):

1. Configure um remote no GitHub e faca push da branch `main`.
2. Abra a aba "Actions" do repositorio e aguarde o workflow
   `build-windows` terminar.
3. Baixe os artefatos `TP1AlgoritmosCG-executable` (o `.exe` e as DLLs) e
   `TP1AlgoritmosCG-installer` (o instalador `TP1AlgoritmosCG-Setup.exe`).

Para gerar localmente em uma maquina Windows:

```powershell
pip install -r requirements.txt pyinstaller
cd build
pyinstaller --noconfirm tp1_algoritmos.spec
iscc installer.iss   # requer Inno Setup instalado
```
