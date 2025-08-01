from typing import TYPE_CHECKING

import numpy as np
from napari.utils.notifications import show_error
from qtpy.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from skimage.exposure import equalize_adapthist, rescale_intensity
from skimage.restoration import denoise_wavelet

from quantpunc.combobox_manager import ComboBoxManager

if TYPE_CHECKING:
    from napari import Viewer


class Preprocessor(QWidget):
    def __init__(self, viewer: "Viewer"):
        super().__init__()
        self.viewer = viewer
        self._init_widget()

    def process_images(self) -> None:
        layer = self.img_combobox.currentData()

        if type(layer).__name__ == "Image":
            img = layer.data.copy()

            if img.ndim > 2:
                show_error("The selected image must be 2D.")
                return

            img_name = layer.name
            processed_img = self.preprocess_pipeline(img=img)
            processed_name = f"{img_name}_processed"

            if processed_name in self.viewer.layers:
                self.viewer.layers.remove(processed_name)

            self.viewer.add_image(data=processed_img, name=processed_name)

    def preprocess_pipeline(self, img: np.ndarray) -> np.ndarray:
        """
        Processes an image using wavelet denoising, intensity rescaling, and
        adaptive histogram equalization.

        Parameters
        ----------
        image: np.ndarray
            Array of a image layer.

        Returns
        -------
        np.ndarray
            Array of a processed image.
        """

        current_mode = self.mode_combobox.currentText()
        current_method = self.method_combobox.currentText()

        img = denoise_wavelet(
            image=img, mode=current_mode, method=current_method
        )

        img = rescale_intensity(image=img, out_range=np.float64)
        img = equalize_adapthist(image=img)
        img = rescale_intensity(image=img, out_range=np.uint16)

        return img

    def _init_widget(self) -> None:
        main_layout = QVBoxLayout()
        preprocessing_layout = QVBoxLayout()
        preprocessing_group = QGroupBox("Preprocessing")

        img_label = QLabel("Select layer")
        method_label = QLabel("Thresholding Method")
        mode_label = QLabel("Denoising Mode")

        self.img_combobox = QComboBox()
        self.preprocess_cbox_manager = ComboBoxManager(viewer=self.viewer)
        self.preprocess_cbox_manager.register_combobox(
            combobox=self.img_combobox, filter_fn=None
        )

        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems(["soft", "hard"])

        self.method_combobox = QComboBox()
        self.method_combobox.addItems(["BayesShrink", "VisuShrink"])

        process_button = QPushButton("Process")
        process_button.setObjectName("process_button")
        process_button.clicked.connect(self.process_images)

        preprocessing_layout.addWidget(img_label)
        preprocessing_layout.addWidget(self.img_combobox)
        preprocessing_layout.addWidget(mode_label)
        preprocessing_layout.addWidget(self.mode_combobox)
        preprocessing_layout.addWidget(method_label)
        preprocessing_layout.addWidget(self.method_combobox)
        preprocessing_layout.addWidget(process_button)
        preprocessing_layout.setSpacing(5)
        preprocessing_layout.setContentsMargins(10, 20, 10, 10)

        preprocessing_group.setLayout(preprocessing_layout)
        preprocessing_group.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        main_layout.addWidget(preprocessing_group)

        self.setLayout(main_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(self.sizeHint().height())
