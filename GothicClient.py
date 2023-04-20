from __future__ import annotations

import asyncio
import copy
import ctypes
import logging
import multiprocessing
import os.path
import re
import sys
import typing
import queue
import zipfile
import io
from pathlib import Path

# CommonClient import first to trigger ModuleUpdater
from CommonClient import CommonContext, server_loop, ClientCommandProcessor, gui_enabled, get_base_parser, logger
from Utils import init_logging, is_windows, persistent_load, persistent_store

if __name__ == "__main__":
    init_logging("GothicClient")

from worlds.gothic1 import Gothic1World
from worlds.gothic1.Items import item_id_to_name, item_table
from worlds.gothic1.Locations import location_table

import watchdog
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

import colorama
from NetUtils import ClientStatus, NetworkItem, RawJSONtoTextParser
from MultiServer import mark_raw


# Send/Receive from the perspective of the game
G1_SEND_FILE = "ap_send.txt"
G1_RECEIVE_FILE = "ap_receive.txt"
G1_MOD_FILE = "Data\\archipelago.vdf"

class GothicClientProcessor(ClientCommandProcessor):
    ctx: GothicContext
    observer: Observer

    @mark_raw
    def _cmd_set_path(self, path: str = '') -> bool:
        """Manually set the Gothic install directory (if the automatic detection fails)."""
        if path:
            self.ctx.path = path
            persistent_store("Gothic 1", "path", path)
            self.ctx.log_mod_installation_status()
            return True
        else:
            logger.info(f"Current path: {self.ctx.path}")
            self.ctx.log_mod_installation_status()
            # logger.info("Run this command with the path to your Gothic installation to change it.")
        return False

