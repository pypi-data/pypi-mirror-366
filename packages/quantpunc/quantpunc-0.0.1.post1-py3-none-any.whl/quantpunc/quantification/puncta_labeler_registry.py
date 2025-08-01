from typing import Type

from quantpunc.quantification.default_puncta_labelers import (
    AbstractPunctaLabeler,
    BlobDoGLabeler,
    BlobDoHLabeler,
    BlobLoGLabeler,
    RFCPunctaLabeler,
)

PUNCTA_LABELER_REGISTRY: dict[str, Type[AbstractPunctaLabeler]] = {}


def register_puncta_labeler(
    name: str, cls: Type[AbstractPunctaLabeler]
) -> None:
    PUNCTA_LABELER_REGISTRY[name] = cls


def register_default_puncta_labelers() -> None:
    register_puncta_labeler("Random Forest Classifier", RFCPunctaLabeler)
    register_puncta_labeler("Laplacian of Gaussian", BlobLoGLabeler)
    register_puncta_labeler("Determinant of Hessian", BlobDoHLabeler)
    register_puncta_labeler("Difference of Gaussians", BlobDoGLabeler)
