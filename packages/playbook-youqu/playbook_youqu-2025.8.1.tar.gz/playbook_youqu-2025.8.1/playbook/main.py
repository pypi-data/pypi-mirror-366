import time
from typing import List, Dict
import itertools
import json
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from funnylog2 import logger

from playbook import utils
from playbook.command import Command


class PlayBook:

    def __init__(self, **kwargs):
        self.clients = kwargs.get("clients")
        self.tags = kwargs.get("tags")
        self.only_one_client = True if len(self.clients) == 1 else False
        self.IS_DEBUG = kwargs.get("debug") is True
        self.kwargs = kwargs
        self.pause: int = 3
        self.wait_test_start_range: int = 20

    def make_playbook(self) -> List[List[Dict]]:
        playbook: List = []
        group: List = []
        apps = sorted(self.kwargs.get("apps"), key=lambda x: x.get("order"))
        if self.only_one_client:
            for app_obj in apps:
                app_dict = self.create_app_dict(app_obj, split_run=False)
                group.append(app_dict)
                playbook.append(group)
                group = []
        else:
            for app_obj in apps:
                split_run = app_obj.get("split_run")
                app_dict = self.create_app_dict(app_obj, split_run=split_run)
                if split_run:
                    if group:
                        playbook.append(group)
                        group = []
                    group.append(app_dict)
                    playbook.append(group)
                    group = []
                else:
                    group.append(app_dict)
            if group:
                playbook.append(group)
        transfer_file = "transfer.json"
        with open(transfer_file, "w", encoding="utf-8") as f:
            json.dump(playbook, f, indent=4)
            logger.info(f"PlayBook 生成 {transfer_file} ☟☟☟\n{json.dumps(playbook, indent=4)}")
        return playbook

    def create_app_dict(self, app_obj: Dict, split_run: bool) -> Dict:
        clients = self.clients if split_run else "rolling"
        if self.only_one_client:
            clients = self.clients
            split_run = False
        app_dict = {
            "app_name": app_obj.get("app_name"),
            "git": {
                "url": app_obj.get("git_url"),
                "branch": app_obj.get("git_branch")
            },
            "framework": app_obj.get("framework"),
            "split_run": split_run,
            "clients": clients,
            "order": app_obj.get("order"),
            "device": app_obj.get("device")
        }
        return app_dict

    def get_client_test_status(self, host, task_id):
        if self.IS_DEBUG:
            return False
        return utils.get_client_status(host, task_id)

    def run_by_cmd(self, cmd: str, hosts: list, task_id: str, reboot: bool = True):
        logger.info(f"{cmd, hosts, task_id, reboot}")
        if self.IS_DEBUG:
            return
        client_ready = utils.reboot_clients(hosts, reboot)
        if client_ready:
            if reboot:
                time.sleep(60)
            return_code = os.system(cmd)
            logger.info(f"command_return_code: {return_code}")
            utils.set_playbook_run_exitcode(return_code)
            utils.clients_task_end(hosts, task_id)
            logger.info(f"{cmd, hosts, task_id} 执行完，释放机器")
        else:
            logger.info(f"{hosts, reboot} 重启失败")

    def generate_command(self, app: Dict, client=None):
        framework, *default_manages = app.get("framework").split("->")
        if default_manages:
            default_manages = default_manages[0]
        else:
            default_manages = None
        clients = app.get("clients") if client is None else [client]

        if hasattr(Command, f"{framework}_command"):
            cmd, hosts = getattr(
                Command(
                    app.get("app_name"),
                    clients,
                    default_manages,
                    self.tags,
                    self.kwargs.get("task_id"),
                    app.get("git").get("url"),
                    app.get("git").get("branch"),
                    self.kwargs.get("json_backfill_base_url"),
                    self.kwargs.get("json_backfill_user"),
                    self.kwargs.get("json_backfill_password"),
                    self.kwargs.get("pms_user"),
                    self.kwargs.get("pms_password"),
                    self.kwargs.get("pms_task_id"),
                    self.IS_DEBUG,
                    self.kwargs.get("manages"),
                    self.kwargs.get("other_args"),
                ),
                f"{framework}_command"
            )()
        else:
            raise EnvironmentError(f"Framework: {framework} not supported")
        return cmd, hosts

    def play(self):
        playbooks = self.make_playbook()
        for index, group in enumerate(playbooks):
            logger.debug(f"======= 开始执行 group {index + 1} =======")
            split_run = len(group) == 1 and group[0].get("split_run")
            if split_run or self.only_one_client:
                utils.clients_task_start([i.get("host") for i in self.clients], self.kwargs.get("task_id"))
                cmd, hosts = self.generate_command(group[0])
                reboot = True
                if index == 0:
                    reboot = False
                self.run_by_cmd(cmd, hosts, self.kwargs.get("task_id"), reboot)
            else:
                executor = ThreadPoolExecutor()

                device_group = []
                no_device_group = []
                for app in group:
                    app_devices = app.get("device")
                    if app_devices:
                        app_devices = app_devices.split(",")
                        for app_device in app_devices:
                            if app_device not in ",".join([i.get("device") for i in self.clients if i.get("device")]):
                                no_device_group.append(app)
                                break
                        else:
                            device_group.append(app)
                    else:
                        no_device_group.append(app)
                tasks = []
                for app_index, app in enumerate(no_device_group):
                    for client in itertools.cycle(self.clients):
                        client_host = client.get("host")
                        if self.get_client_test_status(client_host, self.kwargs.get("task_id")):
                            time.sleep(self.pause)
                        else:
                            logger.debug(f"{client} 状态空闲，开始执行")
                            utils.task_start(client_host, self.kwargs.get("task_id"))
                            reboot = True
                            if index == 0 and app_index < len(self.clients):
                                reboot = False
                            cmd, hosts = self.generate_command(app, client)
                            t = executor.submit(self.run_by_cmd, cmd, hosts, self.kwargs.get("task_id"), reboot)
                            tasks.append(t)
                            time.sleep(self.pause)
                            break
                if no_device_group:
                    wait(tasks, return_when=ALL_COMPLETED)
                tasks = []
                for app_index, app in enumerate(device_group):
                    app_devices = app.get("device").split(",")
                    for client in itertools.cycle(self.clients):
                        client_host = client.get("host")
                        client_devices = client.get("device").split(",") if client.get("device") else []

                        if utils.are_multisets_equal(app_devices, client_devices):
                            if self.get_client_test_status(client_host, self.kwargs.get("task_id")):
                                time.sleep(self.pause)
                            else:
                                logger.debug(f"{client} 状态空闲，开始执行")
                                utils.task_start(client_host, self.kwargs.get("task_id"))
                                reboot = True
                                if index == 0 and app_index < len(self.clients):
                                    reboot = False
                                cmd, hosts = self.generate_command(app, client)
                                t = executor.submit(self.run_by_cmd, cmd, hosts, self.kwargs.get("task_id"), reboot)
                                tasks.append(t)
                                time.sleep(self.pause)
                                break
                        else:
                            time.sleep(self.pause)
                if device_group:
                    wait(tasks, return_when=ALL_COMPLETED)
                executor.shutdown()
            logger.debug(f"======= 结束执行 group {index + 1} =======\n")


def playbook(input_json_path, debug):
    utils.print_flag()
    with open(input_json_path, "r", encoding="utf-8") as f:
        kwargs = json.load(f)

    kwargs["debug"] = debug
    input_clients = kwargs.get("clients")
    if not input_clients:
        raise ValueError
    clients = []
    for client in input_clients:
        if utils.check_remote_connected(*utils.convert_client_to_ip(client.get("host")), debug):
            clients.append(client)
        else:
            logger.error(f"======= {client} SSH 连接不通，已剔出资源池！=======")
    kwargs["clients"] = clients

    utils.pre_env()
    PlayBook(**kwargs).play()
    logger.info("PlayBook Task Execution Completed. ღღღ")
    utils.exit_with_playbook_run_exitcode()


if __name__ == '__main__':
    playbook("../info.json", debug=True)
