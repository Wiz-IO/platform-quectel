# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel

from platform import system
from platformio.managers.platform import PlatformBase

class QuectelPlatform(PlatformBase):
    def configure_default_packages(self, variables, targets):
        framework = variables.get("pioframework", [])
        if variables["board"].startswith('ec2'):
            del self.packages["toolchain-gccarmnoneeabi"]
        else:
            del self.packages["toolchain-gcc-ec2x"]
        return PlatformBase.configure_default_packages(self, variables, targets)