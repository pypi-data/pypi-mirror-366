from typing import TYPE_CHECKING

import numpy as np
from napari.utils.notifications import show_error
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from quantpunc.combobox_manager import ComboBoxManager
from quantpunc.table.table_widget import TableWidget

if TYPE_CHECKING:
    from napari import Viewer, layers


class ColocalizationWidget(QWidget):
    def __init__(self, viewer: "Viewer", table_widget: TableWidget):
        super().__init__()
        self.viewer = viewer
        self.table_widget = table_widget
        self._init_widget()

    def get_iou(self) -> None:
        """
        Computes the intersection over union for two labels layers and stores it
        in a table model.
        """

        first_puncta = self.first_combobox.currentData()
        second_puncta = self.second_combobox.currentData()
        mask_layer = self.mask_combobox.currentData()

        if first_puncta is None or second_puncta is None:
            show_error(
                "Please ensure a layer is selected in both dropdown menus."
            )
            return

        if first_puncta.data.ndim > 2 or second_puncta.data.ndim > 2:
            show_error("The two layers must be 2D.")
            return

        first_nonzero = first_puncta.data > 0
        second_nonzero = second_puncta.data > 0

        iou_scores = {}

        if mask_layer is not None:
            mask_data = mask_layer.data
            labels = np.unique(mask_data)
            labels = labels[labels != 0]

            for label in labels:
                region = mask_data == label

                intersection = (
                    np.logical_and(first_nonzero, second_nonzero) & region
                ).sum()
                union = (
                    np.logical_or(first_nonzero, second_nonzero) & region
                ).sum()

                if union == 0:
                    iou_scores[label] = 0
                else:
                    iou_scores[label] = round(intersection / union, 4)

        else:
            intersection = np.logical_and(first_nonzero, second_nonzero).sum()
            union = np.logical_or(first_nonzero, second_nonzero).sum()

            if union == 0:
                iou_scores[-1] = 0
            else:
                iou_scores[-1] = round(intersection / union, 4)

        iou_view = self.table_widget.iou_table_view
        iou_model = iou_view.dict_model

        paired_uuids = tuple(
            sorted((first_puncta.unique_id, second_puncta.unique_id))
        )
        first_name = first_puncta.name.removesuffix("_puncta")
        second_name = second_puncta.name.removesuffix("_puncta")
        paired_names = tuple(sorted((first_name, second_name)))

        names_to_delete = []
        uuid_pairs_to_delete = set()

        for name, old_uuids in iou_model.names_to_uuids.items():
            if any(uuid in old_uuids for uuid in paired_uuids):
                names_to_delete.append(name)
                uuid_pairs_to_delete.add(old_uuids)

        for name in names_to_delete:
            del iou_model.names_to_uuids[name]

        for uuid_pair in uuid_pairs_to_delete:
            iou_model.data_dict.pop(uuid_pair, None)

        iou_model.names_to_uuids[first_name] = paired_uuids
        iou_model.names_to_uuids[second_name] = paired_uuids
        iou_model.data_dict[paired_uuids] = {
            "name": paired_names,
            "data": iou_scores,
        }

        if not self.table_widget.save_initialized:
            self.table_widget.initialize_table_settings()

        first_selection_index = self.table_widget.table_selection_box.findText(
            first_name
        )

        second_selection_index = (
            self.table_widget.table_selection_box.findText(second_name)
        )

        if first_selection_index == -1:
            (
                self.table_widget.table_selection_box.addItem(
                    first_name, userData=first_puncta.unique_id
                )
            )

            first_selection_index = (
                self.table_widget.table_selection_box.findText(first_name)
            )

        if second_selection_index == -1:
            (
                self.table_widget.table_selection_box.addItem(
                    second_name, userData=second_puncta.unique_id
                )
            )

        self.table_widget.table_selection_box.setCurrentIndex(0)
        self.table_widget.table_selection_box.setCurrentIndex(
            first_selection_index
        )
        self.viewer.layers.selection.active = first_puncta

    def _init_widget(self) -> None:
        main_layout = QVBoxLayout()

        first_label = QLabel("Select first annotated layer")
        second_label = QLabel("Select second annotated layer")
        mask_label = QLabel("Select mask")

        self.first_combobox = QComboBox()
        self.second_combobox = QComboBox()
        self.mask_combobox = QComboBox()

        def label_only_filter(layer: "layers.Layer") -> bool:
            return type(layer).__name__ == "Labels"

        self.colocalization_cbox_manager = ComboBoxManager(viewer=self.viewer)
        self.colocalization_cbox_manager.register_combobox(
            combobox=self.first_combobox, filter_fn=label_only_filter
        )
        self.colocalization_cbox_manager.register_combobox(
            combobox=self.second_combobox, filter_fn=label_only_filter
        )
        self.colocalization_cbox_manager.register_combobox(
            combobox=self.mask_combobox, filter_fn=None
        )

        self.form_layout = QFormLayout()

        iou_button = QPushButton("Compute IoU")
        iou_button.setObjectName("iou_button")
        iou_button.clicked.connect(self.get_iou)

        main_layout.addWidget(first_label)
        main_layout.addWidget(self.first_combobox)
        main_layout.addWidget(second_label)
        main_layout.addWidget(self.second_combobox)
        main_layout.addWidget(mask_label)
        main_layout.addWidget(self.mask_combobox)
        main_layout.addWidget(iou_button)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(7, 5, 7, 5)
        self.setLayout(main_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(200)
