from pip._internal import main as pipmain
import sys
import platform

if __name__ == "__main__":
    # make sure we're running same python version as SP
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 6
    assert sys.version_info.micro == 1
    assert platform.architecture()[0] == "32bit"

    with open("requirements.txt") as requirements:
        pipmain(
            [
                "install",
                "-t",
                "../../packages/site-packages/",
                *requirements.readlines(),
            ]
        )
