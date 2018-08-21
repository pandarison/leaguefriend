# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-02 10:22:39
# @Last Modified by:   caspar
# @Last Modified time: 2018-08-17 23:35:49

import rumps
import urllib
from monitor import LeagueMonitor
import subprocess
import os
import threading 
import time


def getAppPath():
    #/Users/caspar/Work/coding/python/AutoLOL/dist/autolol.app/Contents/Resources
    return os.path.realpath("../../")


class LeagueFriend(rumps.App):

    def __init__(self, *args, **kwargs):
        super(LeagueFriend, self).__init__(*args, **kwargs)
        self._AUTOMODE_ = {}

    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.alert("Not Implemented Yet!")

    def autocheck(self, idx):
        m = LeagueMonitor()
        sleep_time = 1
        previous = "IDLE"
        while self._AUTOMODE_[idx]:
            state = m.getClientState()
            self.menu["System: IDLE"].title = "System: {}".format(state)
            if state in ["Matchmaking", "ReadyCheck"]:
                sleep_time = 6
            elif state == "InProgress":
                sleep_time = 60
            elif state == "ChampSelect" and state != previous:
                team = m.getTeammembersFancy()
                data = {
                    "option":"pregame",
                    "region":m.getRegion(),
                    "data":team
                }
                threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],)).start()
                sleep_time = 6
            elif state in ["EndOfGame", "WaitingForStats", "PreEndOfGame"] and previous not in ["EndOfGame", "WaitingForStats", "PreEndOfGame"]:
                gameID = m.getPreviousGameID()
                data = {
                    "option":"postgame",
                    "region":m.getRegion(),
                    "data":{
                        "gameID":gameID,
                        "playerName":m.getCurrentPlayer()['internal_name']
                    }
                }
                threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],)).start()
                sleep_time = 30
            else:
                sleep_time = 30

            time.sleep(sleep_time)
            previous = state

    @rumps.clicked("Check My Team")
    def check_stats(self, _):
        m = LeagueMonitor()
        if m.getClientState() == "ChampSelect":
            team = m.getTeammembersFancy()
            data = {
                "option":"pregame",
                "data":team,
                "region":m.getRegion()
            }
            t = threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],))
            t.start()
        elif m.getClientState() == "InProgress":
            player = m.getCurrentPlayer()
            player['assigned_role'] = "None"
            data = {
                "option":"pregame",
                "data":[player],
                "region":m.getRegion()
            }
            t = threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],))
            t.start()
        else:
            rumps.alert("Can't find running League of Legends client, or not in champion selection.")

    @rumps.clicked("Previous Game")
    def check_last_game(self, _):
        m = LeagueMonitor()
        gameID = m.getPreviousGameID()
        if gameID is not None:
            data = {
                "option":"postgame",
                "region":m.getRegion(),
                "data":{
                    "gameID":gameID,
                    "playerName":m.getCurrentPlayer()['internal_name']
                }
            }
            threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],)).start()
        else:
            rumps.alert("Can't find game information.")

    @rumps.clicked("Automatic Mode")
    def auto_mode(self, sender):
        sender.state = not sender.state
        if sender.state:
            idx = len(self._AUTOMODE_) + 1
            self._AUTOMODE_[idx] = True
            self.child_process = threading.Thread(target=self.autocheck, args=(idx,))
            self.child_process.start()
        else:
            idx = len(self._AUTOMODE_)
            self._AUTOMODE_[idx] = False


def app():
    LeagueFriend("League Friend", menu=["Preferences", "Check My Team", "Previous Game", "Automatic Mode",  "System: IDLE"], icon=os.path.realpath("resources/app.icns")).run()

if __name__ == '__main__':
    app()
