from collections import defaultdict
from typing import TYPE_CHECKING, Callable

import numpy as np
import pandas as pd
from napari.utils.notifications import show_error, show_info
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)
from skimage import (
    exposure,
    filters,
)
from skimage.draw import disk
from skimage.exposure import equalize_adapthist
from skimage.feature import (
    blob_dog,
    blob_doh,
    blob_log,
    hessian_matrix,
    hessian_matrix_eigvals,
)
from skimage.restoration import denoise_wavelet
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from quantpunc.combobox_manager import ComboBoxManager
from quantpunc.quantification.abstract_puncta_labeler import (
    AbstractPunctaLabeler,
)

if TYPE_CHECKING:
    from napari import Viewer, layers

    from quantpunc.quantification.puncta_analyzer import PunctaAnalyzer


class SkimageBlobLabeler(AbstractPunctaLabeler):
    def __init__(
        self,
        viewer: "Viewer",
        puncta_analyzer: "PunctaAnalyzer",
        labeling_method: Callable,
        parameters: dict[str, int | float],
    ):
        self.viewer = viewer
        self.puncta_analyzer = puncta_analyzer
        self.labeling_method = labeling_method
        self.parameters = parameters
        self.param_widgets: dict[str, QWidget] = defaultdict(QWidget)

    def label_puncta(
        self, image: np.ndarray, masks: np.ndarray | None, label_intensity: int
    ) -> np.ndarray:
        """
        Produces the array for a puncta labels layer using one of
        skimage's blob detection algorithms and adds it to the viewer's layer
        list.

        Parameters
        ----------
        image: np.ndarray
            Array of a image layer.

        masks: np.ndarray | None
            Array of a masks label layer. None indicates that the
            user has specified no masks.

        label_intensity: int
            The color of the puncta labels.

        Returns
        -------
        np.ndarray
            Array of a puncta labels layer.
        """

        blob_method_parameters = {
            param_name: self.cast_to_numericals(line_edit.text())
            for param_name, line_edit in self.param_widgets.items()
        }

        blob_coords = self.labeling_method(
            image=image, **blob_method_parameters
        )

        if masks is not None:
            spatial_coords = blob_coords[:, :-1].astype(np.uint16)
            sizes = blob_coords[:, -1]

            mask_labels = masks[tuple(spatial_coords.T)]
            matching_results = np.column_stack(
                (spatial_coords, sizes, mask_labels)
            )
            matching_results = matching_results[matching_results[:, -1] != 0]

            blob_coords = matching_results[:, :-1]

        blob_labels = self.create_labels_from_coords(
            img_shape=image.shape,
            points=blob_coords,
            label_intensity=label_intensity,
        )

        return blob_labels

    def initialize_widgets(self) -> QLayout:
        form_layout = QFormLayout()

        for param in self.parameters:
            label = QLabel(param)
            line_edit = QLineEdit()

            param_val = self.parameters[param]

            if isinstance(param_val, float):
                double_validator = QDoubleValidator()
                double_validator.setNotation(
                    QDoubleValidator.Notation.StandardNotation
                )
                line_edit.setValidator(double_validator)

            elif isinstance(param_val, int):
                int_validator = QIntValidator()
                line_edit.setValidator(int_validator)

            line_edit.setText(str(param_val))
            form_layout.addRow(label, line_edit)
            self.param_widgets[param] = line_edit

        form_layout.setSpacing(5)

        return form_layout

    def create_labels_from_coords(
        self, img_shape: tuple, points: np.ndarray, label_intensity: int
    ) -> np.ndarray:
        """
        Creates an array for the puncta labels layer from the coordinates of
        skimage's blob detection algorithm.

        Parameters
        ----------
        img_shape: tuple
            Dimensions of a user-specified image.

        points: np.ndarray
            Coordinates and radii of each punctum produced by skimage's blob
            detection algorithms.

        label_intensity: int
            User-specified color of the puncta labels.

        Returns
        -------
        np.ndarray
            Array of a puncta labels layer.
        """

        y_coords = []
        x_coords = []

        for point in points:
            y, x = disk(center=point[:-1], radius=point[-1], shape=img_shape)
            y_coords.append(y)
            x_coords.append(x)

        if len(x_coords) == 0:
            return np.array([])

        y_coords = np.concatenate(y_coords, axis=0)
        x_coords = np.concatenate(x_coords, axis=0)

        labels = np.zeros(shape=img_shape, dtype=np.uint16)
        labels[y_coords, x_coords] = label_intensity

        return labels

    def cast_to_numericals(self, parameter: str) -> int | float:
        parameter = parameter.strip()

        if parameter.isdigit():
            return int(parameter)
        elif "." in parameter:
            return float(parameter)
        else:
            raise ValueError("Invalid parameter type for blob labeler.")


