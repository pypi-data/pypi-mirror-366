# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import os
import socket
import threading
import time
import typing as t


class UniqueId:

    __uniqueid_counter = 0
    __uniqueid_lock = threading.Lock()

    def __init__(self, localid: str|None = None):
        if localid is not None:
            self.__local_id = localid
        else:
            with self.__uniqueid_lock:
                self.__local_id = f"{time.time()}.{self.__uniqueid_counter}"
                self.__uniqueid_counter += 1
        self.__host_id = socket.getfqdn()  # TODO forbidden chars?!
        self.__process_id = str(os.getpid())

    @property
    def long_str(self) -> str:
        return self.__long_str(self.short_str)

    @property
    def short_str(self) -> str:
        return f"{self.__host_id}..{self.__process_id}..{self.processonly_short_str}"

    @property
    def processonly_long_str(self) -> str:
        return self.__long_str(self.__local_id)

    @property
    def processonly_short_str(self) -> str:
        return self.__local_id

    def __long_str(self, txt: str) -> str:
        return f"annize..{txt}"

    def __str__(self):
        return self.long_str
