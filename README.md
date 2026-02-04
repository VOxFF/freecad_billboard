# FreeCAD Billboard Workbench

FreeCAD-Billboard is a simple workbench that lets you create text billboards that
always face the camera in FreeCAD's 3D view.

It is intended for annotation, labeling, and documentation workflows where you need
readable text overlays that remain visible from any viewing angle.

<img width="3767" height="1677" alt="image" src="https://github.com/user-attachments/assets/da37f240-cd5e-4a13-a9a0-5ed6d8f64f65" />

---

## Features

- Create **text billboards** that automatically face the camera
- Supports the following customization options:
  - **Font** settings (name, size, color, alignment)
  - **Background** box with transparency and padding
  - **Frame** outline with configurable width and color
- Properties editable in FreeCAD's standard Properties panel
- Billboards persist with document save/load

---

## Requirements

- **FreeCAD** 1.0+

---

## Installation

1. Find your FreeCAD user Mod directory

FreeCAD looks for workbenches and plugins under a user-specific Mod directory:

Linux
```bash
~/.FreeCAD/Mod
```
or
```bash
~/.local/share/FreeCAD/Mod
```

macOS
```bash
~/Library/Preferences/FreeCAD/Mod
```

Windows
```bash
%APPDATA%\FreeCAD\Mod
```

You can also check Edit → Preferences → General → Application → Paths in FreeCAD.

2. Copy / clone the workbench

Create a folder for the workbench inside Mod, for example:
```bash
~/.local/share/FreeCAD/Mod/Billboard/
```

Put your plugin files there:
```
Billboard/
  ├── Init.py
  ├── InitGui.py
  ├── BillboardObject.py
  ├── BillboardViewProvider.py
  ├── BillboardCommand.py
  └── README.md
```

If this repository is hosted on Git, you can clone directly:

```bash
cd ~/.local/share/FreeCAD/Mod
git clone https://github.com/<your-user>/freecad_billboard.git Billboard
```

Restart FreeCAD after installing the workbench.

---

## Usage

1. Open or create a document in FreeCAD.
2. Select **Billboard** from the workbench dropdown.
3. Click **Create Text Billboard** in the toolbar (or menu: Billboard → Create Text Billboard).
4. Edit properties in the Properties panel to customize the billboard.
5. Rotate the view — the text always faces the camera.

---

## Architecture

The workbench is organized into focused modules with clear responsibilities:

```
freecad_billboard/
├── __init__.py              # Package marker
├── Init.py                  # FreeCAD registration (non-GUI)
├── InitGui.py               # Workbench definition + toolbar
├── BillboardObject.py       # FeaturePython data model
├── BillboardViewProvider.py # Coin3D visualization
├── BillboardCommand.py      # GUI command to create billboards
└── Resources/
    └── icons/
        └── Billboard.svg    # Toolbar icon
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `BillboardObject.py` | Defines billboard properties (text, font, colors, etc.) |
| `BillboardViewProvider.py` | Renders billboard using Coin3D scene graph (SoText2) |
| `BillboardCommand.py` | Registers "Create Text Billboard" command |
| `InitGui.py` | Defines workbench, toolbar, and menu |

### Properties Reference

| Property | Group | Type | Description |
|----------|-------|------|-------------|
| Text | Billboard | String | The text to display |
| FontSize | Font | Float | Font size in points |
| FontName | Font | String | Font family name |
| TextColor | Font | Color | Text color |
| Alignment | Font | Enum | LEFT, CENTER, RIGHT |
| ShowBackground | Background | Bool | Show background box |
| BackgroundColor | Background | Color | Background fill color |
| BackgroundPadding | Background | Float | Padding around text (pixels) |
| ShowFrame | Frame | Bool | Show frame outline |
| FrameColor | Frame | Color | Frame line color |
| FrameWidth | Frame | Float | Frame line width (pixels) |

---

## License

LGPL-3.0
