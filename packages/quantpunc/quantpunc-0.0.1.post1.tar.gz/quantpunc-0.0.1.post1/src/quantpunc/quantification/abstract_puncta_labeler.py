from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
from qtpy.QtWidgets import QLayout

if TYPE_CHECKING:
    from napari import Viewer

    from quantpunc.quantification.puncta_analyzer import PunctaAnalyzer


class AbstractPunctaLabeler(ABC):
    @abstractmethod
    def __init__(self, viewer: "Viewer", puncta_analyzer: "PunctaAnalyzer"):
        """Labeler class must be passed a viewer instance and puncta analyzer widget."""
        self.viewer = viewer
        self.auto_counter = puncta_analyzer

    @abstractmethod
    def label_puncta(
        self, image: np.ndarray, masks: np.ndarray | None, label_intensity: int
    ) -> np.ndarray:
        """Labeling function should account for the case where the user provides no masks.
        Returns a binary puncta image with 0 as background. Return an empty numpy array to produce no labels."""

    @abstractmethod
    def initialize_widgets(self) -> QLayout:
        """Returns a layout with widgets that will be used to parameterize the puncta labeler."""
