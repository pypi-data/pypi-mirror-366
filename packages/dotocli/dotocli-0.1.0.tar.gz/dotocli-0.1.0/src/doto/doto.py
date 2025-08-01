"""Doto package management tool.

Contains the main Doto class.
"""

import socket
from pathlib import Path

import typer
from platformdirs import PlatformDirs
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str

from doto.package_manager.base_package_manager import Package

app_host = typer.Typer(name="host", no_args_is_help=False, help="Manage hosts")


class Tag(BaseModel):
    """Represents a tag."""

    name: str


class PackageList(BaseModel):
    """Represents a list of packages."""

    source: str
    packages: list[Package]


class Host(BaseModel):
    """Represents a host."""

    name: str
    tags: list[Tag] = []
    packages: PackageList


class Manifest(BaseModel):
    """Represents a manifest."""

    version: str = "1.0"  # Version of the manifest format
    hosts: list[Host]


class Doto:
    """Represents the Doto application."""

    def __init__(self) -> None:
        """Initialize the Doto class."""
        self.app_name = "doto"
        self.app_author = "doto"
        self.dirs = PlatformDirs(self.app_name, self.app_author)
        self.manifest_path = self.dirs.user_data_path / "manifest.yaml"
        self.manifest = self._load_manifest()
        self.host = socket.gethostname()

    def _load_manifest(self) -> Manifest:
        """Load the manifest from the file."""
        if self.manifest_path.exists() is False:
            print(f"Manifest file does not exist at: {self.manifest_path}")
            return Manifest(hosts=[])
        return parse_yaml_raw_as(Manifest, self.manifest_path.read_text())

    def _save_manifest(self) -> None:
        """Save the manifest to the file."""
        manifest_str = to_yaml_str(self.manifest)
        self.manifest_path.write_text(manifest_str)
        print(f"Manifest saved to: {self.manifest_path}")

    def init(self) -> bool:
        """Initialize the Doto application."""
        if self.dirs.user_data_path.exists() is False:
            self.dirs.user_data_path.mkdir(parents=True, exist_ok=True)
            print(f"Manifest directory created at: {self.dirs.user_data_dir}")
            self.add_host(self.host)
            self._save_manifest()
        else:
            print(f"Manifest directory already exists at: {self.dirs.user_data_dir}")
        return True

    def add_host(self, name: str) -> None:
        """Add a host to the manifest."""
        for host in self.manifest.hosts:
            if host.name == name:
                print(f"Host '{name}' already exists in the manifest.")
                return
        host = Host(name=name, packages=PackageList(source="apt", packages=[]))
        self.manifest.hosts.append(host)
        self._save_manifest()
        print(f"Host '{name}' added to the manifest.")


@app_host.command()
def add(name: str) -> None:
    """Add a host to the manifest."""
    doto = Doto()
    doto.add_host(name)
