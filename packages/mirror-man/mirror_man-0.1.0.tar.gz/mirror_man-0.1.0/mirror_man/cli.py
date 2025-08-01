import typer
import shutil
from datetime import datetime
from mirror_man.mirror_data import apt_sources
import subprocess


app = typer.Typer()
__VERSION__ = "0.1.0"


def version_callback(value: bool):
    if value:
        typer.echo(__VERSION__)


def get_os():
    """Get the current operating system."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    for line in os_info.splitlines():
        if line.startswith("PRETTY_NAME="):
            return line.split("=")[1].strip('"')


def backup(file_path: str):
    """Backup the current apt sources."""
    backup_path = f"{file_path}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
    shutil.copy(file_path, backup_path)
    print(f"Backup created at {backup_path}")


def set_apt_sources(source: str):
    """Set the apt sources to the specified source."""
    file_path = "/etc/apt/sources.list"
    backup(file_path)
    with open(file_path, "w") as f:
        f.write(source)


def set_yum_repos():
    """Set the yum repositories to the specified repo."""
    backup("/etc/yum.repos.d/CentOS-Base.repo")
    backup("/etc/yum.repos.d/epel.repo")
    # Assuming the CentOS 7 repo is being set up
    # This is a placeholder command; adjust as necessary for your environment
    # The actual command to set up the repo may vary based on your requirements
    # Here we use a command to download the repo file from Aliyun
    # and clean the yum cache
    # Note: Ensure you have the necessary permissions to run this command
    # and that the URLs are correct for your environment.
    # This command assumes you have curl installed and the URLs are accessible.
    cmd = """curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo
curl -o /etc/yum.repos.d/epel.repo https://mirrors.aliyun.com/repo/epel-7.repo 
sed -i -e '/mirrors.cloud.aliyuncs.com/d' -e '/mirrors.aliyuncs.com/d' /etc/yum.repos.d/CentOS-Base.repo
yum clean all && yum makecache"""
    subprocess.run(cmd, shell=True, check=True)


@app.command()
def aliyun():
    # TODO: Implement Aliyun functionality
    os = get_os()
    if os.startswith("Ubuntu"):
        set_apt_sources(apt_sources[os.lower().replace(" ", "_").replace(".", "")[:11]])
    elif os.startswith("CentOS"):
        set_yum_repos()


@app.command()
def huaweiyun():
    # TODO: Implement Huawei Cloud functionality
    print("Huawei Cloud functionality is not yet implemented.")


def main():
    app()

if __name__ == "__main__":
    main()
