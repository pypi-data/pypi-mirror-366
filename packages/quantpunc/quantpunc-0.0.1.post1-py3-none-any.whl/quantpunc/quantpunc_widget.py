from napari import Viewer
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from quantpunc.preprocessing import Preprocessor
from quantpunc.quantification.colocalization import ColocalizationWidget
from quantpunc.quantification.puncta_analyzer import (
    PunctaAnalyzer,
)
from quantpunc.table.table_widget import TableWidget
from quantpunc.watershed import WatershedWidget


class QuantPunc(QWidget):
    def __init__(self, viewer: Viewer):
        super().__init__()
        self.viewer = viewer
        self._init_widget()

    def _init_widget(self) -> None:
        self.preprocessor = Preprocessor(viewer=self.viewer)
        self.table_widget = TableWidget(viewer=self.viewer)
        self.blob_counter = PunctaAnalyzer(
            viewer=self.viewer,
            table_widget=self.table_widget,
        )
        self.watershed_widget = WatershedWidget(
            viewer=self.viewer,
            table_widget=self.table_widget,
        )
        self.colocalization = ColocalizationWidget(
            viewer=self.viewer,
            table_widget=self.table_widget,
        )

        self.quantification_tab = QTabWidget()
        self.quantification_tab.addTab(self.blob_counter, "Puncta Labeling")
        self.quantification_tab.addTab(self.watershed_widget, "Watershed")
        self.quantification_tab.addTab(self.colocalization, "Colocalization")
        (
            self.quantification_tab.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Fixed
            )
        )

        quantification_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.quantification_tab)
        quantification_widget.setLayout(main_layout)
        quantification_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        quantification_widget.setMaximumHeight(410)

        self.viewer.layers.events.removed.connect(
            self.table_widget.on_layer_deleted
        )

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.preprocessor)
        splitter.addWidget(quantification_widget)
        splitter.addWidget(self.table_widget)

        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)

        splitter.setHandleWidth(2)

        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #888;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 5)

        self.setLayout(layout)
