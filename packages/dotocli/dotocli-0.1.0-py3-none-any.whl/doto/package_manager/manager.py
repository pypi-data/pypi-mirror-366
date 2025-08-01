"""Package Manager Module."""

import typer

from doto.package_manager._apt import AptPackageManager
from doto.package_manager.base_package_manager import BasePackageManager, Package

app = typer.Typer(name="package", no_args_is_help=False, help="Manage packages from different sources")


class PackageManager:
    """The main package manager class that acts as a context."""

    def __init__(self, source: str) -> None:
        """Initialize the PackageManager with a specified source."""
        self._managers: dict[str, BasePackageManager] = {"apt": AptPackageManager()}
        if source.lower() not in self._managers:
            err = f"Unknown package source: '{source}'. Available sources: {list(self._managers.keys())}"
            raise ValueError(err)
        self.source = source
        self.manager = self._get_manager(self.source)

    def _get_manager(self, source: str) -> BasePackageManager:
        """Get the correct package manager instance."""
        manager = self._managers.get(source.lower())
        if not manager:
            err = f"Unknown package source: '{source}'. Available sources: {list(self._managers.keys())}"
            raise ValueError(err)
        return manager

    def search(self, query: str) -> Package | None:
        """Search for packages using the specified or default manager."""
        return self.manager.search(query)

    def get(self, package_name: str, source: str) -> Package:
        """Get a package by name using the specified or default manager."""
        manager = self._get_manager(source)
        result = manager.search(package_name)
        if not result:
            err = f"Package '{package_name}' not found."
            raise ValueError(err)
        return result

    def install(self, package_name: str) -> bool:
        """Installs a package using the specified or default manager."""
        return self.manager.install(package_name)

    def remove(self, package_name: str, source: str) -> bool:
        """Remove a package using the specified or default manager."""
        manager = self._get_manager(source)
        return manager.remove(package_name)

    def update(self) -> bool:
        """Update package lists/repositories using the specified or default manager."""
        return self.manager.update()

    def upgrade(self, package_name: str, source: str) -> bool:
        """Upgrades packages using the specified or default manager."""
        manager = self._get_manager(source)
        return manager.upgrade(package_name)


@app.command()
def add(name: str, source: str) -> None:
    """Add a package to the specified source."""
    print(f"Adding package '{name}' to source '{source or 'default'}'...")
    manager = PackageManager(source)
    package = manager.get(name, source)
    print(f"Found Package {package.name}: {package.version}")
