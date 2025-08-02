import click
import subprocess
import platform

@click.command()
@click.option('--os', type=click.Choice(['Windows', 'Ubuntu', 'RedHat', 'Red_Hat', 'Rocky'], case_sensitive=False),
              default=None, help='Option for installing on Windows, Ubuntu, Red Hat, or Rocky')
def installdev(os):
    """Setup local DevOps development environment"""
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = {}
            for line in f:
                key, value = line.strip().split('=')
                os_info[key.strip('"')] = value.strip('"')

        if os == 'Windows' or (os is None and platform.system() == 'Windows'):
            # Command to execute on Windows
            command = ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-Command',
                       'Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/OiMoulder/Yeller/master/windows.ps1 | Invoke-Expression'
                    ]
        elif os == 'Ubuntu' or (os is None and os_info.get('NAME') == 'Ubuntu'):
            # Command to execute on Ubuntu
            command = ['echo', 'Hello from Ubuntu!']
        elif os == 'RedHat' or os == 'Red_Hat' or (os is None and os_info.get('NAME') in ['Red Hat Enterprise Linux']):
            # Command to execute on Red Hat
            command = ['echo', 'Hello from Red Hat!']
        elif os == 'Rocky' or (os is None and os_info.get('NAME') in ['Rocky']):
            # Command to execute on Rocky
            command = ['echo', 'Hello from Rocky Linux!']
        else:
            click.echo("Please specify a valid operating system (Windows, Ubuntu, RedHat, or Rocky)")
            return

        subprocess.run(command, check=True)
    except FileNotFoundError:
        click.echo("Cannot determine operating system.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running command: {e}")
