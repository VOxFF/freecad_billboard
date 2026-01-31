"""FreeCAD Billboard Workbench - GUI Initialization."""

import os
import FreeCAD
import FreeCADGui


class BillboardWorkbench(FreeCADGui.Workbench):
    """Billboard Workbench for creating text and image billboards."""

    MenuText = "Billboard"
    ToolTip = "Create text and image billboards that face the camera"

    @property
    def Icon(self):
        # Try to find icon in Mod directories
        for base in [FreeCAD.getUserAppDataDir(), FreeCAD.getResourceDir()]:
            icon_path = os.path.join(base, "Mod", "Billboard", "Resources", "icons", "Billboard.svg")
            if os.path.exists(icon_path):
                return icon_path
        return ""

    def Initialize(self):
        """Called when the workbench is first loaded."""
        import BillboardCommand  # noqa: F401 - registers commands

        self.appendToolbar("Billboard Tools", ["CreateTextBillboard"])
        self.appendMenu("Billboard", ["CreateTextBillboard"])

    def Activated(self):
        """Called when the workbench is activated."""
        pass

    def Deactivated(self):
        """Called when the workbench is deactivated."""
        pass

    def GetClassName(self):
        """Return the C++ class name."""
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(BillboardWorkbench())
