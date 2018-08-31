# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-01 16:23:01
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-27 12:32:56

import requests
from requests.auth import HTTPBasicAuth
import os
import json
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class LeagueMonitor(object):

    def __init__(self):
        if os.path.exists("/Applications/League of Legends.app/Contents/LoL/lockfile"):
            lockfile = open("/Applications/League of Legends.app/Contents/LoL/lockfile")
            lockcontent = lockfile.read()
            self.port = lockcontent.split(":")[2]
            self.password = lockcontent.split(":")[3]
            self.baseURL = "https://127.0.0.1:{}".format(self.port)
            self.available = True
        else:
            self.available = False

    def getRegion(self):
        try:
            r = requests.get(self.baseURL + "/riotclient/get_region_locale", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)['region']
        except Exception as e:
            return None        


    def getClientState(self):
        try:
            r = requests.get(self.baseURL + "/lol-gameflow/v1/gameflow-phase", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return r.text[1:-1]
        except Exception as e:
            return None
        


    def getPlayerNameByID(self, uid):
        try:
            r = requests.get(self.baseURL + "/lol-summoner/v1/summoners/{}".format(uid), verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)["internalName"]
        except Exception as e:
            return None

    def getCurrentPlayer(self):
        r = requests.get(self.baseURL + "/lol-login/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
        summonerId = json.loads(r.text)["summonerId"]
        return self.getPlayerNameByIDFancy(int(summonerId))


    def getCurrentChampSelectSession(self):
        try:
            r = requests.get(self.baseURL + "/lol-champ-select/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)
        except Exception as e:
            return None

    def getPlayerNameByIDFancy(self, uid):
        try:
            r = requests.get(self.baseURL + "/lol-summoner/v1/summoners/{}".format(uid), verify=False, auth=HTTPBasicAuth('riot', self.password))
            return {
                "internal_name":json.loads(r.text)["internalName"],
                "display_name":json.loads(r.text)["displayName"]
            }
        except Exception as e:
            return None

    def getTeammembers(self):
        try:
            r = requests.get(self.baseURL + "/lol-champ-select/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)
        except Exception as e:
            return None

    def getTeammembersFancy(self):
        try:
            r = requests.get(self.baseURL + "/lol-champ-select/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            r = json.loads(r.text)
            result = []
            for player in r['myTeam']:
                p1 = self.getPlayerNameByIDFancy( int(player['summonerId']) )
                p1['assigned_role'] = player['assignedPosition']
                result.append(p1)
            return result
        except Exception as e:
            return None

    def getPreviousGameID(self):
        try:
            r = requests.get(self.baseURL + "/lol-match-history/v1/delta", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)['deltas'][0]['gameId']
        except Exception as e:
            return None

    def getCurrentGameID(self):
        try:
            r = requests.get(self.baseURL + "/lol-gameflow/v1/session", verify=False, auth=HTTPBasicAuth('riot', self.password))
            return json.loads(r.text)['gameData']['gameId']
        except Exception as e:
            return None

    
def main():
    m = LeagueMonitor()

    print(m.getTeammembersFancy())

        
if __name__ == '__main__':
    main()