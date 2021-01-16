#!/bin/bash

# Minimum Software Versions
REQ_DOCKER_VERSION=18.2.0

# Required to generate and install a ssh key so menu containers can securely execute commands on host
AUTH_KEYS_FILE=~/.ssh/authorized_keys
CONTAINER_KEYS_FILE=./.internal/.ssh/id_rsa

sys_arch=$(uname -m)

while test $# -gt 0
do
    case "$1" in
        --no-ask) NOASKCONFIRM="true"
            ;;
        --*) echo "bad option $1"
            ;;
    esac
    shift
done

echo "IOTstack Installation"
if [ "$EUID" -eq "0" ]; then
  echo "Please do not run as root"
  exit
fi

function command_exists() {
	command -v "$@" > /dev/null 2>&1
}

function minimum_version_check() {
	# Usage: minimum_version_check required_version current_major current_minor current_build
	# Example: minimum_version_check "1.2.3" 1 2 3
	REQ_MIN_VERSION_MAJOR=$(echo "$1"| cut -d' ' -f 2 | cut -d'.' -f 1)
	REQ_MIN_VERSION_MINOR=$(echo "$1"| cut -d' ' -f 2 | cut -d'.' -f 2)
	REQ_MIN_VERSION_BUILD=$(echo "$1"| cut -d' ' -f 2 | cut -d'.' -f 3)

	CURR_VERSION_MAJOR=$2
	CURR_VERSION_MINOR=$3
	CURR_VERSION_BUILD=$4
	
	VERSION_GOOD="Unknown"

	if [ -z "$CURR_VERSION_MAJOR" ]; then
		echo "$VERSION_GOOD"
		return 1
	fi

	if [ -z "$CURR_VERSION_MINOR" ]; then
		echo "$VERSION_GOOD"
		return 1
	fi

	if [ -z "$CURR_VERSION_BUILD" ]; then
		echo "$VERSION_GOOD"
		return 1
	fi

	if [ "${CURR_VERSION_MAJOR}" -ge $REQ_MIN_VERSION_MAJOR ]; then
		VERSION_GOOD="true"
		echo "$VERSION_GOOD"
		return 0
	else
		VERSION_GOOD="false"
	fi

	if [ "${CURR_VERSION_MAJOR}" -ge $REQ_MIN_VERSION_MAJOR ] && \
		[ "${CURR_VERSION_MINOR}" -ge $REQ_MIN_VERSION_MINOR ]; then
		VERSION_GOOD="true"
		echo "$VERSION_GOOD"
		return 0
	else
		VERSION_GOOD="false"
	fi

	if [ "${CURR_VERSION_MAJOR}" -ge $REQ_MIN_VERSION_MAJOR ] && \
		[ "${CURR_VERSION_MINOR}" -ge $REQ_MIN_VERSION_MINOR ] && \
		[ "${CURR_VERSION_BUILD}" -ge $REQ_MIN_VERSION_BUILD ]; then
		VERSION_GOOD="true"
		echo "$VERSION_GOOD"
		return 0
	else
		VERSION_GOOD="false"
	fi

	echo "$VERSION_GOOD"
}

function user_in_group() {
	if grep -q $1 /etc/group ; then
		if id -nGz "$USER" | grep -qzxF "$1";	then
				echo "true"
		else
				echo "false"
		fi
	else
		echo "notgroup"
	fi
}

function install_docker() {
  if command_exists docker; then
    echo "Docker already installed" >&2
  else
    echo "Install Docker" >&2
    curl -fsSL https://get.docker.com | sh
    sudo -E usermod -aG docker $USER
  fi

  if command_exists docker-compose; then
    echo "docker-compose already installed" >&2
  else
    echo "Install docker-compose" >&2
    sudo -E apt install -y docker-compose
  fi

	echo "" >&2
	echo "You should now restart your system" >&2
}

function do_group_setup() {
	echo "Setting up groups:"
	if [[ ! "$(user_in_group bluetooth)" == "notgroup" ]] && [[ ! "$(user_in_group bluetooth)" == "true" ]]; then
    echo "User is NOT in 'bluetooth' group. Adding:" >&2
    echo "sudo usermod -G bluetooth -a $USER" >&2
		sudo -E usermod -G "bluetooth" -a $USER
	fi

	if [ ! "$(user_in_group docker)" == "true" ]; then
    echo "User is NOT in 'docker' group. Adding:" >&2
    echo "sudo usermod -G docker -a $USER" >&2
		sudo -E usermod -G "docker" -a $USER
	fi

	echo "" >&2
	echo "Rebooting or logging off is advised." >&2
}

function do_env_setup() {
	sudo -E apt-get install git wget unzip -y
}

function do_iotstack_setup() {
	git clone https://github.com/SensorsIot/IOTstack.git
	cd IOTstack

	if [ $? -eq 0 ]; then
		echo "IOTstack cloned"
	else
		echo "Could not find IOTstack directory"
		exit 5
	fi
}

function generate_container_ssh() {
	cat /dev/null | ssh-keygen -q -N "" -f $CONTAINER_KEYS_FILE
}

function install_ssh_keys() {
	if [ -f "$CONTAINER_KEYS_FILE" ]; then
		NEW_KEY="$(cat $CONTAINER_KEYS_FILE.pub)"
		if grep -Fxq "$NEW_KEY" $AUTH_KEYS_FILE ; then
			echo "Key already exists in '$AUTH_KEYS_FILE' Skipping..."
		else
			echo "$NEW_KEY" >> $AUTH_KEYS_FILE
			echo "Key added."
		fi
	fi
}

do_env_setup
do_iotstack_setup
generate_container_ssh
install_ssh_keys
install_docker
do_group_setup