from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel
from superqt import QLabeledDoubleSlider

import finn
import finn.layers
from finn._qt.layer_controls.qt_image_controls_base import (
    QtBaseImageControls,
)
from finn._qt.layer_controls.qt_layer_clipping_plane_controls import QtLayerClippingPlanes
from finn._qt.utils import qt_signals_blocked
from finn.layers.image._image_constants import (
    ImageRendering,
    Interpolation,
)
from finn.utils.translations import trans


class QtImageControls(QtBaseImageControls):
    """Qt view and controls for the napari Image layer.

    Parameters
    ----------
    layer : finn.layers.Image
        An instance of a napari Image layer.

    Attributes
    ----------
    layer : finn.layers.Image
        An instance of a napari Image layer.
    MODE : Enum
        Available modes in the associated layer.
    PAN_ZOOM_ACTION_NAME : str
        String id for the pan-zoom action to bind to the pan_zoom button.
    TRANSFORM_ACTION_NAME : str
        String id for the transform action to bind to the transform button.
    button_group : qtpy.QtWidgets.QButtonGroup
        Button group for image based layer modes (PAN_ZOOM TRANSFORM).
    button_grid : qtpy.QtWidgets.QGridLayout
        GridLayout for the layer mode buttons
    panzoom_button : finn._qt.widgets.qt_mode_button.QtModeRadioButton
        Button to pan/zoom shapes layer.
    transform_button : finn._qt.widgets.qt_mode_button.QtModeRadioButton
        Button to transform shapes layer.
    attenuationSlider : qtpy.QtWidgets.QSlider
        Slider controlling attenuation rate for `attenuated_mip` mode.
    attenuationLabel : qtpy.QtWidgets.QLabel
        Label for the attenuation slider widget.
    interpComboBox : qtpy.QtWidgets.QComboBox
        Dropdown menu to select the interpolation mode for image display.
    interpLabel : qtpy.QtWidgets.QLabel
        Label for the interpolation dropdown menu.
    isoThresholdSlider : qtpy.QtWidgets.QSlider
        Slider controlling the isosurface threshold value for rendering.
    isoThresholdLabel : qtpy.QtWidgets.QLabel
        Label for the isosurface threshold slider widget.
    renderComboBox : qtpy.QtWidgets.QComboBox
        Dropdown menu to select the rendering mode for image display.
    renderLabel : qtpy.QtWidgets.QLabel
        Label for the rendering mode dropdown menu.
    """

    layer: "finn.layers.Image"
    PAN_ZOOM_ACTION_NAME = "activate_image_pan_zoom_mode"
    TRANSFORM_ACTION_NAME = "activate_image_transform_mode"

    def __init__(self, layer) -> None:
        super().__init__(layer)

        self.layer.events.interpolation2d.connect(self._on_interpolation_change)
        self.layer.events.interpolation3d.connect(self._on_interpolation_change)
        self.layer.events.rendering.connect(self._on_rendering_change)
        self.layer.events.iso_threshold.connect(self._on_iso_threshold_change)
        self.layer.events.attenuation.connect(self._on_attenuation_change)

        self.interpComboBox = QComboBox(self)
        self.interpComboBox.currentTextChanged.connect(self.changeInterpolation)
        self.interpComboBox.setToolTip(
            trans._(
                "Texture interpolation for display.\nnearest and linear are most performant."
            )
        )
        self.interpLabel = QLabel(trans._("interpolation:"))

        renderComboBox = QComboBox(self)
        rendering_options = [i.value for i in ImageRendering]
        renderComboBox.addItems(rendering_options)
        index = renderComboBox.findText(
            self.layer.rendering, Qt.MatchFlag.MatchFixedString
        )
        renderComboBox.setCurrentIndex(index)
        renderComboBox.currentTextChanged.connect(self.changeRendering)
        self.renderComboBox = renderComboBox
        self.renderLabel = QLabel(trans._("rendering:"))

        sld = QLabeledDoubleSlider(Qt.Orientation.Horizontal, parent=self)
        sld.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        cmin, cmax = self.layer.contrast_limits_range
        sld.setMinimum(cmin)
        sld.setMaximum(cmax)
        sld.setValue(self.layer.iso_threshold)
        sld.valueChanged.connect(self.changeIsoThreshold)
        self.isoThresholdSlider = sld
        self.isoThresholdLabel = QLabel(trans._("iso threshold:"))

        sld = QLabeledDoubleSlider(Qt.Orientation.Horizontal, parent=self)
        sld.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sld.setMinimum(0)
        sld.setMaximum(0.5)
        sld.setSingleStep(0.001)
        sld.setValue(self.layer.attenuation)
        sld.setDecimals(3)
        sld.valueChanged.connect(self.changeAttenuation)
        self.attenuationSlider = sld
        self.attenuationLabel = QLabel(trans._("attenuation:"))

        colormap_layout = QHBoxLayout()
        if hasattr(self.layer, "rgb") and self.layer.rgb:
            colormap_layout.addWidget(QLabel("RGB"))
            self.colormapComboBox.setVisible(False)
            self.colorbarLabel.setVisible(False)
        else:
            colormap_layout.addWidget(self.colorbarLabel)
            colormap_layout.addWidget(self.colormapComboBox)
        colormap_layout.addStretch(1)

        self.layout().addRow(self.button_grid)
        self.layout().addRow(self.opacityLabel, self.opacitySlider)
        self.layout().addRow(trans._("blending:"), self.blendComboBox)
        self.layout().addRow(trans._("contrast limits:"), self.contrastLimitsSlider)
        self.layout().addRow(trans._("auto-contrast:"), self.autoScaleBar)
        self.layout().addRow(trans._("gamma:"), self.gammaSlider)
        self.layout().addRow(trans._("colormap:"), colormap_layout)
        self.layout().addRow(self.interpLabel, self.interpComboBox)

        self.clippingPlaneControls = QtLayerClippingPlanes(self)

        for i in range(self.clippingPlaneControls.rowCount()):
            label_item = self.clippingPlaneControls.itemAt(i, QFormLayout.LabelRole)
            field_item = self.clippingPlaneControls.itemAt(i, QFormLayout.FieldRole)

            label_widget = label_item.widget() if label_item else None
            field_widget = field_item.widget() if field_item else None

            if label_widget and field_widget:
                self.layout().addRow(label_widget, field_widget)
            elif field_widget:  # If there's no label, just add the field
                self.layout().addRow(field_widget)

        self.layout().addRow(self.renderLabel, self.renderComboBox)
        self.layout().addRow(self.isoThresholdLabel, self.isoThresholdSlider)
        self.layout().addRow(self.attenuationLabel, self.attenuationSlider)

        self._on_ndisplay_changed()

    def changeInterpolation(self, text):
        """Change interpolation mode for image display.

        Parameters
        ----------
        text : str
            Interpolation mode used by vispy. Must be one of our supported
            modes:
            'bessel', 'bicubic', 'linear', 'blackman', 'catrom', 'gaussian',
            'hamming', 'hanning', 'hermite', 'kaiser', 'lanczos', 'mitchell',
            'nearest', 'spline16', 'spline36'
        """
        if self.ndisplay == 2:
            self.layer.interpolation2d = text
        else:
            self.layer.interpolation3d = text

    def changeRendering(self, text):
        """Change rendering mode for image display.

        Parameters
        ----------
        text : str
            Rendering mode used by vispy.
            Selects a preset rendering mode in vispy that determines how
            volume is displayed:
            * translucent: voxel colors are blended along the view ray until
              the result is opaque.
            * mip: maximum intensity projection. Cast a ray and display the
              maximum value that was encountered.
            * additive: voxel colors are added along the view ray until
              the result is saturated.
            * iso: isosurface. Cast a ray until a certain threshold is
              encountered. At that location, lighning calculations are
              performed to give the visual appearance of a surface.
            * attenuated_mip: attenuated maximum intensity projection. Cast a
              ray and attenuate values based on integral of encountered values,
              display the maximum value that was encountered after attenuation.
              This will make nearer objects appear more prominent.
        """
        self.layer.rendering = text
        self._update_rendering_parameter_visibility()

    def changeIsoThreshold(self, value):
        """Change isosurface threshold on the layer model.

        Parameters
        ----------
        value : float
            Threshold for isosurface.
        """
        with self.layer.events.blocker(self._on_iso_threshold_change):
            self.layer.iso_threshold = value

    def _on_contrast_limits_change(self):
        with self.layer.events.blocker(self._on_iso_threshold_change):
            cmin, cmax = self.layer.contrast_limits_range
            self.isoThresholdSlider.setMinimum(cmin)
            self.isoThresholdSlider.setMaximum(cmax)
        return super()._on_contrast_limits_change()

    def _on_iso_threshold_change(self):
        """Receive layer model isosurface change event and update the slider."""
        with self.layer.events.iso_threshold.blocker():
            self.isoThresholdSlider.setValue(self.layer.iso_threshold)

    def changeAttenuation(self, value):
        """Change attenuation rate for attenuated maximum intensity projection.

        Parameters
        ----------
        value : Float
            Attenuation rate for attenuated maximum intensity projection.
        """
        with self.layer.events.blocker(self._on_attenuation_change):
            self.layer.attenuation = value

    def _on_attenuation_change(self):
        """Receive layer model attenuation change event and update the slider."""
        with self.layer.events.attenuation.blocker():
            self.attenuationSlider.setValue(self.layer.attenuation)

    def _on_interpolation_change(self, event):
        """Receive layer interpolation change event and update dropdown menu.

        Parameters
        ----------
        event : finn.utils.event.Event
            The napari event that triggered this method.
        """
        interp_string = event.value.value

        with (
            self.layer.events.interpolation.blocker(),
            self.layer.events.interpolation2d.blocker(),
            self.layer.events.interpolation3d.blocker(),
        ):
            if self.interpComboBox.findText(interp_string) == -1:
                self.interpComboBox.addItem(interp_string)
            self.interpComboBox.setCurrentText(interp_string)

    def _on_rendering_change(self):
        """Receive layer model rendering change event and update dropdown menu."""
        with self.layer.events.rendering.blocker():
            index = self.renderComboBox.findText(
                self.layer.rendering, Qt.MatchFlag.MatchFixedString
            )
            self.renderComboBox.setCurrentIndex(index)
            self._update_rendering_parameter_visibility()

    def _update_rendering_parameter_visibility(self):
        """Hide isosurface rendering parameters if they aren't needed."""
        rendering = ImageRendering(self.layer.rendering)
        iso_threshold_visible = rendering == ImageRendering.ISO
        self.isoThresholdLabel.setVisible(iso_threshold_visible)
        self.isoThresholdSlider.setVisible(iso_threshold_visible)
        attenuation_visible = rendering == ImageRendering.ATTENUATED_MIP
        self.attenuationSlider.setVisible(attenuation_visible)
        self.attenuationLabel.setVisible(attenuation_visible)

    def _update_interpolation_combo(self):
        interp_names = [i.value for i in Interpolation.view_subset()]
        interp = (
            self.layer.interpolation2d
            if self.ndisplay == 2
            else self.layer.interpolation3d
        )
        with qt_signals_blocked(self.interpComboBox):
            self.interpComboBox.clear()
            self.interpComboBox.addItems(interp_names)
            self.interpComboBox.setCurrentText(interp)

    def _on_ndisplay_changed(self):
        """Update widget visibility based on 2D and 3D visualization modes."""
        self._update_interpolation_combo()
        self.clippingPlaneControls._on_ndisplay_changed()
        if self.ndisplay == 2:
            self.isoThresholdSlider.hide()
            self.isoThresholdLabel.hide()
            self.attenuationSlider.hide()
            self.attenuationLabel.hide()
            self.renderComboBox.hide()
            self.renderLabel.hide()
        else:
            self.renderComboBox.show()
            self.renderLabel.show()
            self._update_rendering_parameter_visibility()
        super()._on_ndisplay_changed()
