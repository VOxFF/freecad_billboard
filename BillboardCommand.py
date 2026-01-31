"""Billboard Commands - GUI commands for creating billboards."""

import FreeCAD
import FreeCADGui


class CreateTextBillboard:
    """Command to create a new text billboard."""

    def GetResources(self):
        """Return command resources (icon, menu text, tooltip)."""
        return {
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
