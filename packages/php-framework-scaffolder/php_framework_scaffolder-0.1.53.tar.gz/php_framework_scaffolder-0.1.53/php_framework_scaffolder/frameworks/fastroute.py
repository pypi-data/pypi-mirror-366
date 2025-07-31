from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType
from typing import List

class FastRouteSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.FASTROUTE)

    def get_setup_commands(self) -> List[List[str]]:
        raise NotImplementedError("Not implemented")
    
    def get_routes_command(self) -> List[str]:
        raise NotImplementedError("Not implemented")