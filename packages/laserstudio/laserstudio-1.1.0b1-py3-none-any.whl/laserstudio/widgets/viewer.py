from PyQt6.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QFileDialog,
    QGraphicsPixmapItem,
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColorConstants,
    QWheelEvent,
    QMouseEvent,
    QKeyEvent,
    QGuiApplication,
    QPainter,
    QPixmap,
    QPolygonF,
    QTransform,
    QPen,
    QColor,
)
from enum import Enum, auto
from typing import Optional, Union

from shapely import Polygon

from laserstudio.utils.colors import LedgerColors
from .stagesight import (
    StageSight,
    StageInstrument,
    CameraInstrument,
    ProbeInstrument,
    LaserInstrument,
)
import logging
from .scangeometry import ScanGeometry
import numpy as np
from ..instruments.stage import MoveFor
from .marker import IdMarker, Marker
from ..utils.util import yaml_to_qtransform, qtransform_to_yaml


class Viewer(QGraphicsView):
    """
    Widget to display circuit photos, navigate and control position, display the
    results...
    """

    class Mode(int, Enum):
        """Viewer modes."""

        NONE = auto()
        STAGE = auto()
        ZONE = auto()
        ZONE_TILTED = auto()
        ZONE_POLY = auto()
        PIN = auto()

    # Signal emitted when a new mode is set
    mode_changed = pyqtSignal(int)
    # Signal emitted when the mouse has moved in scene
    mouse_moved = pyqtSignal(float, float)
    # Signal emitted when the follow stage sight option changed
    follow_stage_sight_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # # Align objects to the center
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        # The main scene of the graphic view
        self.__scene = QGraphicsScene()
        self.setScene(self.__scene)

        # Cross cursor
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Make background black
        self.setBackgroundBrush(QBrush(QColorConstants.Black))

        # Selection of mode
        self.__mode = Viewer.Mode.NONE

        # Hide ScrollBars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Enable anti-aliasing
        self.setRenderHints(QPainter.RenderHint.Antialiasing)

        # Current camera position and zoom factor
        # self.__cam_pos_zoom = QPointF(), 1.0
        self.scale(1, -1)

        # By default, there is no StageSight
        self.stage_sight: Optional[StageSight] = None
        self._follow_stage_sight = False

        # Scanning geometry object and its representative item in the view.
        # Also includes the scan path
        self.scan_geometry = ScanGeometry()
        self.__scene.addItem(self.scan_geometry)
        self.scan_geometry.setZValue(3)

        # Permits to activate tools
        self.setInteractive(True)

        # Augment the scene rect to a very big size.
        self.setSceneRect(-1e6, -1e6, 2e6, 2e6)

        # Background picture
        self.__picture_item = None
        self.background_picture_path = None

        # Pin points for background picture
        self.pins = []
        # PIN Markers
        self.pin_markers = [
            Marker(color=LedgerColors.SerenityPurple.value),
            Marker(color=LedgerColors.SerenityPurple.value),
            Marker(color=LedgerColors.SerenityPurple.value),
        ]
        for m in self.pin_markers:
            m.setZValue(4)
            self.__scene.addItem(m)
            m.hide()

        # Markers
        self.__markers: list[Marker] = []
        self.default_marker_size = 30.0

        # To prevent warning, due to QTBUG-103935 (https://bugreports.qt.io/browse/QTBUG-103935)
        if (vp := self.viewport()) is not None:
            vp.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        # Polygon for zone creation
        self.zone_poly = QPolygonF()
        self.zone_poly_item = QGraphicsPolygonItem(self.zone_poly)
        self.zone_poly_item.setZValue(2)
        self.__scene.addItem(self.zone_poly_item)

        self.setMouseTracking(True)

    @property
    def markers(self) -> list[Marker]:
        return self.__markers

    def marker_size(self, value: float):
        self.default_marker_size = value
        for m in self.__markers:
            m.size = value

    @property
    def follow_stage_sight(self) -> bool:
        return self._follow_stage_sight

    @follow_stage_sight.setter
    def follow_stage_sight(self, value: bool):
        """Triggers an update of the camera position when the stage sight change its own position."""
        if self.stage_sight is None:
            return

        # We force to disconnect, in all cases (if already connected).
        if self._follow_stage_sight:
            self.stage_sight.position_changed.disconnect()

        if value:
            self.stage_sight.position_changed.connect(
                lambda _: self.__setattr__(
                    "cam_pos_zoom",
                    (self.focused_element_position(), self.zoom),
                )
            )
            self.stage_sight.update_pos()

        # Emit the signal if necessary
        if self._follow_stage_sight != value:
            self._follow_stage_sight = value
            self.follow_stage_sight_changed.emit(value)

    def reset_camera(self, item: Optional[QGraphicsPixmapItem] = None):
        """Resets the camera to show all elements of the scene"""
        if item is not None:
            all_elements_rect = item.sceneTransform().mapRect(item.boundingRect())
        else:
            all_elements_rect = self.__scene.itemsBoundingRect()
        viewport = self.viewport()
        viewport_size = (
            viewport.size() if viewport is not None else all_elements_rect.size()
        )
        w_ratio = viewport_size.width() / (all_elements_rect.width() * 1.2)
        h_ratio = viewport_size.height() / (all_elements_rect.height() * 1.2)
        self.cam_pos_zoom = (
            all_elements_rect.center(),
            min(w_ratio, h_ratio),
        )

    def reset_camera_to_stage_sight(self):
        """Resets the camera to show the stage sight"""
        if self.stage_sight is None:
            return
        self.reset_camera(self.stage_sight.image)

    def __place_picture_item(self, at_stage_sight: bool = False):
        item = self.__picture_item
        if item is None:
            return
        # Put if far far away in the back
        item.setZValue(-10)
        if not at_stage_sight or self.stage_sight is None:
            # We place the image at current viewing position
            transform = QTransform()
            pos = (
                self.stage_sight.pos()
                if self.stage_sight is not None and at_stage_sight
                else self.cam_pos_zoom[0]
            )
            transform.translate(pos.x(), pos.y())
            # Scene Y-axis is up, while for images it shall be down. We flip the
            # image over the Y-axis to show it in the right orientation.
            transform.scale(1, -1)
            transform.translate(
                -item.boundingRect().width() / 2, -item.boundingRect().height() / 2
            )
        else:
            # We place the image at current stagesight' position
            transform = self.stage_sight.image.sceneTransform()

        item.setTransform(transform)
        self.__scene.addItem(item)

    def __set_picture_item(self, item: QGraphicsPixmapItem):
        item = self.__picture_item = QGraphicsPixmapItem(item.pixmap())

    def snap_picture_from_camera(self):
        """Takes the current picture from the current
        and set it as background picture"""
        if self.stage_sight is None:
            return
        self.clear_picture()
        self.__set_picture_item(self.stage_sight.image)
        self.__place_picture_item(at_stage_sight=True)

    def clear_picture(self):
        """Clears the background picture"""
        if self.__picture_item is not None:
            self.__scene.removeItem(self.__picture_item)
            self.__picture_item = None
            self.background_picture_path = None

    def load_picture(self, picture_path: Optional[str] = None):
        """Requests loading a backgound picture from the user"""
        filename = (
            # Make the file dialog visible and on top
            QFileDialog.getOpenFileName(
                self,
                "Open picture",
                "",
                "Images (*.png *.jpg *.jpeg)",
                options=QFileDialog.Option.DontUseNativeDialog,
            )[0]
            if picture_path is None
            else picture_path
        )
        if len(filename):
            # Remove previous picture if defined
            self.clear_picture()
            # Get the picture and set it as background
            item = QGraphicsPixmapItem(QPixmap(filename))
            self.__set_picture_item(item)
            self.__place_picture_item()
            # Save picture path for when transform is saved.
            self.background_picture_path = filename

    def add_stage_sight(
        self,
        stage: Optional[StageInstrument],
        camera: Optional[CameraInstrument],
        probes: list[ProbeInstrument] = [],
    ):
        """Instantiate a stage sight associated with given stage.

        :param stage: The stage instrument to be associated with the stage sight
        """
        # Add StageSight item
        self.stage_sight = StageSight(stage, camera, probes)
        self.stage_sight.setZValue(1)
        self.__scene.addItem(self.stage_sight)

    @property
    def mode(self) -> Mode:
        """Mode property to indicate in which mode the Viewer is.

        :return: Current selected mode."""
        return self.__mode

    @mode.setter
    def mode(self, new_mode: Mode):
        self.__mode = new_mode
        self.__update_drag_mode()
        self.__update_selection_color()
        logging.getLogger("laserstudio").debug(f"Viewer mode selection: {new_mode}")
        self.mode_changed.emit(int(new_mode))

    def select_mode(self, mode: Union[Mode, int], toggle: bool = False):
        """Selects the Viewer's mode. If toogle is set to true,
        the function behaves as 'toggling',
        meaning that the mode is reset to NONE if it is reselected."""
        if isinstance(mode, int):
            mode = Viewer.Mode(mode)

        if toggle and self.mode == mode:
            mode = Viewer.Mode.NONE

        self.zone_poly.clear()
        self.zone_poly_item.setPolygon(self.zone_poly)

        self.mode = mode

    def go_next(self):
        """Actions to perform when Laser Studio receive a Go Next command.
        Retrieve the next point position from Scan Geometry
        Inform the StageSight to go to the retrieved position
        """
        result = {}
        if self.scan_geometry:
            next_point = self.scan_geometry.next_point()
            if next_point is not None and self.stage_sight is not None:
                result = {"next_point_geometry": next_point}
                next_point = self.point_for_desired_move(next_point)
                result["next_point_applied"] = next_point
                self.stage_sight.move_to(QPointF(*next_point))
        return result

    def __update_selection_color(
        self, has_shift: Optional[bool] = None, is_valid: bool = True
    ):
        """Convenience function to change the current Application Palette to modify
        the highlight color. It permits to the Zone creation tool to have green / red
        colors
        """
        if has_shift is None:
            has_shift = (
                Qt.KeyboardModifier.ShiftModifier
                in QGuiApplication.queryKeyboardModifiers()
            )
        color = ("red" if has_shift else "green") if is_valid else "orange"
        self.setStyleSheet(f"QGraphicsView {{ selection-background-color: {color}; }}")
        c = (
            (QColorConstants.Red if has_shift else QColorConstants.Green)
            if is_valid
            else QColorConstants.DarkYellow
        )
        pen = QPen(c)
        if isinstance(c, QColor):
            c.setAlpha(64)
        pen.setCosmetic(True)
        self.zone_poly_item.setPen(pen)
        self.zone_poly_item.setBrush(QBrush(c))

    def __update_drag_mode(self):
        if self.mode == Viewer.Mode.ZONE:
            self.setDragMode(Viewer.DragMode.RubberBandDrag)
        else:
            self.setDragMode(Viewer.DragMode.NoDrag)

    @property
    def cam_pos_zoom(self) -> tuple[QPointF, float]:
        """'Camera' position and zoom of the Viewer: The first element is
        the position in the stage where the viewer is centered on.
        The second element is the zoom factor, which must be strictly positive.

        :return: A tuple containing the point where the viewer is centered
            on and a float indicating the zoom factor.
        """
        return self.__compute_pos_zoom()

    @cam_pos_zoom.setter
    def cam_pos_zoom(self, new_value: tuple[QPointF, float]):
        assert new_value[1] > 0
        self.resetTransform()
        self.scale(new_value[1], -new_value[1])
        self.centerOn(new_value[0])

    @property
    def zoom(self) -> float:
        """Zoom factor of the viewer"""
        return self.cam_pos_zoom[1]

    @zoom.setter
    def zoom(self, factor: float):
        """Change the zoom by applying the zoom factor given in parameter

        :param factor: the zoom factor given in parameter.
        """
        self.cam_pos_zoom = self.cam_pos_zoom[0], factor

    @zoom.deleter
    def zoom(self):
        """Resets the zoom"""
        self.zoom = 1.0

    # User interactions
    def wheelEvent(self, event: Optional[QWheelEvent]):
        """
        Handle mouse wheel events to manage zoom.
        """
        if event is None:
            return
        # Get current position and zoom factor of camera
        pos, zoom = self.cam_pos_zoom
        # The zoom factor to apply
        zr = 2 ** (event.angleDelta().y() / (8 * 120))

        if not self._follow_stage_sight:
            # We want to zoom relative to the current cursor position, not relative
            # to the center of the widget. This involves some math...
            # p is the pointed position in the scene, and we want to keep p at the
            # same screen position after changing the zoom. If c1 and c2 are the
            # camera positions before and after the zoom changes,
            # z1 and z2 the zoom levels, then we want:
            # z1 * (p - c1) = z2 * (p - c2)
            # which gives:
            # c2 = c1 * (z1/z2) + p * (1 - z1/z2)
            # we can use zr = z2/z1, the zoom factor to apply.

            # The pointed position
            p = self.mapToScene(event.position().toPoint())
            pos = (pos / zr) + (p * (1 - (1 / zr)))

        zoom *= zr

        # Update the position and zoom factors
        self.cam_pos_zoom = pos, zoom
        event.accept()

    def mousePressEvent(self, event: Optional[QMouseEvent]):
        """
        Called when mouse button is pressed.
        In case of Mode being STAGE, triggers a move of the stage's StageSight.
        In case of Mode being PIN, triggers a pin of the background picture.
        In case of Mode being ZONE_POLY, triggers a polygon shaped zone creation.
        In case of Mode being ZONE_TILTED, triggers a tilted rectangle shaped zone creation.
        """
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            # Map the mouse position to the scene position
            scene_pos = self.mapToScene(event.pos())

            if self.mode == Viewer.Mode.STAGE and self.stage_sight is not None:
                scene_pos = self.point_for_desired_move((scene_pos.x(), scene_pos.y()))
                self.stage_sight.move_to(QPointF(*scene_pos))
                event.accept()
                return

            if self.mode == Viewer.Mode.PIN:
                self.pin(scene_pos.x(), scene_pos.y())

            elif self.mode == Viewer.Mode.ZONE_TILTED:
                self.zone_poly.append(scene_pos)
                if self.zone_poly.count() == 3:
                    fourth_point = scene_pos - (self.zone_poly[1] - self.zone_poly[0])
                    self.zone_poly.append(fourth_point)
                    if self.is_valid_zone:
                        modifiers = QGuiApplication.queryKeyboardModifiers()
                        if Qt.KeyboardModifier.ShiftModifier in modifiers:
                            self.scan_geometry.remove(self.zone_poly)
                        else:
                            self.scan_geometry.add(self.zone_poly)
                        self.zone_poly.clear()
                        self.zone_poly_item.setPolygon(self.zone_poly)
                    else:
                        self.zone_poly.remove(self.zone_poly.count() - 1)

            elif self.mode == Viewer.Mode.ZONE_POLY:
                self.zone_poly.append(scene_pos)
                self.zone_poly_item.setPolygon(self.zone_poly)

        # The event is a press of the right button
        if event.button() == Qt.MouseButton.RightButton:
            # Disable the StageSight tracking
            self.follow_stage_sight = False

            # Scroll gesture mode
            self.setDragMode(Viewer.DragMode.ScrollHandDrag)
            # Transform as left press button event,
            # to make the scroll by dragging actually effective.
            event = QMouseEvent(
                event.type(),
                event.position(),
                Qt.MouseButton.LeftButton,
                event.buttons(),
                event.modifiers(),
                event.pointingDevice(),
            )

        super().mousePressEvent(event)

    @property
    def is_valid_zone(self) -> bool:
        """
        Check if the zone is valid.
        """
        if self.zone_poly.count() < 3:
            return False
        points = [(p.x(), p.y()) for p in self.zone_poly]
        shapely_poly = Polygon(points)
        return shapely_poly.is_valid

    def mouseMoveEvent(self, event: Optional[QMouseEvent]):
        """
        Called when mouse moves.
        """
        is_valid = True
        if event is not None:
            # Map the mouse position to the scene position
            scene_pos = self.mapToScene(event.pos())
            self.mouse_moved.emit(scene_pos.x(), scene_pos.y())

            if self.mode == Viewer.Mode.ZONE_POLY and not self.zone_poly.isEmpty():
                # Check if mouse button is pressed
                if Qt.MouseButton.LeftButton not in event.buttons():
                    self.zone_poly.remove(self.zone_poly.count() - 1)
                self.zone_poly.append(scene_pos)
                self.zone_poly_item.setPolygon(self.zone_poly)
                is_valid = self.is_valid_zone

            elif self.mode == Viewer.Mode.ZONE_TILTED:
                if (nb_pts := self.zone_poly.count()) == 1:
                    full_poly = QPolygonF(self.zone_poly)
                    full_poly.append(scene_pos)
                    self.zone_poly_item.setPolygon(full_poly)
                elif nb_pts == 2:
                    fourth_point = scene_pos - (self.zone_poly[1] - self.zone_poly[0])
                    full_poly = QPolygonF(self.zone_poly)
                    full_poly.append(scene_pos)
                    full_poly.append(fourth_point)
                    self.zone_poly_item.setPolygon(full_poly)

        if self.mode in [
            Viewer.Mode.ZONE,
            Viewer.Mode.ZONE_POLY,
            Viewer.Mode.ZONE_TILTED,
        ]:
            # In Zone Mode, a release of the Shift key makes the highlight
            # color to be changed to red (remove)
            self.__update_selection_color(is_valid=is_valid)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]):
        """
        Called when mouse button is released.
        Used to get out the panning, when Right button is released.
        Used to detect the end of the Zone selection.
        """
        if event is None:
            return
        is_left = event.button() == Qt.MouseButton.LeftButton
        is_right = event.button() == Qt.MouseButton.RightButton

        if is_right:
            # Go back to regular drag mode.
            self.__update_drag_mode()

        if self.mode == Viewer.Mode.ZONE and is_left:
            # Get the corresponding Polygon within the scene
            rect = self.rubberBandRect()
            zone = self.mapToScene(rect)
            # Add or remove the new rectangle to/from the current zone geometry
            modifiers = QGuiApplication.queryKeyboardModifiers()
            if Qt.KeyboardModifier.ShiftModifier in modifiers:
                # Remove the zone to all the polygons
                self.scan_geometry.remove(zone)
            else:
                self.scan_geometry.add(zone)

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == Viewer.Mode.ZONE_POLY:
                self.zone_poly.append(self.mapToScene(event.pos()))
                modifiers = QGuiApplication.queryKeyboardModifiers()
                if Qt.KeyboardModifier.ShiftModifier in modifiers:
                    self.scan_geometry.remove(self.zone_poly)
                else:
                    self.scan_geometry.add(self.zone_poly)
                self.zone_poly_item.setPolygon(QPolygonF())
                self.zone_poly.clear()

        return super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: Optional[QKeyEvent]):
        """
        Called when a keyboard button is pressed.
        """
        if self.mode == Viewer.Mode.ZONE_POLY or self.mode == Viewer.Mode.ZONE:
            self.__update_selection_color(is_valid=True)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: Optional[QKeyEvent]):
        """
        Called when a keyboard button is released.
        """
        if self.mode == Viewer.Mode.ZONE_POLY or self.mode == Viewer.Mode.ZONE:
            self.__update_selection_color(is_valid=True)
        super().keyReleaseEvent(event)

    def pin(self, x: float, y: float):
        """
        Called when the user clicks in the viewer, in PIN mode.

        :param x: New position abscissa.
        :param y: New position ordinate.
        """

        if (pic := self.__picture_item) is None:
            return
        if self.stage_sight is None:
            return
        if self.stage_sight.stage is None:
            stage_pos = self.stage_sight.pos()
        else:
            stage_pos = self.stage_sight.scene_coords_from_stage_coords(
                self.stage_sight.stage.position
            )
        stage_pos = stage_pos.x(), stage_pos.y()

        n = len(self.pins)
        if n == 0:
            # We are pinning the first point.
            # Apply simple translation as first step
            tx = stage_pos[0] - x
            ty = stage_pos[1] - y
            t = QTransform()
            t.translate(tx, ty)
            pic.setTransform(pic.sceneTransform() * t)
            x += tx
            y += ty
        # Now pin the point, after initial translation.
        # If we remove the translation code above, the algorithm will still
        # work.
        pix_pos = pic.sceneTransform().inverted()[0].map(x, y)

        # Show the marker
        self.pin_markers[n].setPos(x, y)
        for m in self.pin_markers[: n + 1]:
            m.show()
        for m in self.pin_markers[n + 1 :]:
            m.hide()

        self.pins.append((stage_pos, pix_pos))

        logging.getLogger("laserstudio").debug(f"Pins: {self.pins}")
        if len(self.pins) == 3:
            # Time to recalculate the picture transformation matrix!
            #
            # We have three sets of two points A and B where:
            # - A is a spatial position (from stage)
            # - B is the corresponding position in the picture (in pixels,
            #   picked by the user)
            # To each point we add a third coordinate, set to 1, which will
            # allow us to work with translations.
            #
            # We want to find the 3x3 matrix T such as:
            # T * B1 = A1
            # T * B2 = A2
            # T * B3 = A3
            #
            # Written differently, this gives:
            # T * [B1, B2, B3] = [A1, A2, A3]
            #
            # Thus we have:
            # T = [A1, A2, A3] * Inv([B1, B2, B3])
            points_a = list(p[0] + (1,) for p in self.pins)
            points_b = list(p[1] + (1,) for p in self.pins)
            mat_a = np.matrix(points_a).transpose()
            mat_b = np.matrix(points_b).transpose()
            mat = mat_a * np.linalg.inv(mat_b)
            # Convert to QTransform
            # QTransform uses m31, m32 and m33 for translation, and not
            # m13, m23 and m33. Using the transposed version of mat seems
            # to fix the compatibility.
            qtrans = QTransform(*mat.flatten().tolist()[0]).transposed()
            pic.resetTransform()
            pic.setTransform(qtrans)
            # Clear pin points for future pinning, and leave pin mode.
            self.pins.clear()
            self.mode = self.Mode.NONE
        else:
            # Go to stage mode.
            self.mode = self.Mode.STAGE

    def __compute_pos_zoom(self):
        hsb, vsb = self.horizontalScrollBar(), self.verticalScrollBar()
        assert vsb and hsb
        # Get scene positioning in the Viewport thanks to the scrollbars' value
        doc_left = hsb.minimum()
        doc_width = hsb.maximum() + hsb.pageStep() - doc_left
        doc_x = hsb.value() + hsb.pageStep() / 2
        doc_top = vsb.minimum()
        doc_height = vsb.maximum() + vsb.pageStep() - doc_top
        doc_y = vsb.value() + vsb.pageStep() / 2

        # Get scene sizing
        sr = self.sceneRect()

        # Get doc to scene scale factors (invert of zoom)
        scale_x, scale_y = sr.width() / doc_width, sr.height() / doc_height

        # Converts previous positioning
        scene_x = sr.left() + (doc_x - doc_left) * scale_x
        scene_y = sr.bottom() - (doc_y - doc_top) * scale_y

        return QPointF(scene_x, scene_y), 1 / scale_x

    def focused_element_position(self) -> QPointF:
        """
        Gives the focused element's position, indicated by
          self.instruments.stage.move_for.
        """
        stage_sight = self.stage_sight
        if stage_sight is None or stage_sight.stage is None:
            # This should not happen...
            return QPointF()

        pos = stage_sight.mapToScene(0.0, 0.0)
        if stage_sight.stage.move_for.type == MoveFor.Type.CAMERA_CENTER:
            # Camera's center is always placed at StageSigth's coordinates.
            return pos

        if stage_sight.stage.move_for.type == MoveFor.Type.PROBE:
            marker = stage_sight.marker(
                ProbeInstrument, stage_sight.stage.move_for.index
            )
        elif stage_sight.stage.move_for.type == MoveFor.Type.LASER:
            marker = stage_sight.marker(
                LaserInstrument, stage_sight.stage.move_for.index
            )
        else:
            # This should not happen...
            return pos

        if marker is None:
            # This should not happen...
            return pos

        probe_position = stage_sight.mapToScene(marker.pos())
        return probe_position

    def point_for_desired_move(
        self, point: Union[QPointF, tuple[float, float]]
    ) -> tuple[float, float]:
        """
        Gives the actual stage's destination according to desired element
          to point at given position, indicated by
          self.instruments.stage.move_for.

        :param point: the desired position.
        :return: the stage's position to apply
        """
        if isinstance(point, QPointF):
            point = point.x(), point.y()

        stage_sight = self.stage_sight
        if stage_sight is None or stage_sight.stage is None:
            # This should not happen...
            return point
        elif stage_sight.stage.move_for.type == MoveFor.Type.CAMERA_CENTER:
            # Camera's center is always placed at Stage's coordinates.
            return point

        # Save camera positioning and zoom
        old_cam_pos_zoom = self.cam_pos_zoom

        # Force a refresh of main stage position (that may change viewer's position)
        stage_position = stage_sight.stage.position.xy.data

        # Get focused element scene's position
        probe_position = self.focused_element_position()

        # Restore the camera position and zoom
        self.cam_pos_zoom = old_cam_pos_zoom

        return (
            point[0] + stage_position[0] - probe_position.x(),
            point[1] + stage_position[1] - probe_position.y(),
        )

    def add_marker(
        self, position: Optional[tuple[float, float]] = None, color=QColorConstants.Red
    ) -> IdMarker:
        """
        Add a marker at a specific position, or at current observed position
        """
        marker = IdMarker(color=color)
        self.__markers.append(marker)
        self.__scene.addItem(marker)
        if position is None:
            p = self.focused_element_position()
            position = p.x(), p.y()
        marker.setPos(*position)
        marker.setZValue(2)
        marker.size = self.default_marker_size
        marker.update_tooltip()
        return marker

    def clear_markers(self):
        """Removes all markers."""
        for marker in self.__markers:
            self.__scene.removeItem(marker)
        self.__markers.clear()

    @property
    def settings(self) -> dict:
        """Export settings to a dict for yaml serialization."""
        data = {}
        data["marker_size"] = self.default_marker_size

        if self.background_picture_path is not None:
            data["background_picture_path"] = self.background_picture_path
        if (pic := self.__picture_item) is not None:
            data["background_picture_transform"] = qtransform_to_yaml(pic.transform())
            data["background_picture_transform_pins"] = [
                [m.pos().x(), m.pos().y()] for m in self.pin_markers
            ]
        return data

    @settings.setter
    def settings(self, data: dict):
        """Import settings from a dict."""
        if (marker_size := data.get("marker_size")) is not None:
            self.marker_size(marker_size)
        if (path := data.get("background_picture_path")) is not None:
            self.load_picture(path)
            if (transform := data.get("background_picture_transform")) is not None and (
                pic := self.__picture_item
            ) is not None:
                pic.setTransform(yaml_to_qtransform(transform))
            if (pins := data.get("background_picture_transform_pins")) is not None:
                for i, pin in enumerate(pins):
                    self.pin_markers[i].setPos(pin[0], pin[1])
                    self.pin_markers[i].show()
