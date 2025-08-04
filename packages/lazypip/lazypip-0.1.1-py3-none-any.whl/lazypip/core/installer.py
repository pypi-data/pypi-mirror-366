def install_package(package_name: str):
    import subprocess
    subprocess.run(["python", "-m", "pip", "install", package_name])


def upgrade_package(package_name: str):
    import subprocess
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", package_name])

