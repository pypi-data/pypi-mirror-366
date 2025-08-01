from typing import TYPE_CHECKING

from napari.utils.notifications import show_error
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from scipy.ndimage import distance_transform_edt, label
from skimage.filters import sobel
from skimage.segmentation import watershed

from quantpunc.combobox_manager import ComboBoxManager
from quantpunc.table.table_widget import TableWidget

if TYPE_CHECKING:
    from napari import Viewer, layers


class WatershedWidget(QWidget):
    def __init__(self, viewer: "Viewer", table_widget: TableWidget):
        super().__init__()
        self.viewer = viewer
        self.table_widget = table_widget
        self._init_widget()

    def watershed_layer(self) -> None:
        """
        Applies watershed segmentation to a puncta labels layer with an
        elevation map from a distance transform or Sobel filter. The user
        can also provide an optional labels layer with seed points.
        """

        layer = self.img_combobox.currentData()

        if layer is None:
            show_error("Please select an image to watershed.")
            return

        img = layer.data.copy()

        if img.ndim > 2:
            show_error("The selected image must be 2D.")
            return

        seed_points_layer = self.seed_point_combobox.currentData()

        if seed_points_layer is not None:
            seed_points = seed_points_layer.data.copy()
            seed_points = label(seed_points)[0]
        else:
            seed_points = None

        elevation_map = self.elevation_map_combobox.currentText()

        if elevation_map == "Distance Transform":
            transformed_img = -distance_transform_edt(img)
        elif elevation_map == "Sobel":
            transformed_img = sobel(img)
        else:
            transformed_img = img

        watershed_img = watershed(
            image=transformed_img,
            markers=seed_points,
            mask=img,
        )

        watershed_layer_name = f"{layer.name}_watershed"

        if watershed_layer_name in self.viewer.layers:
            self.viewer.layers.events.removed.disconnect(
                self.table_widget.on_layer_deleted
            )
            self.viewer.layers.remove(watershed_layer_name)
            self.viewer.layers.events.removed.connect(
                self.table_widget.on_layer_deleted
            )

        self.viewer.add_labels(data=watershed_img, name=watershed_layer_name)

        self.viewer.layers.selection.active = self.viewer.layers[
            watershed_layer_name
        ]

        layer.visible = False

        if seed_points_layer is not None:
            seed_points_layer.visible = False

    def _init_widget(self) -> None:
        self.main_layout = QVBoxLayout()

        img_label = QLabel("Select masks to watershed")
        seed_point_label = QLabel("Select seed point layer")
        elevation_map_label = QLabel("Elevation map")

        self.img_combobox = QComboBox()
        self.seed_point_combobox = QComboBox()
        self.elevation_map_combobox = QComboBox()

        def labels_only_filter(layer: "layers.Layer") -> bool:
            return type(layer).__name__ == "Labels"

        self.labeling_cbox_manager = ComboBoxManager(viewer=self.viewer)
        self.labeling_cbox_manager.register_combobox(
            combobox=self.img_combobox,
            filter_fn=labels_only_filter,
        )
        self.labeling_cbox_manager.register_combobox(
            combobox=self.seed_point_combobox,
            filter_fn=labels_only_filter,
        )

        self.elevation_map_combobox.addItems(["Distance Transform", "Sobel"])

        watershed_button = QPushButton("Watershed")
        watershed_button.setObjectName("watershed_button")
        watershed_button.clicked.connect(self.watershed_layer)

        self.main_layout.addWidget(img_label)
        self.main_layout.addWidget(self.img_combobox)
        self.main_layout.addWidget(seed_point_label)
        self.main_layout.addWidget(self.seed_point_combobox)
        self.main_layout.addWidget(elevation_map_label)
        self.main_layout.addWidget(self.elevation_map_combobox)
        self.main_layout.addWidget(watershed_button)
        self.main_layout.setSpacing(7)
        self.main_layout.setContentsMargins(7, 5, 7, 5)

        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMaximumHeight(200)
