# -*- coding: utf-8 -*-
from typing import Iterable, ClassVar

from .actions import GenerateCertAction, RemoveCertAction, GenerateSignerCertificateAction
from .schema import CertsSchema
from ..feature import Feature
from ..schema import FeatureSchema
from ...action import Action


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
