import subprocess
import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PackageStatus(Enum):
    INSTALLED = "installed"
    OUTDATED = "outdated"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"


@dataclass
class Package:
    name: str
    version: Optional[str] = None
    latest_version: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    requires: Optional[List[str]] = None
    required_by: Optional[List[str]] = None
    status: PackageStatus = PackageStatus.UNKNOWN

    @property
    def status_symbol(self) -> str:
        return {
            PackageStatus.INSTALLED: "✓",
            PackageStatus.OUTDATED: "↑",
            PackageStatus.NOT_INSTALLED: "✗",
            PackageStatus.UNKNOWN: "?"
        }[self.status]


class PipAPI:
    """Wrapper for pip commands with proper error handling and parsing."""

    def __init__(self):
        self._cache = {}
        self._cache_valid = False

    def _run_pip_command(self, args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a pip command and return the result."""
        cmd = ["pip"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False  # We'll handle errors manually
            )
            return result
        except FileNotFoundError:
            raise RuntimeError("pip command not found. Please ensure pip is installed.")

    def list_installed(self, refresh: bool = False) -> List[Package]:
        """Get list of installed packages."""
        if not refresh and self._cache_valid and 'installed' in self._cache:
            return self._cache['installed']

        result = self._run_pip_command(["list", "--format=json"])
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list packages: {result.stderr}")

        packages = []
        try:
            data = json.loads(result.stdout)
            for item in data:
                package = Package(
                    name=item["name"],
                    version=item["version"],
                    status=PackageStatus.INSTALLED
                )
                packages.append(package)
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse pip list output")

        self._cache['installed'] = packages
        self._cache_valid = True
        return packages

    def list_outdated(self, refresh: bool = False) -> List[Package]:
        """Get list of outdated packages."""
        if not refresh and self._cache_valid and 'outdated' in self._cache:
            return self._cache['outdated']

        result = self._run_pip_command(["list", "--outdated", "--format=json"])
        if result.returncode != 0:
            # Not necessarily an error - might just be no outdated packages
            self._cache['outdated'] = []
            return []

        packages = []
        try:
            data = json.loads(result.stdout)
            for item in data:
                package = Package(
                    name=item["name"],
                    version=item["version"],
                    latest_version=item["latest_version"],
                    status=PackageStatus.OUTDATED
                )
                packages.append(package)
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse pip outdated output")

        self._cache['outdated'] = packages
        return packages

    def show_package(self, package_name: str) -> Optional[Package]:
        """Get detailed information about a specific package."""
        result = self._run_pip_command(["show", package_name])
        if result.returncode != 0:
            return None

        # Parse pip show output
        data = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().lower()] = value.strip()

        # Parse requires and required-by
        requires = []
        if 'requires' in data and data['requires']:
            requires = [req.strip() for req in data['requires'].split(',')]

        required_by = []
        if 'required-by' in data and data['required-by']:
            required_by = [req.strip() for req in data['required-by'].split(',')]

        # Determine status
        status = PackageStatus.INSTALLED
        outdated_packages = {pkg.name.lower(): pkg for pkg in self.list_outdated()}
        if package_name.lower() in outdated_packages:
            status = PackageStatus.OUTDATED

        return Package(
            name=data.get('name', package_name),
            version=data.get('version'),
            summary=data.get('summary'),
            location=data.get('location'),
            requires=requires if requires else None,
            required_by=required_by if required_by else None,
            status=status
        )

    def install_package(self, package_name: str, upgrade: bool = False) -> Tuple[bool, str]:
        """Install a package. Returns (success, output)."""
        args = ["install"]
        if upgrade:
            args.append("--upgrade")
        args.append(package_name)

        result = self._run_pip_command(args)
        self._invalidate_cache()

        return result.returncode == 0, result.stdout + result.stderr

    def uninstall_package(self, package_name: str, yes: bool = True) -> Tuple[bool, str]:
        """Uninstall a package. Returns (success, output)."""
        args = ["uninstall"]
        if yes:
            args.append("-y")
        args.append(package_name)

        result = self._run_pip_command(args)
        self._invalidate_cache()

        return result.returncode == 0, result.stdout + result.stderr

    def upgrade_package(self, package_name: str) -> Tuple[bool, str]:
        """Upgrade a specific package. Returns (success, output)."""
        return self.install_package(package_name, upgrade=True)

    def upgrade_all(self) -> Tuple[bool, str]:
        """Upgrade all outdated packages. Returns (success, output)."""
        outdated = self.list_outdated()
        if not outdated:
            return True, "No packages to upgrade"

        all_output = []
        all_success = True

        for package in outdated:
            success, output = self.upgrade_package(package.name)
            all_output.append(f"Upgrading {package.name}: {'SUCCESS' if success else 'FAILED'}")
            all_output.append(output)
            if not success:
                all_success = False

        return all_success, "\n".join(all_output)

    def freeze(self) -> List[str]:
        """Get pip freeze output as list of requirement strings."""
        result = self._run_pip_command(["freeze"])
        if result.returncode != 0:
            raise RuntimeError(f"Failed to freeze packages: {result.stderr}")

        return [line.strip() for line in result.stdout.split('\n') if line.strip()]

    def install_from_requirements(self, requirements_file: str) -> Tuple[bool, str]:
        """Install packages from requirements file. Returns (success, output)."""
        result = self._run_pip_command(["install", "-r", requirements_file])
        self._invalidate_cache()

        return result.returncode == 0, result.stdout + result.stderr

    def search_packages(self, query: str) -> List[Dict[str, str]]:
        """Search for packages (using PyPI API since pip search is deprecated)."""
        try:
            import requests
            response = requests.get(f"https://pypi.org/pypi/{query}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [{
                    'name': data['info']['name'],
                    'summary': data['info']['summary'],
                    'version': data['info']['version']
                }]
        except:
            pass

        # Fallback: simple search via PyPI simple API
        try:
            import requests
            response = requests.get(f"https://pypi.org/simple/", timeout=10)
            if response.status_code == 200:
                # This is a very basic search - in a real implementation you'd want
                # to use the proper PyPI search API or a third-party service
                content = response.text.lower()
                if query.lower() in content:
                    return [{'name': query, 'summary': 'Package found on PyPI', 'version': 'unknown'}]
        except:
            pass

        return []

    def check_package_exists(self, package_name: str) -> bool:
        """Check if a package exists on PyPI."""
        try:
            import requests
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_package_info_from_pypi(self, package_name: str) -> Optional[Dict]:
        """Get package information from PyPI."""
        try:
            import requests
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def _invalidate_cache(self):
        """Invalidate the internal cache."""
        self._cache.clear()
        self._cache_valid = False

    def refresh_cache(self):
        """Refresh all cached data."""
        self._invalidate_cache()
        self.list_installed(refresh=True)
        self.list_outdated(refresh=True)
