from qtpy.QtCore import QAbstractTableModel, QModelIndex, Qt
from qtpy.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QSizePolicy,
    QTableView,
)


class DictionaryModel(QAbstractTableModel):
    def __init__(self, headers: list[str]):
        super().__init__()
        self.data_dict: dict[str | tuple, dict] = {}
        self.names_to_uuids: dict[str | tuple, str | tuple] = {}
        self.current_data: list[tuple] | None = None

        self.headers = headers
        self.initialized = False

    def rowCount(self, parent=None) -> int:
        if self.current_data is not None:
            return len(self.current_data)
        else:
            return 0

    def columnCount(self, parent=None) -> int:
        if self.current_data is not None:
            return len(self.headers)
        else:
            return 0

    def data(
        self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole
    ) -> str | None:
        """
        Displays data from the model to a cell in the table.

        Parameters
        ----------
        index: QModelIndex
            The cell's index.
        role: Qt.ItemDataRole.DisplayRole
            Used to request data to display to the table.

        Returns
        -------
        str | None
            Item to be displayed in a cell. None if there's no data
            or the index is invalid.
        """

        if not index.isValid() or self.current_data is None:
            return None
        elif role == Qt.ItemDataRole.DisplayRole:
            row, col = index.row(), index.column()
            label, data = self.current_data[row]

            if isinstance(data, (int, float)):
                return str(label) if col == 0 else str(data)
            elif isinstance(data, tuple):
                return str(label) if col == 0 else str(data[col - 1])

        return None

    def headerData(
        self,
        section,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> None:
        """
        Displays column headers.

        Parameters
        ----------
        section
            The header's index.
        orientation: Qt.Orientation
            Specifies whether orientation is vertical or horizontal.
        role: Qt.ItemDataRole.DisplayRole
            Used to request header data.
        """

        if (
            role == int(Qt.ItemDataRole.DisplayRole)
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.headers[section]

        return None

    def setCurrentDict(self, layer_data: dict[int, int] | None) -> None:
        """
        Resets model to display new data in the table view. Clears the current
        data if None is passed.

        Parameters
        ----------
        layer_data: dict[int, int] | None
            New data for the model.
        """

        self.beginResetModel()

        if layer_data is not None:
            self.current_data = list(layer_data.items())
        else:
            self.current_data = None

        self.endResetModel()


class TableView(QTableView):
    def __init__(self, headers=list[str]):
        super().__init__()
        self.dict_model = DictionaryModel(headers=headers)
        self.setModel(self.dict_model)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setCornerButtonEnabled(False)
        self.setTabKeyNavigation(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.selection_model = self.selectionModel()

    def get_label_column_index(self) -> int:
        for col in range(self.df_model.columnCount()):
            if (
                self.df_model.headerData(
                    col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
                )
                == "label"
            ):
                return col

        raise ValueError("Label column not found")
