# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-01 16:23:01
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-30 20:22:12

import requests
from requests.auth import HTTPBasicAuth
import os
import json
import time
import threading
from client_data import GameData, GamePhaseWaitingTime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

TEST = [{'id': 100630443, 'internal_name': 'sonamilol', 'display_name': 'Sonami LOL', 'assigned_role': '', 'champion_id': 82}, {'id': 100630443, 'internal_name': 'sonamilol', 'display_name': 'Sonami LOL', 'assigned_role': '', 'champion_id': 62}]


class LeagueMonitor(threading.Thread):

    def __init__(self, client_data, *args, **kwargs):
        self.client_data = client_data
        super(LeagueMonitor, self).__init__(*args, **kwargs)
        self._cache = {}
        self.WAS_IN_GAME = True
    def getPlayerByID(self, uid):
        try:
            if "getPlayerByID:" + str(uid) in self._cache:
                return dict(self._cache["getPlayerByID:" + str(uid)])
            if uid == 0:
                return {
                    "id":0,
                    "internal_name":"",
                    "display_name":""
                }
            r = requests.get(self.baseURL + "/lol-summoner/v1/summoners/{}".format(uid), verify=False, auth=HTTPBasicAuth('riot', self.password))
            result = {
                "id":uid,
                "internal_name":json.loads(r.text)["internalName"],
                "display_name":json.loads(r.text)["displayName"]
            }
            self._cache["getPlayerByID:" + str(uid)] = result
            return result
        except Exception as e:
            return None
        


    def run(self):
        while True:
            if self.client_data.game_phase == GameData.GAME_PHASE__WAITING_FOR_CLIENT:
                self.getConfig()
            elif self.client_data.game_phase == GameData.GAME_PHASE__WAITING_FOR_REGION:
                self.updateRegion()
            elif self.client_data.game_phase == GameData.GAME_PHASE__WAITING_FOR_PLAYER:
                self.updateCurrentPlayer()
            else:
                self.updateGamePhase()
                #self.client_data.myTeamPlayers = TEST
                if self.client_data.game_phase == GameData.GAME_PHASE__CHAMPSELECT:
                    self.updateMyTeamPlayers()
                    self.updateTheirPlayers()
                if self.client_data.game_phase != GameData.GAME_PHASE__INPROGRESS:
                    if self.WAS_IN_GAME == True:
                        self.WAS_IN_GAME = False
                        self.updatePreviousGameID()
                

            time.sleep(GamePhaseWaitingTime[self.client_data.game_phase])


    

    def getConfig(self):
        if os.path.exists("/Applications/League of Legends.app/Contents/LoL/lockfile"):
            lockfile = open("/Applications/League of Legends.app/Contents/LoL/lockfile")
            lockcontent = lockfile.read()
            self.port = lockcontent.split(":")[2]
            self.password = lockcontent.split(":")[3]
            self.baseURL = "https://127.0.0.1:{}".format(self.port)
            self.client_data.game_phase = GameData.GAME_PHASE__WAITING_FOR_REGION
            return True
        else:
            return False

    def updateRegion(self):
        try:
            r = requests.get(self.baseURL + "/riotclient/get_region_locale", verify=False, auth=HTTPBasicAuth('riot', self.password))
            self.client_data.region = json.loads(r.text)['region']
            
            self.client_data.game_phase = GameData.GAME_PHASE__WAITING_FOR_PLAYER
            return True
        except Exception as e:
            return False

    def updateCurrentPlayer(self):
        try:
            r = requests.get(self.baseURL + "/lol-login/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            summonerId = json.loads(r.text)["summonerId"]
            player = self.getPlayerByID(summonerId)
            self.client_data.player = player

            self.client_data.game_phase = GameData.GAME_PHASE__WAITING_FOR_MATCHMAKING
            return True
        except Exception as e:
            return False

    

    def updateGamePhase(self):
        try:
            r = requests.get(self.baseURL + "/lol-gameflow/v1/gameflow-phase", verify=False, auth=HTTPBasicAuth('riot', self.password))
            phase = r.text[1:-1]
            if phase in ["Matchmaking", "ReadyCheck"]:
                self.client_data.game_phase = GameData.GAME_PHASE__MATCHMAKING
            elif phase in ["ChampSelect"]:
                self.client_data.game_phase = GameData.GAME_PHASE__CHAMPSELECT
            elif phase in ["InProgress"]:
                self.client_data.game_phase = GameData.GAME_PHASE__INPROGRESS
                self.WAS_IN_GAME = True
            elif phase in ["WaitingForStats", "PreEndOfGame"]:
                self.client_data.game_phase = GameData.GAME_PHASE__PREENDOFGAME
            else:
                self.client_data.game_phase = GameData.GAME_PHASE__WAITING_FOR_MATCHMAKING
            return True
        except Exception as e:
            self.client_data.game_phase = GameData.GAME_PHASE__WAITING_FOR_CLIENT
            return False     

    def updateMyTeamPlayers(self):
        try:
            r = requests.get(self.baseURL + "/lol-champ-select/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            r = json.loads(r.text)
            players = []
            for player in r['myTeam']:
                p1 = self.getPlayerByID( int(player['summonerId']) )
                p1['assigned_role'] = player['assignedPosition']
                p1['champion_id'] = player['championId']
                players.append(p1)
            self.client_data.myTeamPlayers = players
            return True
        except Exception as e:
            print(e)
            return False

    def updateTheirPlayers(self):
        try:
            r = requests.get(self.baseURL + "/lol-champ-select/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            r = json.loads(r.text)
            players = []
            for player in r['theirTeam']:
                p1 = self.getPlayerByID( 0 )
                p1['assigned_role'] = player['assignedPosition']
                p1['champion_id'] = player['championId']
                players.append(p1)
            self.client_data.theirTeamPlayers = players
            return True
        except Exception as e:
            print(e)
            return False

    def updatePreviousGameID(self):
        try:
            print("called")
            r = requests.get(self.baseURL + "/lol-match-history/v1/delta", verify=False, auth=HTTPBasicAuth('riot', self.password))
            previous_game_id = json.loads(r.text)['deltas'][0]['gameId']
            self.client_data.previous_game_id = previous_game_id
        except Exception as e:
            return None



    
def main():
    print(GameData.GAME_PHASE__WAITING_FOR_CLIENT.value)

        
if __name__ == '__main__':
    main()