from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType
from typing import List

class FuelSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.FUEL)

    def get_setup_commands(self) -> List[List[str]]:
        raise NotImplementedError("Not implemented")
    
    def get_routes_command(self) -> List[str]:
        raise NotImplementedError("Not implemented")