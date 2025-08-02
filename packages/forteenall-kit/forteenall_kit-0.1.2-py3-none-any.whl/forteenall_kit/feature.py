# This file is auto-generated. Do not edit manually.
# For upadte this file pls run 'bash update.sh' on main forteenall project

# Main imports
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forteenall_kit.invoke import Invoker
    from forteenall_kit.space import SpaceProject

# Invokers import
from forteenall_kit.invokers.spaceDup import Feature as Feature_spaceDup

class FeatureManager:
    def __init__(self):
        self.features = {
          'spaceDup': Feature_spaceDup
        }
        self.spaces: dict[str, SpaceProject] = {}
        self.executed = set()

    def execute(self, feature_name: str, **params):
        '''
        this function run invokers.
        Args:
            feature_name (str): name of feature
        '''


