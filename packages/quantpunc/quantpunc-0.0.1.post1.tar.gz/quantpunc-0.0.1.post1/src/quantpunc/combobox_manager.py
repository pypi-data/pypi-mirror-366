from typing import TYPE_CHECKING, Callable, List, Tuple

from qtpy.QtWidgets import QComboBox

if TYPE_CHECKING:
    from napari import Viewer


class ComboBoxManager:
    def __init__(self, viewer: "Viewer"):
        self.viewer = viewer
        self.comboboxes: List[Tuple[QComboBox, Callable | None]] = []

        self.viewer.layers.events.inserted.connect(self._add_layer)
        self.viewer.layers.events.removed.connect(self._remove_layer)

    def register_combobox(
        self,
        combobox: QComboBox,
        filter_fn: Callable | None = None,
    ) -> None:
        self.comboboxes.append((combobox, filter_fn))
        self._populate_combobox(combobox, filter_fn)

    def _populate_combobox(
        self, combobox: QComboBox, filter_fn: Callable | None
    ) -> None:
        """
        Adds layer names and data from the layer list to the combobox with optional
        filtering based on layer type.

        Parameters
        ----------
        combobox: QComboBox
            Dropdown menu of layer names.
        filter_fn: Callable | None
            Optional function to filter layer types.
        """

        combobox.blockSignals(True)
        combobox.clear()

        combobox.addItem("None", userData=None)

        for layer in self.viewer.layers:
            if filter_fn is None or filter_fn(layer):
                combobox.addItem(layer.name, userData=layer)

        combobox.blockSignals(False)

    def _add_layer(self, event) -> None:
        layer = event.value
        layer.events.name.connect(self._rename_layer)

        for combobox, filter_fn in self.comboboxes:
            if filter_fn is None or filter_fn(layer):
                combobox.addItem(layer.name, userData=layer)

    def _remove_layer(self, event) -> None:
        layer = event.value
        layer.events.name.disconnect(self._rename_layer)

        for combobox, _ in self.comboboxes:
            idx = combobox.findText(layer.name)
            if idx != -1:
                combobox.removeItem(idx)

    def _rename_layer(self, event) -> None:
        for combobox, filter_fn in self.comboboxes:
            self._populate_combobox(combobox, filter_fn)