class BlobDoGLabeler(SkimageBlobLabeler):
    def __init__(self, viewer: "Viewer", puncta_analyzer: "PunctaAnalyzer"):
        super().__init__(
            viewer=viewer,
            puncta_analyzer=puncta_analyzer,
            labeling_method=blob_dog,
            parameters={
                "min_sigma": 5,
                "max_sigma": 7,
                "sigma_ratio": 1.6,
                "threshold": 0.01,
                "overlap": 0.5,
            },
        )


class BlobDoHLabeler(SkimageBlobLabeler):
    def __init__(self, viewer: "Viewer", puncta_analyzer: "PunctaAnalyzer"):
        super().__init__(
            viewer=viewer,
            puncta_analyzer=puncta_analyzer,
            labeling_method=blob_doh,
            parameters={
                "min_sigma": 5,
                "max_sigma": 7,
                "num_sigma": 10,
                "threshold": 0.01,
                "overlap": 0.5,
            },
        )


class BlobLoGLabeler(SkimageBlobLabeler):
    def __init__(self, viewer: "Viewer", puncta_analyzer: "PunctaAnalyzer"):
        super().__init__(
            viewer=viewer,
            puncta_analyzer=puncta_analyzer,
            labeling_method=blob_log,
            parameters={
                "min_sigma": 5,
                "max_sigma": 7,
                "num_sigma": 10,
                "threshold": 0.01,
                "overlap": 0.5,
            },
        )


