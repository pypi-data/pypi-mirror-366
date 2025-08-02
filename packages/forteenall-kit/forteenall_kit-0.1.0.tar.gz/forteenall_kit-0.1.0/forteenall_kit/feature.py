from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forteenall_kit.invoke import Invoker
    from forteenall_kit.space import SpaceProject


class FeatureManager:
    def __init__(self):
        self.features: dict[str, Invoker] = {}
        self.spaces: dict[str, SpaceProject] = {}
        self.executed = set()

    def execute(self, feature_name: str, **params):
        """
        this function run invokers.
        Args:
            feature_name (str): name of feature
        """
