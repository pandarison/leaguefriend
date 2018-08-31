# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-02 10:22:39
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-27 11:49:37

import rumps
import urllib
from monitor import LeagueMonitor
import subprocess
import os
import threading 
import time
import xmlrpc.client
import requests
import json

__VERSION__ = 1.0


def getAppPath():
    #/Users/caspar/Work/coding/python/AutoLOL/dist/autolol.app/Contents/Resources
    return os.path.realpath("../../")

def rpc_call(data):
    with xmlrpc.client.ServerProxy("http://localhost:8913/") as proxy:
        proxy.call(str(data))


class LeagueFriend(rumps.App):

    def __init__(self, *args, **kwargs):
        super(LeagueFriend, self).__init__(*args, **kwargs)
        self._AUTOMODE_ = {}


    @rumps.clicked("Check For Updates")
    def prefs(self, _):
        #rumps.alert("Not Implemented Yet!")
        #rpc_call({"option":"test", "data":"test"})
        r = requests.get("https://api.github.com/repos/pandarison/leaguefriend/releases/latest").json()
        latest = float(r['tag_name'])
        if latest <= __VERSION__:
            rumps.alert("No update yet!")
            return

        text = "The latest release of League Friend was release on: \n"
        text += r['published_at'].replace("T", " ").replace("Z", " ")
        text += "\n\n\n"
        text += "Release Notes:\n"
        text += r['body']
        text += "\n\nOpen website by click [Open] below."
        window = rumps.Window("Note: League Friend is still under development.", "Update", ok="Open", cancel="Not Now", default_text=text)
        window.icon = os.path.realpath("resources/app.icns")
        response = window.run()
        if response.clicked:
            threading.Thread(target=subprocess.call, args=(["open", "https://github.com/pandarison/leaguefriend" ],)).start()

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
                self.session = {"team1":[], "team2":[]}
                data = {
                    "option":"pregame",
                    "region":m.getRegion(),
                    "data":team
                }
                threading.Thread(target=subprocess.call, args=(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data) ],)).start()
                sleep_time = 6
            elif state == "ChampSelect" and False:
                data = m.getCurrentChampSelectSession()
                flag = False
                for summoner in data['myTeam']:
                    if summoner['championId'] != 0 and summoner['championId'] not in self.session['team1']:
                        self.session['team1'].append(summoner['championId'])
                        flag = True
                for summoner in data['theirTeam']:
                    if summoner['championId'] != 0 and summoner['championId'] not in self.session['team2']:
                        self.session['team2'].append(summoner['championId'])
                        flag = True
                if flag:
                    self.menu["System: IDLE"].title = "System: {}".format("BEFORE_CALL")
                    rpc_call({
                        "option":"ChampSelect-Update",
                        "data":self.session
                        })
                    self.menu["System: IDLE"].title = "System: {}".format("END_CALL")
                sleep_time = 6

            elif state == "InProgress":
                sleep_time = 30
            elif previous in ["InProgress", "WaitingForStats", "PreEndOfGame"] and state not in ["InProgress", "WaitingForStats", "PreEndOfGame"]:
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

            previous = state
            time.sleep(sleep_time)
            

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
            #print("".join(["open", "-W", "-n", "-a", getAppPath(), "--args", "browser", str(data)]))
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
    LeagueFriend("League Friend", menu=["Check For Updates", "Check My Team", "Previous Game", "Automatic Mode",  "System: IDLE"], icon=os.path.realpath("resources/app.icns")).run()

if __name__ == '__main__':
    app()