class GothicContext(CommonContext):
    command_processor = GothicClientProcessor
    game = "Gothic 1"
    items_handling = 0b111
    observer = None
    path = None
    communicate_task = None
    sending = False
    last_sent_read = True
    last_sent_item = None
    chest_count = 0

    announcements = queue.Queue()
    difficulty_override = -1
    to_send = queue.Queue()
    sent_items = []
    to_receive = queue.Queue()

    def __init__(self, *args, **kwargs):
        super(GothicContext, self).__init__(*args, **kwargs)
        self.raw_text_parser = RawJSONtoTextParser(self)
        self.event_handler = GothicEventHandler(self)
        self.path = persistent_load().get("Gothic 1", {}).get("path", None)
        self.communicate_task = asyncio.create_task(self.communicate(), name = "Send")

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(GothicContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()
        await self.send_msgs([{"cmd": "Get", "keys": ["chest_count", "sent_items"]}])

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            # self.difficulty = args["slot_data"]["game_difficulty"]
            # self.all_in_choice = args["slot_data"]["all_in_map"]
            # slot_req_table = args["slot_data"]["mission_req"]
            # self.mission_order = args["slot_data"].get("mission_order", 0)
            # self.final_mission = args["slot_data"].get("final_mission", 29)
            self.clean_files()
        elif cmd in {"ReceivedItems"}:
            for item in args["items"]:
                item_name = item_id_to_name[item.item]
                self.to_send.put(item_name)
        elif cmd in {"Retrieved"}:
            chest_count = args["keys"]["chest_count"]
            if chest_count is None:
                self.chest_count = 0
            else:
                self.chest_count = chest_count
            sent_items = args["keys"]["sent_items"]
            if sent_items is not None:
                for item in sent_items:
                    # sent_items is a subset of to_send,
                    # so this is a safe operation
                    self.to_send.queue.remove(item)
            self.start_observer()

    def clean_files(self):
        if not self.path:
            self.get_path()
        reconnect_obs = True if self.observer else False
        if reconnect_obs:
            self.stop_observer()
        send_path, receive_path = self.get_file_paths()
        # Write empty string (in Gothic's encoding) to receive file
        with open(receive_path, mode = 'wb') as file:
            file.write((0).to_bytes(4, 'little'))
        # Make send file empty
        with open(send_path, mode = 'w') as _:
            pass
        if reconnect_obs:
            self.start_observer()

    def log_mod_installation_status(self):
        if self.check_mod_installation():
            logger.info("Mod installation found.")
        else:
            logger.warning("Mod installation not found. Please use /set_path [path] to set a valid Gothic installation path.")
    
    def check_mod_installation(self) -> bool:
        if self.path is not None:
            success = True
            send_path, receive_path = self.get_file_paths()
            success &= os.path.isfile(send_path)
            success &= os.path.isfile(receive_path)
            success &= os.path.isfile(fr"{self.path}\{G1_MOD_FILE}")
            return success
        return False

    def start_observer(self):
        if not self.observer:
            if not self.path:
                self.get_path()
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.path)
            self.observer.start()
            logger.info("Started observation")

    def stop_observer(self):
        if self.observer:
            self.observer.stop()
            self.observer = None
            logger.info("Stopped observation")

    def get_path(self):
        self.path = persistent_load().get("Gothic 1", {}).get("path", None)

    async def communicate(self):
        while True:
            if self.last_sent_read:
                if self.last_sent_item is not None:
                    await self.send_msgs([{"cmd": "Set", "key": "sent_items", "default": [], "want_reply": False,
                                           "operations": [{"operation": "add", "value": [self.last_sent_item]}]}])
                    self.last_sent_item = None
                if self.to_send.qsize() > 0:
                    self.sending = True
                    item = self.to_send.get()
                    item_inst = item_table[item].inst
                    _, receive_path = self.get_file_paths()
                    with open(receive_path, mode = 'wb') as file:
                        length = len(item_inst)
                        file.write(length.to_bytes(4, 'little'))
                        file.write(item_inst.encode())
                    self.last_sent_item = item
                    self.last_sent_read = False
                    self.sending = False
            while self.to_receive.qsize() > 0:
                msgs = self.to_receive.get()
                check = msgs[0]
                if check == "1": # code for chest
                    await self.send_msgs([
                        {"cmd": 'LocationChecks', "locations": [location_table[self.chest_count].code]},
                        {"cmd": "Set", "key": "chest_count", "default": self.chest_count, "want_reply": False,
                         "operations": [{"operation": "add", "value": 1}]}
                    ])
                    self.chest_count += 1
            # Send one item per second
            await asyncio.sleep(1)

    def on_print_json(self, args: dict):
        # goes to this world
        if "receiving" in args and self.slot_concerns_self(args["receiving"]):
            relevant = True
        # found in this world
        elif "item" in args and self.slot_concerns_self(args["item"].player):
            relevant = True
        # not related
        else:
            relevant = False

        if relevant:
            self.announcements.put(self.raw_text_parser(copy.deepcopy(args["data"])))

        super(GothicContext, self).on_print_json(args)

    def run_gui(self):
        from kvui import GameManager

        class GothicManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Gothic Client"

        self.ui = GothicManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def shutdown(self):
        await super(GothicContext, self).shutdown()
        if self.observer:
            self.observer.stop()
        if self.communicate_task:
            self.communicate_task.cancel()

    def get_file_paths(self) -> tuple[str, str]:
        send = fr"{self.path}\{G1_SEND_FILE}"
        receive = fr"{self.path}\{G1_RECEIVE_FILE}"
        return (send, receive)


async def main():
    multiprocessing.freeze_support()
    parser = get_base_parser()
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    args = parser.parse_args()

    ctx = GothicContext(args.connect, args.password)
    ctx.auth = args.name
    if ctx.server_task is None:
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    await ctx.exit_event.wait()

    await ctx.shutdown()

class GothicEventHandler(FileSystemEventHandler):
    ctx: GothicContext
    send_procs = 0
    receive_procs = 0

    def __init__(self, ctx: GothicContext):
        self.ctx = ctx
    
    def on_modified(self, event):
        super().on_modified(event)

        send_path, receive_path = self.ctx.get_file_paths()
        
        if event.src_path == send_path:
            logger.info("Noticed modified ap_send.")
            self.send_procs += 1
            if self.send_procs == 2:
                self.send_procs = 0
                with open(event.src_path, mode='rt') as file:
                    msgs = file.readlines()
                    self.ctx.to_receive.put(msgs)
        elif event.src_path == receive_path:
            logger.info("Noticed modified ap_receive.")
            self.receive_procs += 1
            if self.receive_procs == 2:
                self.receive_procs = 0
                if not self.ctx.sending:
                    self.ctx.last_sent_read = True

if __name__ == '__main__':
    colorama.init()
    asyncio.run(main())
    colorama.deinit()
