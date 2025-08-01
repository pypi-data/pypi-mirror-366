# doto

Dotfiles management with Python and Ansible
This tool aims to be `poetry` for `Ubuntu`.
It helps maintaing a manifest file that keeps track of the packages and other setting to apply to a system.

Similar to `poetry` you can run `doto add [package]` which will add the package to the manifest file and install it.

The backend for the first version will be `Ansible` but with an abstaraction layer to be able to replace it in the future.

## Features

- Manage packages from different sources
- Manage hosts
  - This allows you to add package to a specific host. For example if you have a workstation and a laptop you might want to apply different settings and packages.
- Add comments to package entries in the Manifest file.
- CLI to manage and view manifest file.
- Sync the manifest to a remote repository via `Git`
- Besides packages one can also choose to add and apply an `Ansible Role` which is maintained and tested in a separate repository.

- Testing and Dry run. By using the test tools available for `Ansible` one can add a package in a dry-run and create a VM to apply the new manifest to verify that the outcome is a expected.
Command could be `doto deploy host`

Future:
- The tool manages a local manifest file on each host to avoid to keep track of packages that are already installed.



## Data Structures

Overview of Data Structures:

- Manifest file
  - Hosts

- Host
  - Name
  - Platform
    - rpi
    - vm
    - x86
    - arm

  - Tags:
    - coding
    - workstation
    - laptop
    - video_editing
  - Packages

Packages don't require any configuration besides installing them.

- Package
  - name
  - version
  - comment

### Commands

`doto add [package]`
will check the available package managers for the package and ask which source to select.
A default can be set or the option `--package-manager` can be provided

- apt
- appimage
  - Github release page
- Flatpak
- Snap
- pypi

## Development

`docker build -t doto-ci .`
`docker run --rm -v $PWD:/workspaces/doto -w /workspaces/doto doto-ci bash -c 'poetry run inv python.ci'`
`docker run --rm -v $PWD:/workspaces/doto -w /workspaces/doto --user $(id -u):$(id -g) doto-ci bash -c 'poetry run inv python.ci'`

### Setup for development

## Ansible

Running ansible playbook

```bash
cd ansible
ansible-galaxy install -r requirements.yml
ansible-playbook -i inventory main.yml
```

## Vagrant

## VirtualBox

```bash
VBoxManage list runningvms | cut -d '"' -f 2 | xargs -I {} VBoxManage controlvm {} poweroff soft && VBoxManage list vms | cut -d '"' -f 2 | xargs -I {} VBoxManage unregistervm {} --delete
```

## TODO

- 2024-03-10:
  - Create PR:
    - <https://github.com/ansible/molecule/discussions/3914>
    - geerlingguy ansible playbook testing
  - Have a dir with shared molecule files like prepare.yml

- 2024-02-22:
  - molecule test does not create a box, I have to run molecule converge first.
  - virtulabox got installed and was signed automatically, need to figure out why. dpkg package?
