from pip._internal import main as pipmain

if __name__ == "__main__":
    with open("requirements.txt") as requirements:
        for package in requirements.readlines():
            pipmain(["install", "-t", "../../packages/site-packages/", package])
