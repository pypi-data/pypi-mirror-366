"""Base Package Manager Module.

This module defines the abstract base class for package managers.
Concrete implementations should inherit from this class and implement its methods.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class Package(BaseModel):
    """Represents a package."""

    name: str
    version: str
    description: str
    installed: bool


class BasePackageManager(ABC):
    """Abstract Base Class defining the common interface for all package managers.

    All concrete package manager implementations must inherit from this class
    and implement its abstract methods.
    """

    @abstractmethod
    def search(self, query: str) -> Package | None:
        """Search for packages matching the given query.

        Args:
            query (str): The search term for packages.

        Returns:
            List[Package]: A list of Package objects that match the search query.

        """
        pass

    @abstractmethod
    def install(self, package_name: str) -> bool:
        """Installs a specified package.

        Args:
            package_name (str): The name of the package to install.

        Returns:
            bool: True if the installation was successful, False otherwise.

        """
        pass

    @abstractmethod
    def remove(self, package_name: str) -> bool:
        """Remove a specified package.

        Args:
            package_name (str): The name of the package to remove.

        Returns:
            bool: True if the removal was successful, False otherwise.

        """
        pass

    @abstractmethod
    def update(self) -> bool:
        """Update the package lists/repositories for this package manager.

        (e.g., `apt update` for APT, refresh snap metadata).

        Returns:
            bool: True if the update was successful, False otherwise.

        """
        pass

    @abstractmethod
    def upgrade(self, package_name: str | None = None) -> bool:
        """Upgrades a specific package or all upgradable packages.

        Args:
            package_name (Optional[str]): The name of the package to upgrade.
                                          If None, all upgradable packages are upgraded.

        Returns:
            bool: True if the upgrade was successful, False otherwise.

        """
        pass
