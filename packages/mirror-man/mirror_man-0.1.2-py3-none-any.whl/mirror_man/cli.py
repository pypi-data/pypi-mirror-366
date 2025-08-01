#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typer
import shutil
from datetime import datetime
from mirror_man.mirror_data import apt_sources
import subprocess

from .version import __version__


app = typer.Typer()


def version_callback(value: bool):
    if value:
        # Simple and direct way to print version, leveraging __main__.py's unbuffered output
        print(f"mirror-man version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    ),
):
    """
    A command-line tool to manage mirror sources.
    """
    pass


def get_os_release():
    """Get the current operating system."""
    try:
        with open("/etc/os-release") as f:
            os_info = f.read()
        for line in os_info.splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=")[1].strip('"')
    except FileNotFoundError:
        return "Unknown OS"
    return "Unknown OS"


def backup(file_path: str):
    """Backup the current sources."""
    try:
        backup_path = f"{file_path}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy(file_path, backup_path)
        print(f"Backup created at {backup_path}")
    except Exception as e:
        print(f"Failed to create backup for {file_path}: {e}")
        raise


def set_apt_sources(source: str):
    """Set the apt sources to the specified source."""
    file_path = "/etc/apt/sources.list"
    backup(file_path)
    try:
        with open(file_path, "w") as f:
            f.write(source)
        print(f"APT sources updated.")
    except Exception as e:
        print(f"Failed to update APT sources: {e}")
        raise


def set_yum_repos(base_repo_url: str, epel_repo_url: str):
    """Set the yum repositories to the specified repos."""
    base_repo_path = "/etc/yum.repos.d/CentOS-Base.repo"
    epel_repo_path = "/etc/yum.repos.d/epel.repo"

    backup(base_repo_path)
    backup(epel_repo_path)

    # Download the new repo files
    try:
        cmd_base = f"curl -o {base_repo_path} {base_repo_url}"
        cmd_epel = f"curl -o {epel_repo_path} {epel_repo_url}"
        subprocess.run(cmd_base, shell=True, check=True)
        subprocess.run(cmd_epel, shell=True, check=True)

        # Clean up Aliyun-specific placeholders if they exist
        cmd_clean = f"sed -i -e '/mirrors.cloud.aliyuncs.com/d' -e '/mirrors.aliyuncs.com/d' {base_repo_path}"
        subprocess.run(
            cmd_clean, shell=True, check=False
        )  # check=False as it might fail if patterns are not found

        # Clean and makecache
        cmd_yum = "yum clean all && yum makecache"
        subprocess.run(cmd_yum, shell=True, check=True)
        print("YUM repositories updated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update YUM repositories: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while updating YUM repositories: {e}")
        raise


@app.command()
def aliyun():
    """Switch to Aliyun mirror sources."""
    os_release = get_os_release()

    if os_release.startswith("Ubuntu"):
        # Map Ubuntu version to the key in apt_sources
        os_key = os_release.lower().replace(" ", "_").replace(".", "")[:11]

        if os_key in apt_sources:
            try:
                set_apt_sources(apt_sources[os_key])
                print(f"Successfully switched to Aliyun mirror for {os_release}.")
            except Exception as e:
                print(f"Failed to switch to Aliyun mirror for {os_release}: {e}")
        else:
            print(f"Aliyun mirror source not found for {os_release}.")
    elif os_release.startswith("CentOS"):
        # Assuming CentOS 7 for now, as per original logic
        # In the future, this could be made more dynamic based on os info
        base_repo_url = "https://mirrors.aliyun.com/repo/Centos-7.repo"
        epel_repo_url = "https://mirrors.aliyun.com/repo/epel-7.repo"
        try:
            set_yum_repos(base_repo_url, epel_repo_url)
            print(f"Successfully switched to Aliyun mirror for {os_release}.")
        except Exception as e:
            print(f"Failed to switch to Aliyun mirror for {os_release}: {e}")
    else:
        print(f"Unsupported operating system: {os_release}")


if __name__ == "__main__":
    app()
