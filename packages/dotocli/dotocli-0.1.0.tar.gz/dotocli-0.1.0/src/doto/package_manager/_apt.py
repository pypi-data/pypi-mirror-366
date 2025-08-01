# https://apt-team.pages.debian.net/python-apt/contents.html
# https://salsa.debian.org/apt-team/python-apt

import apt.cache
import apt.progress
import apt.progress.base

from doto.package_manager.base_package_manager import BasePackageManager, Package


class AptPackageManager(BasePackageManager):
    """Concrete implementation for managing APT packages.

    In a real application, this would execute `apt` or `apt-get` commands.
    """

    def search(self, query: str) -> Package | None:
        """Search for a package in the APT cache.

        Args:
            query (str): The name of the package to search for.

        Returns:
            Package: A Package object if found, otherwise None.

        """
        print(f"Searching APT for: '{query}'")

        cache = apt.Cache()
        pkg = cache.get(query, None)
        if pkg is None:
            print(f"Package '{query}' not found in APT cache.")
            return None

        _version = pkg.candidate.version if pkg.candidate.version is not None else "Unknown"
        _desc = pkg.candidate.summary if pkg.candidate.summary is not None else "No description available"
        return Package(name=pkg.name, version=_version, description=_desc, installed=pkg.is_installed)

    def get(self, query: str) -> Package | None:
        """Get package information for a given query.

        Args:
            query (str): The name of the package to get information for.

        Returns:
            Package: A Package object with the package information.

        """
        print(f"Get APT package information for: '{query}'")
        return self.search(query)

    def install(self, package_name: str) -> bool:
        """Install an APT package.

        Args:
            package_name (str): The name of the package to install.

        Returns:
            bool: True if the installation was successful or the package is already installed, False otherwise.

        """
        print(f"Installing APT package: '{package_name}'")
        # https://github.com/excid3/python-apt/blob/master/doc/examples/inst.py
        cache = apt.Cache(apt.progress.base.OpProgress())
        pkg = cache.get(package_name)
        if pkg is None:
            err = f"Package '{package_name}' not found in APT cache."
            raise ValueError(err)
        if pkg.is_installed:
            print(f"Package '{package_name}' is already installed.")
            return True
        pkg.mark_install()
        progress = apt.progress.base.AcquireProgress()
        install_progress = apt.progress.base.InstallProgress()
        allow_unauthenticated = False
        cache.commit(progress, install_progress, allow_unauthenticated)
        print(f"Package '{package_name}' installed successfully.")
        return True  # Simulate success

    def remove(self, package_name: str) -> bool:
        """Remove an APT package.

        Args:
            package_name (str): The name of the package to remove.

        Returns:
            bool: True if the removal was successful, False otherwise.

        """
        print(f"Removing APT package: '{package_name}'")
        return True  # Simulate success

    def update(self) -> bool:
        """Install an APT package.

        Args:
            package_name (str): The name of the package to install.

        Returns:
            bool: True if the installation was successful or the package is already installed, False otherwise.

        """
        print("Updating APT package lists...")

        cache = apt.Cache()
        acquire = apt.progress.base.AcquireProgress()
        try:
            result = cache.update(fetch_progress=acquire, pulse_interval=0, raise_on_error=True, sources_list=None)
        except apt.cache.FetchFailedException as e:
            print(f"Failed to update APT cache: {e}")
            return False
        if result is True:
            cache.open()
            cache.commit()
        # Cast result to bool for consistency
        # According to the docs it should be an int but a bool is returned
        # Satisfy mypy
        return bool(result)

    def upgrade(self, package_name: str | None = None) -> bool:
        """Upgrade given package.

        Args:
            package_name (Optional[str], optional): _description_. Defaults to None.

        Returns:
            bool: _description_

        """
        if package_name:
            print(f"Upgrading APT package: '{package_name}'")
            # Example: `subprocess.run(["sudo", "apt", "install", "--only-upgrade", "-y", package_name])`
        else:
            print("Upgrading all APT packages...")
            # Example: `subprocess.run(["sudo", "apt", "upgrade", "-y"])`
        return True  # Simulate success
