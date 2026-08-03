from collections.abc import Iterable
from typing import ClassVar

from ...action import Action
from ..feature import Feature
from ..schema import FeatureSchema
from .actions import GenerateCertAction, GenerateSignerCertificateAction, RemoveCertAction
from .schema import CertsSchema


class CertsFeature(Feature):
    """
    Generate SSL certificates for your project.
    """

    @property
    def name(self) -> str:
        return "certs"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        return CertsSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (
            GenerateCertAction(),
            RemoveCertAction(),
            GenerateSignerCertificateAction()
        )
