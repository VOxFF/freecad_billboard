"""Billboard Commands - GUI commands for creating billboards."""

import os
import FreeCAD
import FreeCADGui


def get_icon_path(icon_name="Billboard.svg"):
    """Get the path to an icon."""
    for base in [FreeCAD.getUserAppDataDir(), FreeCAD.getResourceDir()]:
        icon_path = os.path.join(base, "Mod", "Billboard", "Resources", "icons", icon_name)
        if os.path.exists(icon_path):
            return icon_path
    return ""


class CreateTextBillboard:
    """Command to create a new text billboard."""

    def GetResources(self):
        """Return command resources (icon, menu text, tooltip)."""
        return {
            "Pixmap": get_icon_path("AddBillboard.svg"),
            "MenuText": "Create Text Billboard",
            "ToolTip": "Create a text billboard that always faces the camera",
        }

    def Activated(self):
        """Called when the command is activated."""
        import BillboardObject
        BillboardObject.create("TextBillboard")

    def IsActive(self):
        """Return True if there is an active document."""
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("CreateTextBillboard", CreateTextBillboard())