class RFCPunctaLabeler(AbstractPunctaLabeler):
    def __init__(self, viewer: "Viewer", puncta_analyzer: "PunctaAnalyzer"):
        self.viewer = viewer
        self.puncta_analyzer = puncta_analyzer
        self.model: Pipeline | None = None

    def label_puncta(
        self, image: np.ndarray, masks: np.ndarray | None, label_intensity: int
    ) -> np.ndarray:
        """
        Produces the array for a puncta labels layer using a random forest
        classifier (RFC) and adds it to the viewer's layer list.

        Parameters
        ----------
        image: np.ndarray
            Array of a image layer.

        masks: np.ndarray | None
            Array of a masks label layer. None indicates that the
            user has specified no masks.

        label_intensity: int
            The color of the puncta labels.

        Returns
        -------
        np.ndarray
            Array of a puncta labels layer.
        """

        if self.model is None:
            show_error("Please train the RFC before labeling.")
            return np.array([])

        puncta_label_int = int(self.puncta_line_edit.text())

        blob_labels = self.predict(img=image)
        blob_labels = np.where(
            blob_labels == puncta_label_int, label_intensity, 0
        )

        if masks is not None:
            blob_labels = np.where(masks > 0, blob_labels, 0)

        return blob_labels

    def initialize_widgets(self) -> QLayout:
        grid_layout = QGridLayout()

        annotation_selection_label = QLabel("Select annotated layer")
        self.annotation_combobox = QComboBox()
        self.annotation_combobox.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLength
        )
        self.annotation_combobox.setMinimumContentsLength(1)

        def label_only_filter(layer: "layers.Layer") -> bool:
            return type(layer).__name__ == "Labels"

        self.labeling_cbox_manager = ComboBoxManager(viewer=self.viewer)
        self.labeling_cbox_manager.register_combobox(
            combobox=self.annotation_combobox, filter_fn=label_only_filter
        )

        puncta_label = QLabel("puncta_label")
        self.puncta_line_edit = QLineEdit()
        self.puncta_line_edit.setValidator(QIntValidator())

        background_label = QLabel("background_label")
        self.background_line_edit = QLineEdit()
        self.background_line_edit.setValidator(QIntValidator())

        train_button = QPushButton("Train")
        train_button.setObjectName("train_button")
        train_button.clicked.connect(self.train_rfc)

        grid_layout.addWidget(annotation_selection_label, 0, 0, 1, 2)
        grid_layout.addWidget(self.annotation_combobox, 1, 0, 1, 2)
        grid_layout.addWidget(puncta_label, 2, 0)
        grid_layout.addWidget(self.puncta_line_edit, 2, 1)
        grid_layout.addWidget(background_label, 3, 0)
        grid_layout.addWidget(self.background_line_edit, 3, 1)
        grid_layout.addWidget(train_button, 4, 0, 1, 2)

        grid_layout.setSpacing(5)

        return grid_layout

    def train_rfc(self) -> None:
        """
        Extracts ilastik-like features from a user-specified image and trains an RFC.
        """

        layer = self.puncta_analyzer.img_combobox.currentData()

        if layer is None:
            show_error("Please provide an image layer.")
            return

        annotation_name = self.annotation_combobox.currentText()
        annotation_layer = self.viewer.layers[annotation_name]

        if annotation_layer is None:
            show_error("Please provide an annotated labels layer.")
            return

        annotations = np.unique(annotation_layer.data)

        has_zero_and_two_labels = 0 in annotations and len(annotations) == 3

        if not has_zero_and_two_labels:
            show_error("Provided annotation should have only two labels.")
            return

        puncta_label_int = int(self.puncta_line_edit.text())
        background_label_int = int(self.background_line_edit.text())

        labels_in_annotations = (puncta_label_int in annotations) & (
            background_label_int in annotations
        )

        if not labels_in_annotations:
            show_error(
                "One or more specified labels are not found in the annotation layer."
            )
            return

        img = layer.data.copy()
        img_feats_df = self.extract_ilastish_features(
            img=img, annotation_layer=annotation_layer.data
        )

        self.train_seg_model(annotation_df=img_feats_df)

        show_info("Training complete.")

    def extract_ilastish_features(
        self,
        img: np.ndarray,
        annotation_layer: np.ndarray,
    ) -> pd.DataFrame:
        """
        Creates a dataframe of ilastik-like features as inputs for an RFC.

        Parameters
        ----------
        img: np.ndarray
            Array of a user-specified image.

        annotation_layer: np.ndarray
            User-provided annotations.

        Returns
        -------
        pd.DataFrame
            ilastik-like features.
        """

        feature_labels, feature_data = self.preprocess_image(img=img)
        nonzero_indices = np.nonzero(annotation_layer)
        labels = annotation_layer[nonzero_indices]
        labelled_features = feature_data[nonzero_indices]

        rows = []

        for label, features in zip(labels, labelled_features, strict=False):
            row = {f: features[i] for i, f in enumerate(feature_labels)}
            row["label"] = label
            rows.append(row)

        return pd.DataFrame.from_records(rows)

    def preprocess_image(self, img: np.ndarray) -> tuple[list, np.ndarray]:
        """
        Processes an image using adaptive histogram equalization and wavelet
        denoising and creates a stack of features.

        Parameters
        ----------
        img: np.ndarray
            Array of a user-specified image.

        Returns
        -------
        tuple[list, np.ndarray]
            Feature names and values.

        """

        sigmas = [0.7, 1, 3.5]

        rescaled_float = exposure.rescale_intensity(img, out_range=float)
        eqd = equalize_adapthist(rescaled_float, clip_limit=0.05)
        denoised = denoise_wavelet(eqd)

        gaussian_stack = [
            (f"gaussian-{s}", filters.gaussian(denoised, sigma=s))
            for s in sigmas
        ]
        log_stack = [
            (f"LoG-{s}", filters.laplace(g[1]))
            for s, g in zip(sigmas[1:], gaussian_stack[1:], strict=False)
        ]
        gg_mag_stack = [
            (f"sobel-{s}", filters.sobel(g[1]))
            for s, g in zip(sigmas[1:], gaussian_stack[1:], strict=False)
        ]
        hessian_stack = [
            hessian_matrix(
                img, sigma=s, mode="nearest", use_gaussian_derivatives=False
            )
            for s in sigmas[1:]
        ]
        hessian_eig_stack = [
            (f"hess_eig-{s}", hessian_matrix_eigvals(hess)[0])
            for s, hess in zip(sigmas, hessian_stack, strict=False)
        ]

        feature_stack = (
            gaussian_stack + log_stack + gg_mag_stack + hessian_eig_stack
        )

        feature_labels = [f[0] for f in feature_stack]
        feature_data = np.stack([f[1] for f in feature_stack], axis=-1)

        return feature_labels, feature_data

    def train_seg_model(self, annotation_df: pd.DataFrame) -> None:
        """
        Fits an RFC using image features and user-provided annotations.

        Parameters
        ----------
        annotation_df: pd.DataFrame
            Contains columns of features and labels.

        """

        y = annotation_df["label"]
        X = annotation_df.drop(columns=["label"])

        model = make_pipeline(StandardScaler(), RandomForestClassifier())
        model.fit(X, y)

        self.model = model

    def predict(self, img: np.ndarray) -> np.ndarray | None:
        """
        Produces puncta labels for the entire image using a trained RFC.

        Parameters
        ----------
        img: np.ndarray
            Array of a user-specified image.
        """

        img_feats_df = self.extract_ilastish_features(img, np.ones(img.shape))
        img_feats_df = img_feats_df.drop(columns=["label"])

        if self.model is None:
            return None

        predicted_labels = self.model.predict(img_feats_df).reshape(img.shape)

        return predicted_labels
