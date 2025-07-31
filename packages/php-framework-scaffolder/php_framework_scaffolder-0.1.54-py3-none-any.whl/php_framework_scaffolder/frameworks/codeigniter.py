from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType
from typing import List


class CodeIgniterSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.CODEIGNITER)

    def get_setup_commands(self) -> List[List[str]]:
        return [
            [
                "docker",
                "compose",
                "exec",
                "-w",
                "/app",
                "app",
                "php",
                "spark",
                "migrate",
                "--no-interaction",
                "--no-ansi",
            ]
        ]
    

    def get_routes_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "exec",
            "-w",
            "/app",
            "app",
            "php",
            "scripts/dump-routes.php",
        ]
