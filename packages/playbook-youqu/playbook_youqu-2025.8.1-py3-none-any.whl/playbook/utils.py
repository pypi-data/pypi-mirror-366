import os
import re
import sys
import time
import copy

from typing import Tuple

from playbook.config import config
from playbook.__version__ import __version__
from nocmd import RemoteCmd
from funnylog2 import logger


def pre_env():
    empty = "> /dev/null 2>&1"
    os.system("rm -rf ./Pipfile")
    os.system("rm -rf ~/Pipfile")
    os.system("rm -rf .venv")
    os.system("rm -rf ~/.ssh/known_hosts")
    sudo = f"echo '{config.PASSWORD}' | sudo -S"
    if "StrictHostKeyChecking no" not in os.popen("cat /etc/ssh/ssh_config").read():
        os.system(
            f"""{sudo} sed -i "s/#   StrictHostKeyChecking ask/ StrictHostKeyChecking no/g" /etc/ssh/ssh_config {empty}"""
        )
    if os.system(f"sshpass -V {empty}") != 0:
        os.system(f"{sudo} apt update {empty}")
        os.system(f"{sudo} apt install sshpass {empty}")


def check_remote_connected(user, _ip, password, debug: bool = False):
    logger.info(f"Checking remote: {user, _ip, password}")
    if debug:
        return True
    return_code = RemoteCmd(user, _ip, password).remote_run("hostname -I", use_sshpass=True, log_cmd=False)
    if return_code == 0:
        logger.info(f"Remote: {user, _ip, password} connected")
        return True
    return False


def convert_client_to_ip(client: str) -> Tuple[str, str, str]:
    match = re.match(r"^(.+?)@(\d+\.\d+\.\d+\.\d+):{0,1}(.*?)$", client)
    if match:
        user, ip, password = match.groups()
        if not password:
            password = config.PASSWORD
        return user, ip, password
    else:
        raise ValueError(f"Invalid client format, {client}")


def set_playbook_run_exitcode(status):
    if status != 0:
        os.environ["PLAYBOOK_RUN_EXIT_CODE"] = str(status)


def exit_with_playbook_run_exitcode():
    playbook_run_exitcode = os.environ.get("PLAYBOOK_RUN_EXIT_CODE")
    if playbook_run_exitcode is not None and int(playbook_run_exitcode) != 0:
        sys.exit(1)


def are_multisets_equal(l1, l2):
    return all(l1.count(item) == l2.count(item) for item in set(l1)) and len(l1) == len(l2)


def task_start(client, task_id):
    user, ip, password = convert_client_to_ip(client)
    stdout, return_code = RemoteCmd(user, ip, password).remote_run(
        f"touch ~/.playbook_{task_id}_working",
        return_code=True
    )
    return return_code == 0


def clients_task_start(clients: list, task_id: str):
    for client in clients:
        task_start(client, task_id)


def task_end(client, task_id):
    user, ip, password = convert_client_to_ip(client)
    RemoteCmd(user, ip, password).remote_run(f"rm -rf ~/.playbook_{task_id}_working")


def clients_task_end(clients: list, task_id: str):
    for client in clients:
        task_end(client, task_id)


def client_reboot(client: str):
    logger.info(f"Rebooting client: {client}")
    user, ip, password = convert_client_to_ip(client)
    RemoteCmd(user, ip, password).remote_sudo_run("reboot", use_sshpass=True, log_cmd=False)


def check_client_enter_desktop(client: str):
    logger.info(f"Checking client: {client} enter desktop")
    user, ip, password = convert_client_to_ip(client)
    stdout, return_code = RemoteCmd(user, ip, password).remote_run(
        "ps -ef | grep -v grep | grep kwin > /dev/null",
        log_cmd=False,
        return_code=True,
        timeout=10,
    )
    if return_code == 0:
        logger.info(f"Client: {client} entered desktop")
        return True
    return False


def reboot_clients(hosts: list, reboot: bool = True):
    clients = copy.deepcopy(hosts)
    logger.info(f"Reboot status: {clients, reboot}")
    if not reboot:
        return True
    for client in clients:
        client_reboot(client)
    logger.info(f"Waiting for {clients} to enter desktop")
    time.sleep(5)
    for i in range(100):
        for client in clients[::-1]:
            if check_client_enter_desktop(client):
                clients.remove(client)
        if clients:
            time.sleep(2)
        else:
            time.sleep(2)
            logger.info(f"All {hosts} enter desktop")
            return True
    logger.error(f"Timeout waiting for {hosts} to enter desktop")
    return False


def get_client_status(host: str, task_id: str):
    """
    True 繁忙 / False 空闲
    """
    user, ip, password = convert_client_to_ip(host)
    stdout, return_code = RemoteCmd(user, ip, password).remote_run(
        f"[ -f ~/.playbook_{task_id}_working ] && echo true || echo false",
        return_code=True,
        log_cmd=False,
        timeout=10,
    )
    if return_code is None:
        return True
    status = stdout.split()[-1]
    if status == "true":
        return True
    elif status == "false":
        logger.info(f"Client: {host, task_id} is idle")
        return False
    else:
        logger.error(f"Invalid status: {status, stdout}, check {host}:~/.playbook_{task_id}_working")
        return True

def print_flag():
    logger.info(
        rf"""
      _____  _             ____              _    
     |  __ \| |           |  _ \            | |   
     | |__) | | __ _ _   _| |_) | ___   ___ | | __
     |  ___/| |/ _` | | | |  _ < / _ \ / _ \| |/ /
     | |    | | (_| | |_| | |_) | (_) | (_) |   < 
     |_|    |_|\__,_|\__, |____/ \___/ \___/|_|\_\
                      __/ |                       
                     |___/                        
                 
ღღღ PlayBook, Task Scheduling System, version {__version__} ღღღ
        """
    )


if __name__ == '__main__':
    # a = get_client_status("uos@10.8.15.50", "test")
    # print(a)
    print_flag()
