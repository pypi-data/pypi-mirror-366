"""
Created on 2023-04-01

@author: wf
"""

import tempfile
import time

from mwdocker.docker import DockerContainer
from python_on_whales import DockerException


class ProfiWikiContainer:
    """
    a profiwiki docker container wrapper
    """

    def __init__(self, dc: DockerContainer):
        """
        Args:
            dc(DockerContainer): the to wrap
        """
        self.dc = dc

    def log_action(self, action: str):
        """
        log the given action

        Args:
            action(str): the d
        """
        if self.dc:
            print(f"{action} {self.dc.kind} {self.dc.name}", flush=True)
        else:
            print(f"{action}", flush=True)

    def wait_ready(self, timeout=5, check_interval=0.1, verbose=True):
        """
        Wait until the container is fully ready to accept commands

        Args:
            timeout (int): Maximum time to wait in seconds
            check_interval (float): Time between checks in seconds
            verbose (bool): If True, print status messages during waiting

        Raises:
            TimeoutError: If the container is not ready after the timeout period
        """
        start_time = time.time()
        tries = 0

        while time.time() - start_time < timeout:
            tries += 1
            if verbose:
                print(f"Checking if container is ready (try {tries})...")

            try:
                # Try a simple command to check if container is ready
                self.dc.container.execute(["test", "-e", "/bin"], tty=True)
                if verbose:
                    print(f"Container ready after {tries} tries")
                return True
            except Exception as e:
                # If still not ready, wait and try again
                if verbose:
                    print(f"Container not ready on try {tries}: {e}")
                time.sleep(check_interval)

        # If we've reached this point, the timeout has expired
        error_msg = f"Container not ready after {tries} tries and {timeout} seconds"
        if verbose:
            print(error_msg)
        raise TimeoutError(error_msg)

    def upload(self, text: str, path: str, with_wait: bool = True):
        """
        upload the given text to the given path
        """
        with tempfile.NamedTemporaryFile() as tmp:
            self.log_action(f"uploading {tmp.name} as {path} to ")
            with open(tmp.name, "w") as text_file:
                text_file.write(text)
            self.dc.container.copy_to(tmp.name, path)
        if with_wait:
            self.wait_ready()

    def killremove(self, volumes: bool = False):
        """
        kill and remove me

        Args:
            volumes(bool): if True remove anonymous volumes associated with the container, default=True (to avoid e.g. passwords to get remembered / stuck
        """
        if self.dc:
            self.log_action("killing and removing")
            self.dc.container.kill()
            self.dc.container.remove(volumes=volumes)

    def start_cron(self):
        """
        Starting periodic command scheduler: cron.
        """
        self.dc.container.execute(["/usr/sbin/service", "cron", "start"], tty=True)

    def install_plantuml(self):
        """
        install plantuml to this container
        """
        script = """#!/bin/bash
# install plantuml
# WF 2023-05-01
apt-get update
apt-get install -y plantuml
"""
        # https://gabrieldemarmiesse.github.io/python-on-whales/docker_objects/containers/
        script_path = "/root/install_plantuml.sh"
        self.install_and_run_script(script, script_path)
        pass

    def install_and_run_script(self, script: str, script_path: str):
        """
        install and run the given script

        Args:
            script(str): the source code of the script
            script_path(str): the path to copy the script to and then execute
        """
        self.upload(script, script_path)
        # make executable - this is potentially buggy see
        # https://github.com/moby/moby/issues/40399 suggesting that
        # stdin/stdout handling might be problematic
        self.dc.container.execute(["chmod", "+x", script_path], tty=True)
        # run
        self.dc.container.execute([script_path], tty=True)

    def install_fontawesome(self):
        """
        install fontawesome to this container
        """
        script = """#!/bin/bash
# Font Awesome installer for Docker environment
# WF 2025-05-19
BASE_DIR="/var/www/font-awesome"
CONF="font-awesome-all"
APACHE_CONF="/etc/apache2/conf-available/$CONF.conf"

# Start fresh configuration
cat << EOF > "$APACHE_CONF"
# Font Awesome configurations
# Generated: $(date)
# Version: 1.0
# Author: WF
# Description:
#    This configuration provides aliases for three Font Awesome versions
#    4.5.0, 5.15.4, 6.4.0
# with version 4.5.0 being the default "official" version.
EOF
VERSIONS=("4.5.0" "5.15.4" "6.4.0")
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit 1

for version in "${VERSIONS[@]}"; do
  major="${version%%.*}"

  # Map version directly to the correct directory name
  case "$major" in
    4)
      zip_url="https://download.bitplan.com/font-awesome-4.5.0.zip"
      zip_file="font-awesome-$version.zip"
      dir_name="font-awesome"
      ;;
    *)
      zip_url="https://github.com/FortAwesome/Font-Awesome/releases/download/$version/fontawesome-free-$version-desktop.zip"
      zip_file="fontawesome-$version.zip"
      dir_name="fontawesome-free-$version-desktop"
      ;;
  esac

  echo "Installing Font Awesome $version..."

  # Download and extract only if directory doesn't exist
  if [ ! -d "$dir_name" ]; then
    echo "Directory $dir_name not found, downloading and extracting..."
    curl --silent --fail -L "$zip_url" -o "$zip_file"
    unzip -q -o "$zip_file"
    rm -f "$zip_file"

    # Set ownership
    chown -R www-data:www-data "$dir_name"
  else
    echo "Directory $dir_name already exists, skipping download"
  fi

  # Create compatibility symlink if needed
  if [ ! -e "$dir_name/svg" ] && [ -d "$dir_name/svgs" ]; then
    echo "Creating compatibility symlink for $dir_name"
    ln -sf svgs/solid "$dir_name/svg"
  fi

  # Create aliases pointing to the correct directories
  echo "Alias /fontawesome$major $BASE_DIR/$dir_name" >> "$APACHE_CONF"
  echo "Alias /fa$major $BASE_DIR/$dir_name" >> "$APACHE_CONF"
  # version 4 is our "official" fontawesome
  case "$major" in
    4)
      echo "Alias /font-awesome $BASE_DIR/$dir_name" >> "$APACHE_CONF"
      ;;
  esac
done

# Add the directory access configuration
cat <<EOS >> "$APACHE_CONF"
<Directory $BASE_DIR>
  Options Indexes FollowSymLinks MultiViews
  Require all granted
</Directory>
EOS

# Enable the new configuration
a2enconf $CONF > /dev/null
apache2ctl -k graceful
echo "Font Awesome installation complete."
echo "Access via: /fontawesome4, /fontawesome5, /fontawesome6"
echo "or shorthand: /fa4, /fa5, /fa6"
"""
        script_path = "/root/install_fontawesome"
        self.install_and_run_script(script, script_path)
        try:
            self.dc.container.execute(["service", "apache2", "restart"])
        except DockerException as e:
            # we expect a SIGTERM
            if not e.return_code == 143:
                raise e
        pass
