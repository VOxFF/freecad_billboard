"""Billboard ViewProvider - Coin3D visualization for text billboards."""

import FreeCADGui
from pivy import coin


class ViewProviderTextBillboard:
    """ViewProvider for TextBillboard - handles 3D visualization."""

    def __init__(self, vobj):
        """Initialize the view provider."""
        vobj.Proxy = self
        self.Object = None

    def attach(self, vobj):
        """Called when the view provider is attached to the object."""
        self.Object = vobj.Object

        # Root separator for the billboard
        self.root = coin.SoSeparator()
        self.root.setName("BillboardRoot")

        # Translation node for positioning
        self.translation = coin.SoTranslation()

        # Background group (optional)
        self.background_switch = coin.SoSwitch()
        self.background_switch.whichChild = coin.SO_SWITCH_NONE

        self.background_sep = coin.SoSeparator()
        self.background_material = coin.SoMaterial()
        self.background_coords = coin.SoCoordinate3()
        self.background_face = coin.SoFaceSet()
        self.background_face.numVertices.setValue(4)

        self.background_sep.addChild(self.background_material)
        self.background_sep.addChild(self.background_coords)
        self.background_sep.addChild(self.background_face)
        self.background_switch.addChild(self.background_sep)

        # Frame group (optional)
        self.frame_switch = coin.SoSwitch()
        self.frame_switch.whichChild = coin.SO_SWITCH_NONE

        self.frame_sep = coin.SoSeparator()
        self.frame_color = coin.SoBaseColor()
        self.frame_style = coin.SoDrawStyle()
        self.frame_style.style = coin.SoDrawStyle.LINES
        self.frame_coords = coin.SoCoordinate3()
        self.frame_lines = coin.SoLineSet()
        self.frame_lines.numVertices.setValue(5)  # Closed rectangle

        self.frame_sep.addChild(self.frame_color)
        self.frame_sep.addChild(self.frame_style)
        self.frame_sep.addChild(self.frame_coords)
        self.frame_sep.addChild(self.frame_lines)
        self.frame_switch.addChild(self.frame_sep)

        # Text group
        self.text_sep = coin.SoSeparator()
        self.font = coin.SoFont()
        self.text_color = coin.SoBaseColor()
        self.text = coin.SoText2()

        self.text_sep.addChild(self.font)
        self.text_sep.addChild(self.text_color)
        self.text_sep.addChild(self.text)

        # Build scene graph
        self.root.addChild(self.translation)
        self.root.addChild(self.background_switch)
        self.root.addChild(self.frame_switch)
        self.root.addChild(self.text_sep)

        # Add to the view
        vobj.addDisplayMode(self.root, "Standard")

        # Initial update
        self._update_all(vobj.Object)

    def _update_all(self, obj):
        """Update all visual elements from object properties."""
        self._update_text(obj)
        self._update_font(obj)
        self._update_text_color(obj)
        self._update_background(obj)
        self._update_frame(obj)
        self._update_position(obj)

    def _update_text(self, obj):
        """Update the displayed text."""
        if hasattr(obj, "Text"):
            self.text.string.setValue(obj.Text)

        if hasattr(obj, "Alignment"):
            alignment_map = {
                "LEFT": coin.SoText2.LEFT,
                "CENTER": coin.SoText2.CENTER,
                "RIGHT": coin.SoText2.RIGHT,
            }
            self.text.justification = alignment_map.get(
                obj.Alignment, coin.SoText2.CENTER
            )

    def _update_font(self, obj):
        """Update font settings."""
        if hasattr(obj, "FontName"):
            self.font.name.setValue(obj.FontName)
        if hasattr(obj, "FontSize"):
            self.font.size.setValue(obj.FontSize)

    def _update_text_color(self, obj):
        """Update text color."""
        if hasattr(obj, "TextColor"):
            color = obj.TextColor
            self.text_color.rgb.setValue(color[0], color[1], color[2])

    def _update_background(self, obj):
        """Update background visibility and appearance."""
        if hasattr(obj, "ShowBackground"):
            if obj.ShowBackground:
                self.background_switch.whichChild = coin.SO_SWITCH_ALL
                self._update_background_geometry(obj)
            else:
                self.background_switch.whichChild = coin.SO_SWITCH_NONE

    def _update_background_geometry(self, obj):
        """Update background quad geometry based on text size."""
        if hasattr(obj, "BackgroundColor"):
            color = obj.BackgroundColor
            self.background_material.diffuseColor.setValue(
                color[0], color[1], color[2]
            )
            # Handle transparency if specified
            self.background_material.transparency.setValue(0.3)

        # Estimate text bounds (approximate based on font size and text length)
        padding = getattr(obj, "BackgroundPadding", 5.0)
        font_size = getattr(obj, "FontSize", 24.0)
        text = getattr(obj, "Text", "")

        # Rough estimate: each character is about 0.6 * font_size wide
        char_width = font_size * 0.6
        text_width = len(text) * char_width
        text_height = font_size * 1.2

        # Calculate quad corners (in screen-aligned coordinates)
        half_width = (text_width / 2) + padding
        bottom = -padding
        top = text_height + padding

        # Alignment offset
        alignment = getattr(obj, "Alignment", "CENTER")
        if alignment == "LEFT":
            left = -padding
            right = text_width + padding
        elif alignment == "RIGHT":
            left = -text_width - padding
            right = padding
        else:  # CENTER
            left = -half_width
            right = half_width

        # Set quad vertices (counter-clockwise)
        self.background_coords.point.setValues(0, 4, [
            [left, bottom, -0.1],   # Bottom-left (slightly behind text)
            [right, bottom, -0.1],  # Bottom-right
            [right, top, -0.1],     # Top-right
            [left, top, -0.1],      # Top-left
        ])

    def _update_frame(self, obj):
        """Update frame visibility and appearance."""
        if hasattr(obj, "ShowFrame"):
            if obj.ShowFrame:
                self.frame_switch.whichChild = coin.SO_SWITCH_ALL
                self._update_frame_geometry(obj)
            else:
                self.frame_switch.whichChild = coin.SO_SWITCH_NONE

    def _update_frame_geometry(self, obj):
        """Update frame line geometry."""
        if hasattr(obj, "FrameColor"):
            color = obj.FrameColor
            self.frame_color.rgb.setValue(color[0], color[1], color[2])

        if hasattr(obj, "FrameWidth"):
            self.frame_style.lineWidth.setValue(obj.FrameWidth)

        # Use same bounds calculation as background
        padding = getattr(obj, "BackgroundPadding", 5.0)
        font_size = getattr(obj, "FontSize", 24.0)
        text = getattr(obj, "Text", "")

        char_width = font_size * 0.6
        text_width = len(text) * char_width
        text_height = font_size * 1.2

        half_width = (text_width / 2) + padding
        bottom = -padding
        top = text_height + padding

        alignment = getattr(obj, "Alignment", "CENTER")
        if alignment == "LEFT":
            left = -padding
            right = text_width + padding
        elif alignment == "RIGHT":
            left = -text_width - padding
            right = padding
        else:  # CENTER
            left = -half_width
            right = half_width

        # Set line vertices (closed rectangle)
        self.frame_coords.point.setValues(0, 5, [
            [left, bottom, 0],
            [right, bottom, 0],
            [right, top, 0],
            [left, top, 0],
            [left, bottom, 0],  # Close the rectangle
        ])

    def _update_position(self, obj):
        """Update billboard position from object Placement."""
        if hasattr(obj, "Placement"):
            pos = obj.Placement.Base
            self.translation.translation.setValue(pos.x, pos.y, pos.z)

    def updateData(self, fp, prop):
        """Called when a data property of the object changes."""
        if prop == "Text":
            self._update_text(fp)
            if fp.ShowBackground:
                self._update_background_geometry(fp)
            if fp.ShowFrame:
                self._update_frame_geometry(fp)
        elif prop == "FontSize":
            self._update_font(fp)
            if fp.ShowBackground:
                self._update_background_geometry(fp)
            if fp.ShowFrame:
                self._update_frame_geometry(fp)
        elif prop == "FontName":
            self._update_font(fp)
        elif prop == "TextColor":
            self._update_text_color(fp)
        elif prop == "Alignment":
            self._update_text(fp)
            if fp.ShowBackground:
                self._update_background_geometry(fp)
            if fp.ShowFrame:
                self._update_frame_geometry(fp)
        elif prop == "ShowBackground":
            self._update_background(fp)
        elif prop in ("BackgroundColor", "BackgroundPadding"):
            if fp.ShowBackground:
                self._update_background_geometry(fp)
            if fp.ShowFrame:
                self._update_frame_geometry(fp)
        elif prop == "ShowFrame":
            self._update_frame(fp)
        elif prop in ("FrameColor", "FrameWidth"):
            if fp.ShowFrame:
                self._update_frame_geometry(fp)
        elif prop == "Placement":
            self._update_position(fp)

    def onChanged(self, vp, prop):
        """Called when a view property changes."""
        pass

    def getDisplayModes(self, vobj):
        """Return available display modes."""
        return ["Standard"]

    def getDefaultDisplayMode(self):
        """Return the default display mode."""
        return "Standard"

    def setDisplayMode(self, mode):
        """Set the display mode."""
        return mode

    def getIcon(self):
        """Return the icon for this object."""
        return ""

    def claimChildren(self):
        """Return child objects."""
        return []

    def dumps(self):
        """Serialize for saving."""
        return None

    def loads(self, state):
        """Deserialize when loading."""
        return None
