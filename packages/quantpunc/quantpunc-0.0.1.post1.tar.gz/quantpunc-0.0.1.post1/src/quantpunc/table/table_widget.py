from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from qtpy.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from quantpunc.table.table_model_view import TableView

if TYPE_CHECKING:
    from napari import Viewer


class TableWidget(QWidget):
    def __init__(self, viewer: "Viewer"):
        super().__init__()
        self.viewer = viewer
        self.save_initialized: bool = False
        self.save_one_button: QPushButton | None = None
        self.save_all_button: QPushButton | None = None
        self.save_buttons_layout: QHBoxLayout | None = None
        self._init_widget()

    def on_selection_changed(self, index: int) -> None:
        """
        Changes data displayed in table to a newly selected image layer.

        Parameters
        ----------
        index: int
            Index of the image layer name in the dropdown menu.
        """

        layer_name = self.table_selection_box.itemText(index)

        counted_layer_data = self.get_data_dict(
            table_view=self.count_table_view, layer_name=layer_name
        )

        coloc_layer_data = self.get_data_dict(
            table_view=self.iou_table_view, layer_name=layer_name
        )

        puncta_layer_data = self.get_data_dict(
            table_view=self.puncta_table_view, layer_name=layer_name
        )

        count_dict_model = self.count_table_view.dict_model
        coloc_dict_model = self.iou_table_view.dict_model
        puncta_dict_model = self.puncta_table_view.dict_model

        counts_dict = None
        coloc_dict = None
        puncta_dict = None

        if counted_layer_data is not None:
            counts_dict = counted_layer_data["data"]

        if coloc_layer_data is not None:
            coloc_dict = coloc_layer_data["data"]

        if puncta_layer_data is not None:
            puncta_dict = puncta_layer_data["data"]

        count_dict_model.setCurrentDict(layer_data=counts_dict)
        coloc_dict_model.setCurrentDict(layer_data=coloc_dict)
        puncta_dict_model.setCurrentDict(layer_data=puncta_dict)

    def get_data_dict(
        self, table_view: QTableView, layer_name: str
    ) -> dict[str, Any] | None:
        dict_model = table_view.dict_model
        img_name = layer_name
        uuid = dict_model.names_to_uuids.get(img_name)

        if uuid is not None:
            return dict_model.data_dict[uuid]

        return None

    def on_layer_deleted(self, event) -> None:
        """
        Clears data associated with a deleted layer from each table model.

        Parameters
        ----------
        event
            Contains layers that were deleted.
        """

        selection_event_emitter = self.viewer.layers.selection.events.active

        with selection_event_emitter.blocker():
            layer = event.value
            count_dict_model = self.count_table_view.dict_model
            coloc_dict_model = self.iou_table_view.dict_model
            puncta_dict_model = self.puncta_table_view.dict_model

            if layer.unique_id in count_dict_model.data_dict:
                del count_dict_model.data_dict[layer.unique_id]

                for name, uuid in count_dict_model.names_to_uuids.items():
                    if layer.unique_id == uuid:
                        del count_dict_model.names_to_uuids[name]
                        break

            if layer.unique_id in puncta_dict_model.data_dict:
                del puncta_dict_model.data_dict[layer.unique_id]

                for name, uuid in puncta_dict_model.names_to_uuids.items():
                    if layer.unique_id == uuid:
                        del puncta_dict_model.names_to_uuids[name]
                        break

            for uuid_pair in coloc_dict_model.data_dict:
                if layer.unique_id in uuid_pair:
                    del coloc_dict_model.data_dict[uuid_pair]

                    names_to_remove = [
                        name
                        for name, pair in coloc_dict_model.names_to_uuids.items()
                        if pair == uuid_pair
                    ]

                    for name in names_to_remove:
                        del coloc_dict_model.names_to_uuids[name]

                    break

            for i in range(self.table_selection_box.count()):
                if self.table_selection_box.itemData(i) == layer.unique_id:
                    self.table_selection_box.removeItem(i)
                    break

            if len(event.source) == 1:
                if (
                    not count_dict_model.data_dict
                    and not coloc_dict_model.data_dict
                    and self.save_initialized is True
                ):
                    if self.save_one_button is not None:
                        self.save_one_button.clicked.disconnect(
                            self.save_counts_coords_one
                        )

                    if self.save_all_button is not None:
                        self.save_all_button.clicked.disconnect(
                            self.save_counts_coords_all
                        )

                    if self.save_buttons_layout is not None:
                        for i in reversed(
                            range(self.save_buttons_layout.count())
                        ):
                            item = self.save_buttons_layout.itemAt(i)

                            if item is not None:
                                widget = item.widget()

                            if widget is not None:
                                widget.deleteLater()

                    self.save_initialized = False

                    self.viewer.layers.selection.events.active.disconnect(
                        self.on_selection_changed
                    )

                count_dict_model.setCurrentDict(layer_data=None)
                coloc_dict_model.setCurrentDict(layer_data=None)

            self.table_selection_box.setCurrentIndex(-1)
            self.table_selection_box.setCurrentIndex(0)

        return

    def initialize_table_settings(self) -> None:
        """
        Adds save buttons after puncta quantification.
        """

        (
            self.table_selection_box.currentIndexChanged.connect(
                self.on_selection_changed
            )
        )

        self.save_buttons_layout = QHBoxLayout()
        self.save_one_button = QPushButton("Save selected data")
        self.save_one_button.clicked.connect(self.save_counts_coords_one)
        self.save_all_button = QPushButton("Save all data")
        self.save_all_button.clicked.connect(self.save_counts_coords_all)
        self.save_buttons_layout.addWidget(self.save_one_button)
        self.save_buttons_layout.addWidget(self.save_all_button)
        self.main_layout.addLayout(self.save_buttons_layout)

        self.save_initialized = True

    def save_counts_coords_one(self) -> None:
        """
        Saves puncta stats for the currently selected layer shown in the table
        as a csv.
        """

        folder_path_input = QFileDialog.getExistingDirectory(
            self, "Select folder to save count and coordinate data"
        )

        if folder_path_input:
            folder_path = Path(folder_path_input)
            index = self.table_selection_box.currentIndex()

            if index == 0:
                return

            img_name = self.table_selection_box.itemText(index)

            count_dict_model = self.count_table_view.dict_model
            coloc_dict_model = self.iou_table_view.dict_model
            puncta_dict_model = self.puncta_table_view.dict_model

            count_uuid = count_dict_model.names_to_uuids.get(img_name)
            coloc_uuid = coloc_dict_model.names_to_uuids.get(img_name)
            puncta_uuid = puncta_dict_model.names_to_uuids.get(img_name)

            if count_uuid is not None:
                count_data = count_dict_model.data_dict[count_uuid]["data"]
                count_name = count_dict_model.data_dict[count_uuid]["name"]
                count_df = pd.DataFrame(
                    list(count_data.items()), columns=["mask", "count"]
                )
                save_path = folder_path / f"{count_name}_counts.csv"
                count_df.to_csv(save_path, index=False)

            if coloc_uuid is not None:
                coloc_data = coloc_dict_model.data_dict[coloc_uuid]["data"]
                coloc_name = coloc_dict_model.data_dict[coloc_uuid]["name"]
                coloc_name = "-".join(coloc_name)
                coloc_df = pd.DataFrame(
                    list(coloc_data.items()), columns=["mask", "iou"]
                )
                save_path = folder_path / f"{coloc_name}_coloc_summary.csv"
                coloc_df.to_csv(save_path, index=False)

            if puncta_uuid is not None:
                puncta_data = puncta_dict_model.data_dict[puncta_uuid]["data"]
                puncta_name = puncta_dict_model.data_dict[puncta_uuid]["name"]

                puncta_df = pd.DataFrame.from_dict(
                    puncta_data,
                    orient="index",
                    columns=["area", "integrated_intensity", "mask_label"],
                )
                puncta_df.index.name = "puncta_id"
                puncta_df.reset_index(inplace=True)

                save_path = folder_path / f"{puncta_name}_puncta_summary.csv"
                puncta_df.to_csv(save_path, index=False)

            return

    def save_counts_coords_all(self) -> None:
        """
        Saves puncta stats for all layers that have been quantified as csv files.
        """

        folder_path_input = QFileDialog.getExistingDirectory(
            self, "Select folder to save count and coordinate data"
        )

        if folder_path_input:
            folder_path = Path(folder_path_input)
            count_dict_model = self.count_table_view.dict_model
            coloc_dict_model = self.iou_table_view.dict_model
            puncta_dict_model = self.puncta_table_view.dict_model

            if count_dict_model.data_dict:
                for _, count_data in count_dict_model.data_dict.items():
                    count_name = count_data["name"]
                    count_data = count_data["data"]

                    count_df = pd.DataFrame(
                        list(count_data.items()), columns=["mask", "count"]
                    )

                    save_path = folder_path / f"{count_name}_counts.csv"
                    count_df.to_csv(save_path, index=False)

            if coloc_dict_model.data_dict:
                for _, coloc_data in coloc_dict_model.data_dict.items():
                    coloc_name = coloc_data["name"]
                    coloc_name = "-".join(coloc_name)
                    coloc_data = coloc_data["data"]

                    coloc_df = pd.DataFrame(
                        list(coloc_data.items()), columns=["mask", "iou"]
                    )

                    save_path = folder_path / f"{coloc_name}_coloc_summary.csv"
                    coloc_df.to_csv(save_path, index=False)

            if puncta_dict_model.data_dict:
                for _, puncta_data in puncta_dict_model.data_dict.items():
                    puncta_name = puncta_data["name"]
                    puncta_data = puncta_data["data"]

                    puncta_df = pd.DataFrame.from_dict(
                        puncta_data,
                        orient="index",
                        columns=["area", "integrated_intensity", "mask_label"],
                    )
                    puncta_df.index.name = "puncta_id"
                    puncta_df.reset_index(inplace=True)

                    save_path = (
                        folder_path / f"{puncta_name}_puncta_summary.csv"
                    )
                    puncta_df.to_csv(save_path, index=False)

    def _init_widget(self) -> None:
        self.main_layout = QVBoxLayout()
        self.table_layout = QVBoxLayout()
        self.table_tabs = QTabWidget()
        self.info_label = QLabel("Select layer to display table")

        self.table_selection_box = QComboBox()
        self.table_selection_box.addItem("None", userData=None)

        self.count_table_view = TableView(headers=["Mask", "Count"])
        self.puncta_table_view = TableView(
            headers=["ID", "Area", "Intensity", "Mask"]
        )
        self.iou_table_view = TableView(headers=["Mask", "IoU"])

        self.table_tabs.addTab(self.count_table_view, "Counts")
        self.table_tabs.addTab(self.puncta_table_view, "Puncta Stats")
        self.table_tabs.addTab(self.iou_table_view, "Colocalization")
        self.table_tabs.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.table_selection_box)
        self.main_layout.addWidget(self.table_tabs)

        self.setLayout(self.main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
