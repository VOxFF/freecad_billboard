"""Billboard Object - FeaturePython data model for text billboards."""

import FreeCAD


class TextBillboard:
    """A text billboard that always faces the camera."""

    def __init__(self, obj):
        """Initialize the billboard object with properties."""
        obj.Proxy = self
        self.Type = "TextBillboard"

        # Position in 3D space
        obj.addProperty(
            "App::PropertyPlacement", "Placement", "Base",
            "Position and orientation of the billboard"
        )

        # Text content
        obj.addProperty(
            "App::PropertyString", "Text", "Billboard",
            "The text to display"
        ).Text = "Billboard"

        # Font settings
        obj.addProperty(
            "App::PropertyFloat", "FontSize", "Font",
            "Font size in points"
        ).FontSize = 24.0

        obj.addProperty(
            "App::PropertyString", "FontName", "Font",
            "Font family name"
        ).FontName = "Arial"

        obj.addProperty(
            "App::PropertyColor", "TextColor", "Font",
            "Text color"
        ).TextColor = (1.0, 1.0, 1.0, 0.0)  # White

        obj.addProperty(
            "App::PropertyEnumeration", "Alignment", "Font",
            "Text alignment"
        )
        obj.Alignment = ["LEFT", "CENTER", "RIGHT"]
        obj.Alignment = "CENTER"

        # Background settings
        obj.addProperty(
            "App::PropertyBool", "ShowBackground", "Background",
            "Show background behind text"
        ).ShowBackground = False

        obj.addProperty(
            "App::PropertyColor", "BackgroundColor", "Background",
            "Background color"
        ).BackgroundColor = (0.2, 0.2, 0.2, 0.0)  # Dark gray

        obj.addProperty(
            "App::PropertyFloat", "BackgroundPadding", "Background",
            "Padding around text in pixels"
        ).BackgroundPadding = 5.0

        # Frame settings
        obj.addProperty(
            "App::PropertyBool", "ShowFrame", "Frame",
            "Show frame outline around text"
        ).ShowFrame = False

        obj.addProperty(
            "App::PropertyColor", "FrameColor", "Frame",
            "Frame line color"
        ).FrameColor = (1.0, 1.0, 1.0, 0.0)  # White

        obj.addProperty(
            "App::PropertyFloat", "FrameWidth", "Frame",
            "Frame line width in pixels"
        ).FrameWidth = 1.0

    def execute(self, obj):
        """Called when the object needs to be recomputed."""
        pass

    def onChanged(self, obj, prop):
        """Called when a property changes."""
        pass

    def dumps(self):
        """Serialize for saving."""
        return {"Type": self.Type}

    def loads(self, state):
        """Deserialize when loading."""
        if state:
            self.Type = state.get("Type", "TextBillboard")


def create(name: str = "TextBillboard") -> "FreeCAD.DocumentObject":
    """Create a new TextBillboard object in the active document."""
    if FreeCAD.ActiveDocument is None:
        FreeCAD.Console.PrintError("No active document\n")
        return None

    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    TextBillboard(obj)

    # Add view provider if GUI is available
    if FreeCAD.GuiUp:
        import BillboardViewProvider
        BillboardViewProvider.ViewProviderTextBillboard(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()
    return obj
