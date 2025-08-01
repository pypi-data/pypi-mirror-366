from typing import TYPE_CHECKING

import numpy as np
from napari.utils.notifications import show_error, show_info
from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from scipy.ndimage import center_of_mass, label
from scipy.ndimage import sum as ndimage_sum

from quantpunc.combobox_manager import ComboBoxManager
from quantpunc.quantification.puncta_labeler_registry import (
    PUNCTA_LABELER_REGISTRY,
    register_default_puncta_labelers,
)
from quantpunc.table.table_widget import TableWidget

if TYPE_CHECKING:
    from napari import Viewer, layers
register_default_puncta_labelers()


class PunctaAnalyzer(QWidget):
    def __init__(self, viewer: "Viewer", table_widget: TableWidget):
        super().__init__()
        self.viewer = viewer
        self.table_widget = table_widget
        self._init_widget()

    def get_puncta_labels(self) -> None:
        """
        Produces puncta labels for an image using a user-specified method and
        displays it in the viewer.
        """

        layer = self.img_combobox.currentData()

        if layer is None:
            return

        img = layer.data.copy()

        if img.ndim > 2:
            show_error("The selected image must be 2D.")
            return

        if not np.issubdtype(img.dtype, np.unsignedinteger):
            show_error(
                f"The image must be of an unsigned integer type (uint), but got {img.dtype}."
            )
            return

        mask_layer = self.mask_combobox.currentData()
        mask_data = None

        if mask_layer is not None:
            mask_data = mask_layer.data

            if mask_data.ndim > 2:
                show_error("The associated mask must be 2D.")
                return

            mask_data = mask_data.astype(np.uint16)

        label_intensity = int(self.intensity_line_edit.text())

        blob_labels = self.blob_labeler.label_puncta(
            image=img,
            masks=mask_data,
            label_intensity=label_intensity,
        )

        if blob_labels.size == 0:
            show_info("No puncta were detected.")
            return

        puncta_layer_name = f"{layer.name}_puncta"

        if puncta_layer_name in self.viewer.layers:
            self.viewer.layers.remove(puncta_layer_name)

        self.viewer.add_labels(
            data=blob_labels,
            name=puncta_layer_name,
        )

        self.viewer.layers.selection.active = self.viewer.layers[
            puncta_layer_name
        ]

    def get_puncta_counts_and_stats(self) -> None:
        """
        Extracts puncta counts, intensities, areas, and associated masks and stores
        them in tables.
        """

        layer = self.img_combobox.currentData()

        if layer is None:
            show_error("Select a labeled image to count.")
            return

        puncta_name = layer.name + "_puncta"

        try:
            puncta_layer = self.viewer.layers[puncta_name]
        except KeyError:
            puncta_layer = None

        if puncta_layer is None:
            show_error(
                "Please select a labels layer named like the selected image "
                "with '_puncta' added to the end (e.g., 'image_name_puncta')."
            )
            return

        puncta_labels = np.unique(puncta_layer.data)
        puncta_labels = puncta_labels[puncta_labels != 0]

        puncta_region = np.isin(puncta_layer.data, puncta_labels)
        counts: dict[int, int] = {}

        mask_layer = self.mask_combobox.currentData()

        if mask_layer is not None:
            if mask_layer.data.ndim > 2:
                show_error("Mask layer should be a 2D image.")
                return

            mask_labels = np.unique(mask_layer.data)
            mask_labels = mask_labels[mask_labels != 0]

            for mask_val in mask_labels:
                mask_region = mask_layer.data == mask_val
                combined_region = np.logical_and(mask_region, puncta_region)
                _, num_puncta = label(combined_region)

                counts[mask_val] = num_puncta

        else:
            _, num_puncta = label(puncta_region)
            counts[-1] = num_puncta

        count_dict_model = self.table_widget.count_table_view.dict_model

        count_dict_model.names_to_uuids[layer.name] = puncta_layer.unique_id
        count_dict_model.data_dict[puncta_layer.unique_id] = {
            "name": layer.name,
            "data": counts,
        }

        unique_puncta_labels, _ = label(puncta_layer.data)
        puncta_mask = unique_puncta_labels != 0

        puncta_ids = np.unique(unique_puncta_labels)
        puncta_ids = puncta_ids[puncta_ids != 0]

        areas = np.bincount(unique_puncta_labels.ravel())[1:]
        intensities = ndimage_sum(
            layer.data,
            labels=unique_puncta_labels,
            index=puncta_ids,
        )

        if mask_layer is not None:
            mask_labels = []
            centroids = center_of_mass(
                puncta_mask,
                labels=unique_puncta_labels,
                index=puncta_ids,
            )

            for y, x in centroids:
                y, x = int(round(y)), int(round(x))
                mask_label = mask_layer.data[y, x]
                mask_labels.append(mask_label)

        else:
            mask_labels = [-1] * len(puncta_ids)

        puncta_stats: dict[int, tuple] = {
            int(p): (int(a), int(i), int(m))
            for p, a, i, m in zip(
                puncta_ids,
                areas,
                intensities,
                mask_labels,
            )
        }

        puncta_dict_model = self.table_widget.puncta_table_view.dict_model

        puncta_dict_model.names_to_uuids[layer.name] = puncta_layer.unique_id
        puncta_dict_model.data_dict[puncta_layer.unique_id] = {
            "name": layer.name,
            "data": puncta_stats,
        }

        if not self.table_widget.save_initialized:
            self.table_widget.initialize_table_settings()

        selection_index = self.table_widget.table_selection_box.findText(
            layer.name
        )

        if selection_index == -1:
            (
                self.table_widget.table_selection_box.addItem(
                    layer.name, userData=puncta_layer.unique_id
                )
            )

            selection_index = self.table_widget.table_selection_box.findText(
                layer.name
            )

        self.table_widget.table_selection_box.setCurrentIndex(0)
        self.table_widget.table_selection_box.setCurrentIndex(selection_index)
        self.viewer.layers.selection.active = puncta_layer

    def _init_widget(self) -> None:
        self.main_layout = QVBoxLayout()

        img_label = QLabel("Select layer")
        mask_label = QLabel("Select mask")
        method_label = QLabel("Method")

        self.method_combobox = QComboBox()
        self.img_combobox = QComboBox()
        self.mask_combobox = QComboBox()

        self.method_combobox.addItems(list(PUNCTA_LABELER_REGISTRY.keys()))
        self.method_combobox.currentIndexChanged.connect(
            self._update_parameters
        )

        def image_only_filter(layer: "layers.Layer") -> bool:
            return type(layer).__name__ == "Image"

        self.labeling_cbox_manager = ComboBoxManager(viewer=self.viewer)
        self.labeling_cbox_manager.register_combobox(
            combobox=self.img_combobox, filter_fn=image_only_filter
        )
        self.labeling_cbox_manager.register_combobox(
            combobox=self.mask_combobox, filter_fn=None
        )

        intensity_form_layout = QFormLayout()
        intensity_label = QLabel("label_color")
        self.intensity_line_edit = QLineEdit()
        self.intensity_line_edit.setValidator(QIntValidator())
        self.intensity_line_edit.setText("1")
        intensity_form_layout.addRow(intensity_label, self.intensity_line_edit)

        count_buttons_layout = QHBoxLayout()
        label_puncta_button = QPushButton("Label puncta")
        label_puncta_button.setObjectName("label_button")
        label_puncta_button.clicked.connect(self.get_puncta_labels)
        count_buttons_layout.addWidget(label_puncta_button)

        count_puncta_button = QPushButton("Count puncta")
        count_puncta_button.setObjectName("count_button")
        count_puncta_button.clicked.connect(self.get_puncta_counts_and_stats)
        count_buttons_layout.addWidget(count_puncta_button)

        self.main_layout.addWidget(img_label)
        self.main_layout.addWidget(self.img_combobox)
        self.main_layout.addWidget(mask_label)
        self.main_layout.addWidget(self.mask_combobox)
        self.main_layout.addWidget(method_label)
        self.main_layout.addWidget(self.method_combobox)
        self.main_layout.addLayout(intensity_form_layout)
        self.main_layout.addLayout(count_buttons_layout)
        self.main_layout.setSpacing(7)
        self.main_layout.setContentsMargins(7, 5, 7, 5)

        selected_labeler = self.method_combobox.currentText()
        selected_method = PUNCTA_LABELER_REGISTRY[selected_labeler]

        self.blob_labeler = selected_method(
            viewer=self.viewer, puncta_analyzer=self
        )
        self.method_layout = self.blob_labeler.initialize_widgets()
        self.method_layout_index = (
            self.main_layout.indexOf(self.method_combobox) + 1
        )
        self.main_layout.insertLayout(
            self.method_layout_index, self.method_layout
        )

        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMaximumHeight(500)

    def _update_parameters(self) -> None:
        """
        Removes widgets associated with previously selected puncta labeler
        and replaces them with the widgets associated with the current one.
        """

        while self.method_layout.count():
            item = self.method_layout.takeAt(0)

            if item is None:
                return

            widget = item.widget()

            if widget:
                widget.deleteLater()

        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item and item.layout() == self.method_layout:
                self.main_layout.takeAt(i)
                break

        selected_labeler = self.method_combobox.currentText()
        selected_method = PUNCTA_LABELER_REGISTRY[selected_labeler]

        self.blob_labeler = selected_method(
            viewer=self.viewer, puncta_analyzer=self
        )
        self.method_layout = self.blob_labeler.initialize_widgets()
        self.main_layout.insertLayout(
            self.method_layout_index, self.method_layout
        )
