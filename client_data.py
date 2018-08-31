# -*- coding: utf-8 -*-
# @Author: Pandarison
# @Date:   2018-08-28 15:23:14
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-30 20:15:42

import PyObjCTools.AppHelper
from enum import Enum


class GameData(Enum):
    # Game phases
    GAME_PHASE__WAITING_FOR_CLIENT = "Waiting for LOL Client"
    GAME_PHASE__WAITING_FOR_REGION = "Client Launched"
    GAME_PHASE__WAITING_FOR_PLAYER = "Region Detected"
    GAME_PHASE__WAITING_FOR_MATCHMAKING = "Waiting For Matchmaking"
    GAME_PHASE__MATCHMAKING = "Matchmaking"
    GAME_PHASE__CHAMPSELECT = "Champion Select"
    GAME_PHASE__INPROGRESS = "In Game"
    GAME_PHASE__PREENDOFGAME = "Waiting For Stats"
    GAME_PHASE__OTHER = "IDLE"

GamePhaseWaitingTime = {
    GameData.GAME_PHASE__WAITING_FOR_CLIENT:10,
    GameData.GAME_PHASE__WAITING_FOR_REGION:3,
    GameData.GAME_PHASE__WAITING_FOR_PLAYER:3,
    GameData.GAME_PHASE__WAITING_FOR_MATCHMAKING:30,
    GameData.GAME_PHASE__MATCHMAKING:5,
    GameData.GAME_PHASE__CHAMPSELECT:5,
    GameData.GAME_PHASE__INPROGRESS:30,
    GameData.GAME_PHASE__PREENDOFGAME:5,
    GameData.GAME_PHASE__OTHER:30
}

class ClientDataValue(object):
    def __init__(self, value):
        self.listeners = []
        self._value = value


    def addListener(self, func):
        self.listeners.append(func)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if self._value != new_value:
            print("value changed from {} to {}".format(self._value, new_value))
            self._value = new_value
            for func in self.listeners:
                PyObjCTools.AppHelper.callAfter(func)
            



class ClientData(object):

    def __init__(self):
        self.initialise_data()
        # test

    def initialise_data(self):
        self._data = {
            "region":ClientDataValue(""),
            "game_phase":ClientDataValue(GameData.GAME_PHASE__WAITING_FOR_CLIENT),
            "player":{
                "id":ClientDataValue(0),
                "internal_name":ClientDataValue(""),
                "display_name":ClientDataValue("")
            },
            "myTeamPlayers":ClientDataValue([]),
            "theirTeamPlayers":ClientDataValue([]),
            "previous_game_id":ClientDataValue(0)
        }

    @property
    def region(self):
        return self._data['region'].value

    @region.setter
    def region(self, value):
        self._data['region'].value = value

    @property
    def game_phase(self):
        return self._data['game_phase'].value

    @game_phase.setter
    def game_phase(self, value):
        self._data['game_phase'].value = value

    @property
    def previous_game_id(self):
        return self._data['previous_game_id'].value

    @previous_game_id.setter
    def previous_game_id(self, value):
        self._data['previous_game_id'].value = value

    @property
    def player(self):
        return self._data['player']

    @player.setter
    def player(self, value):
        self._data['player']['id'].value = value['id']
        self._data['player']['internal_name'].value = value['internal_name']
        self._data['player']['display_name'].value = value['display_name']

    @property
    def myTeamPlayers(self):
        return self._data['myTeamPlayers'].value

    @myTeamPlayers.setter
    def myTeamPlayers(self, value):
        self._data['myTeamPlayers'].value = value

    @property
    def theirTeamPlayers(self):
        return self._data['theirTeamPlayers'].value

    @theirTeamPlayers.setter
    def theirTeamPlayers(self, value):
        self._data['theirTeamPlayers'].value = value


    ##
    ## Listeners
    ##
    def add_listener_on_game_phase_change(self, func):
        self._data['game_phase'].addListener(func)
    def add_listener_on_region_change(self, func):
        self._data['region'].addListener(func)
    def add_listener_on_player_change(self, func):
        self._data['player']['display_name'].addListener(func)
    def add_listener_on_myTeamPlayers_change(self, func):
        self._data['myTeamPlayers'].addListener(func)
    def add_listener_on_theirTeamPlayers_change(self, func):
        self._data['theirTeamPlayers'].addListener(func)
    def add_listener_on_previous_game_change(self, func):
        self._data['previous_game_id'].addListener(func)

        

