"""Billboard ViewProvider - Coin3D visualization for text billboards."""

import FreeCADGui
from pivy import coin
import math


class ViewProviderTextBillboard:
    """ViewProvider for TextBillboard - handles 3D visualization."""

    def __init__(self, vobj):
        """Initialize the view provider."""
        vobj.Proxy = self
        self.ViewObject = vobj  # Store ViewObject reference
        self.camera_sensor = None

    def attach(self, vobj):
        """Called when the view provider is attached to the object."""
        print(f"ViewProvider attach called for {vobj.Object.Name}")
        self.ViewObject = vobj  # Store ViewObject, access .Object when needed
        print(f"  self.ViewObject set to: {self.ViewObject}")
        print(f"  self.ViewObject.Object: {self.ViewObject.Object}")
        print(f"  self id: {id(self)}")

        # Root separator for the billboard
        self.root = coin.SoSeparator()
        self.root.setName("BillboardRoot")

        # Parent node: Translation for positioning in world space
        self.translation = coin.SoTranslation()

        # Child node: Rotation matrix for billboard orientation
        self.rotation = coin.SoMatrixTransform()

        # Separator for rotated content (text, background, frame)
        self.billboard_content = coin.SoSeparator()

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

        # Text group - using SoText3 for 3D text
        self.text_sep = coin.SoSeparator()
        self.font = coin.SoFont()
        self.text_material = coin.SoMaterial()
        self.text = coin.SoText3()
        self.text.parts = coin.SoText3.FRONT  # Only render front face

        self.text_sep.addChild(self.font)
        self.text_sep.addChild(self.text_material)
        self.text_sep.addChild(self.text)

        # Build billboard content (all in local coordinates)
        self.billboard_content.addChild(self.background_switch)
        self.billboard_content.addChild(self.frame_switch)
        self.billboard_content.addChild(self.text_sep)

        # Build scene graph: root -> translation -> rotation -> content
        self.root.addChild(self.translation)
        self.root.addChild(self.rotation)
        self.root.addChild(self.billboard_content)

        # Add to the view
        vobj.addDisplayMode(self.root, "Standard")
        print("  Added display mode")

        # Initial update
        self._update_all(vobj.Object)
        print("  Updated all properties")

        # Set up camera sensor to update billboard orientation
        self._setup_camera_sensor()
        print("  Setup complete")

    def _setup_camera_sensor(self):
        """Set up a sensor to watch camera changes and update billboard orientation."""
        print("_setup_camera_sensor called")

        view = FreeCADGui.ActiveDocument.ActiveView
        if view is None:
            print("  No ActiveView")
            return

        camera = view.getCameraNode()
        if camera is None:
            print("  No camera node")
            return

        print(f"  Camera type: {type(camera)}")
        print(f"  Camera position: {camera.position.getValue().getValue()}")

        # Create a closure that captures self
        def make_callback(view_provider):
            def callback(sensor, data):
                print(f"Camera sensor callback fired")
                print(f"  view_provider.ViewObject = {view_provider.ViewObject}")
                if view_provider.ViewObject:
                    print(f"  view_provider.ViewObject.Object = {view_provider.ViewObject.Object}")
                view_provider._update_billboard_orientation()
            return callback

        self._sensor_callback = make_callback(self)
        print(f"  self id in _setup_camera_sensor: {id(self)}")
        print(f"  self.ViewObject at sensor setup: {self.ViewObject}")

        # Create sensor that triggers when camera position/orientation changes
        self.camera_sensor = coin.SoFieldSensor(self._sensor_callback, None)
        self.camera_sensor.attach(camera.position)
        print("  Attached position sensor")

        # Also watch orientation
        self.orientation_sensor = coin.SoFieldSensor(self._sensor_callback, None)
        self.orientation_sensor.attach(camera.orientation)
        print("  Attached orientation sensor")

        # Initial orientation update
        self._update_billboard_orientation()


    def _update_billboard_orientation(self):
        """Update billboard rotation matrix to face the camera."""
        print("_update_billboard_orientation called")

        if self.ViewObject is None:
            print("  ViewObject is None, returning")
            return

        obj = self.ViewObject.Object
        if obj is None:
            print("  Object is None, returning")
            return

        print(f"  obj type: {type(obj)}")
        print(f"  obj properties: {obj.PropertiesList if hasattr(obj, 'PropertiesList') else 'N/A'}")
        if not hasattr(obj, "Placement"):
            print("  No Placement property, returning")
            return
        print(f"  Placement: {obj.Placement}")

        view = FreeCADGui.ActiveDocument.ActiveView
        if view is None:
            print("  No ActiveView, returning")
            return

        camera = view.getCameraNode()
        if camera is None:
            print("  No camera, returning")
            return

        # Get camera orientation
        cam_orientation = camera.orientation.getValue()

        # Check if orthographic or perspective camera
        is_ortho = isinstance(camera, coin.SoOrthographicCamera)
        print(f"  Camera type: {'Orthographic' if is_ortho else 'Perspective'}")

        if is_ortho:
            # For orthographic camera, use camera view direction (negative Z in camera space)
            # Camera looks along -Z, so the "to camera" vector is +Z in camera space
            to_cam = cam_orientation.multVec(coin.SbVec3f(0, 0, 1))
            print(f"  Camera view direction (forward): {to_cam.getValue()}")
        else:
            # For perspective camera, use direction from billboard to camera
            pos = obj.Placement.Base
            billboard_pos = coin.SbVec3f(pos.x, pos.y, pos.z)
            cam_pos = camera.position.getValue()
            print(f"  Billboard pos: {billboard_pos.getValue()}")
            print(f"  Camera pos: {cam_pos.getValue()}")
            to_cam = cam_pos - billboard_pos
            to_cam.normalize()
            print(f"  To camera (forward): {to_cam.getValue()}")

        # Use world up for billboard (stays upright in world space)
        world_up = coin.SbVec3f(0, 1, 0)

        # Calculate billboard basis vectors
        # Forward = toward camera (Z axis of billboard)
        forward = to_cam

        # Right = cross(world_up, forward)
        right = world_up.cross(forward)
        length = right.length()
        print(f"  Right before normalize: {right.getValue()}, length: {length}")

        # Handle edge case: looking straight up or down
        if length < 0.001:
            cam_right = cam_orientation.multVec(coin.SbVec3f(1, 0, 0))
            right = cam_right
            print(f"  Using camera right (edge case)")
        else:
            right.normalize()

        print(f"  Right: {right.getValue()}")

        # Recalculate up to ensure orthogonality
        up = forward.cross(right)
        up.normalize()
        print(f"  Up: {up.getValue()}")

        # Build rotation matrix from basis vectors
        # Columns are: right (X), up (Y), forward (Z)
        # Use list-of-rows constructor for proper column-major handling
        matrix = coin.SbMatrix([
            [right[0], up[0], forward[0], 0.0],
            [right[1], up[1], forward[1], 0.0],
            [right[2], up[2], forward[2], 0.0],
            [0.0,      0.0,   0.0,        1.0],
        ])
        print(f"  Matrix: right={right.getValue()}, up={up.getValue()}, forward={forward.getValue()}")

        self.rotation.matrix.setValue(matrix)

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
                "LEFT": coin.SoText3.LEFT,
                "CENTER": coin.SoText3.CENTER,
                "RIGHT": coin.SoText3.RIGHT,
            }
            self.text.justification = alignment_map.get(
                obj.Alignment, coin.SoText3.CENTER
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
            self.text_material.diffuseColor.setValue(color[0], color[1], color[2])
            self.text_material.emissiveColor.setValue(color[0], color[1], color[2])

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
            self.background_material.transparency.setValue(0.3)

        # Estimate text bounds (approximate based on font size and text length)
        padding = getattr(obj, "BackgroundPadding", 5.0)
        font_size = getattr(obj, "FontSize", 24.0)
        text = getattr(obj, "Text", "")

        # Rough estimate: each character is about 0.6 * font_size wide
        char_width = font_size * 0.6
        text_width = len(text) * char_width
        text_height = font_size * 1.2

        # Calculate quad corners in local billboard coordinates (XY plane)
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

        # Set quad vertices in local XY plane (Z=-0.1 to be slightly behind text)
        self.background_coords.point.setValues(0, 4, [
            [left, bottom, -0.1],
            [right, bottom, -0.1],
            [right, top, -0.1],
            [left, top, -0.1],
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

        # Set line vertices in local XY plane (closed rectangle)
        self.frame_coords.point.setValues(0, 5, [
            [left, bottom, 0],
            [right, bottom, 0],
            [right, top, 0],
            [left, top, 0],
            [left, bottom, 0],
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
            self._update_billboard_orientation()

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

    def onDelete(self, vobj, subelements):
        """Called when the object is about to be deleted."""
        self._cleanup_sensors()
        return True

    def _cleanup_sensors(self):
        """Detach camera sensors."""
        if hasattr(self, 'camera_sensor') and self.camera_sensor:
            self.camera_sensor.detach()
            self.camera_sensor = None
        if hasattr(self, 'orientation_sensor') and self.orientation_sensor:
            self.orientation_sensor.detach()
            self.orientation_sensor = None

    def dumps(self):
        """Serialize for saving."""
        return None

    def loads(self, state):
        """Deserialize when loading."""
        # Re-setup camera sensor after loading
        if hasattr(self, 'root') and self.root:
            self._setup_camera_sensor()
        return None
