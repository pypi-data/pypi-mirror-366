#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "1.0.0"

import os
import signal
import tempfile

from glob import glob
from uuid import uuid4


class Pid:
    """
    Process management
    """

    def __init__(
        self,
        pid_name: str,
        quantity: int = 1,
        kill_after: int = 0,
        pid_path: str = None,
    ):
        """
        :param pid_name: pid file location
        :param quantity: number of copies of the program
        :param kill_after: how long will it take to delete the pid and process
        """

        self.pid_file = (
            os.path.join(pid_path, f"{pid_name}.pid")
            if pid_path
            else os.path.join(tempfile.gettempdir(), f"{pid_name}.pid")
        )

        self.quantity = quantity
        self.kill_after = kill_after

    @staticmethod
    def check(p_id: int) -> bool:
        """
        Checking a running process
        :param p_id:
        :return:
        """

        try:
            os.kill(p_id, 0)
        except OSError:
            return False

        return True

    def get_pid_files(self) -> list:
        """
        Get pid files
        :return:
        """

        pid_list = []
        pid_files = []
        pid_files.extend(glob(os.path.join(f"{self.pid_file}*")))

        for p_file in pid_files:
            try:
                with open(p_file, "r") as p:
                    pid_list.append({"pid": int(p.read()), "file": p_file})
            except ValueError:
                os.remove(p_file)
            except FileNotFoundError:
                pass

        return pid_list

    def delete_pid_files(self, pid_files: list) -> list:
        """
        Delete old files with non-existent processes
        :param pid_files:
        :return:
        """

        pid_list = []

        for p in pid_files:
            if not self.check(p.get("pid")):
                os.remove(p.get("file"))
            else:
                pid_list.append(p)

        return pid_list

    def create_pid_file(self) -> tuple:
        """
        Create file with current pid
        :return:
        """

        pid_list = self.delete_pid_files(self.get_pid_files())

        pids_count = len(pid_list)

        if pids_count >= self.quantity:
            return False, None

        pid_file = f"{self.pid_file}.{uuid4()}"

        p_id = os.getpid()

        with open(pid_file, "w") as pf:
            pf.write(str(p_id))

        return p_id, pid_file

    @staticmethod
    def kill(p_id: int) -> str:
        """
        Removal process by pid
        :param p_id:
        :return:
        """

        try:
            os.kill(p_id, signal.SIGKILL)
        except OSError as e:
            return f"{e}"

        return ""
