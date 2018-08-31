# -*- coding: utf-8 -*-
# @Author: Pandarison
# @Date:   2018-08-29 11:54:53
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-30 22:39:58

import toga
import urllib.parse
import os
from league_champions import DATA_CHAMPION_ID_TO_NAME
import PyObjCTools.AppHelper

REGION_CODE = {
    "BR":"br1",
    "EUNE":"eun1",
    "EUW":"euw1",
    "JP":"jp1",
    "KR":"kr",
    "LAN":"la1",
    "LAS":"la2",
    "NA":"na1",
    "OCE":"oc1",
    "TR":"tr1",
    "RU":"ru",
    "PBE":"pbe1"
}

class ProfessorGG(toga.WebView):
    def __init__(self, client_data, *args, **kwargs):
        super(ProfessorGG, self).__init__(*args, **kwargs)
        self.client_data = client_data
        self.site = "Professor.GG"
        self.client_data.add_listener_on_myTeamPlayers_change(self.updateURL)
        self.client_data.add_listener_on_player_change(self.defaultURL)
        self.default_page = True
        self.script = ""
        self.on_webview_load = self.runScript

    def runScript(self, e):
        PyObjCTools.AppHelper.callLater(0.1, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(1.5, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(3, self.evaluate, self.script)

    def defaultURL(self):
        if self.default_page:
            self.default_page = False
            self.url = 'https://www.leagueofgraphs.com/summoner/{}/{}'.format(self.client_data.region.lower(), self.client_data.player['internal_name'].value)
            self.script = """$("#topnavbar").remove();
                            $("#ifrmDiv").remove();
                            $("#cdm-zone-01").remove();
                            $("#cdm-zone-03").remove();
                            $("#cdm-zone-06").remove();
                            $(".app_gdpr--2k2uB").remove(); 
                            $("#footer").remove();
                            $("#sidebar-container").remove();
                            $("#filters-menu").remove();
                            $("#override_POROFESSORINFOBANNER0").remove();
                            $("body").css("background", "none");
                            $("body").css("background-color", "#E3E3E3");
                            $('#pageContent').each(function () {
                                this.style.setProperty( 'width', '100%', 'important' );
                                this.style.setProperty( 'margin-top', '5px', 'important' );
                            });
                            if($("#matchTable").length != 0 && $("#leaguefriend").length == 0) {$("#mainContentContainer").prepend("<button id='leaguefriend' type='button' class='see_more_ajax_button' style='margin-bottom:10px'><a href='javascript:history.back()' style='color:white'>Go Back</a></button>");}
                            """

    def updateURL(self):
        url = 'https://porofessor.gg/pregame/{}/'.format(self.client_data.region.lower())
        for player in self.client_data.myTeamPlayers:
            url = url + "{},".format(urllib.parse.quote(player['internal_name']))
        if self.url != url: 
            self.script = """$("body").attr("style", "background-color: #E3E3E3"); $(".site-content-bg").attr("style", "background-color: #E3E3E3"); $(".site-header").remove();$("#shareinfobanner").remove();$(".site-content-header").remove();$(".site-header-bottom-margin").remove();$("#vmv3-ad-manager").remove(); $(".site-footer").remove(); $("#bigTooltip").remove(); $(".card-5 .cardHeader a").each(function(index, element){"""
            for player in self.client_data.myTeamPlayers:
                self.script += "if($(this).html().trim() == \"___SUMMONERNAME___\"){$(this).append(\"<span style='color:rgb(107, 24, 20)'>[___SUMMONERPOSITION___]</span>\");}"
                self.script = self.script.replace("___SUMMONERNAME___", player['display_name'])
                self.script = self.script.replace("___SUMMONERPOSITION___", player['assigned_role'])
            self.script += "});"
            self.url = url

class BlitzGG(toga.WebView):
    def __init__(self, client_data, *args, **kwargs):
        super(BlitzGG, self).__init__(*args, **kwargs)
        self.client_data = client_data
        self.site = "Previous Game [Blitz.GG]"
        self.client_data.add_listener_on_previous_game_change(self.updateURL)
        self.script = ""
        self.on_webview_load = self.runScript

    def runScript(self, e):
        PyObjCTools.AppHelper.callLater(0.1, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(1.5, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(3, self.evaluate, self.script)

    def updateURL(self):
        url = 'https://app.blitz.gg/lol/match/{}/{}/{}'.format(REGION_CODE[self.client_data.region], urllib.parse.quote(self.client_data.player['internal_name'].value), str(self.client_data.previous_game_id))

        if self.url != url: 
            self.script = """(function() {
            // Load the script
            var script = document.createElement("SCRIPT");
            script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js';
            script.type = 'text/javascript';
            script.onload = function() {
                var $ = window.jQuery;
                $('div').filter(function() {
                    var self = $(this);
                    return self.height() === 60 &&
                           self.css('flex-direction') === 'row' &&
                           self.css('max-width') === '1440px' &&
                           self.css('display') === 'flex';
                }).remove();
                $('div').filter(function() {
                    var self = $(this);
                    return self.height() === 38 &&
                           self.css('position') === 'relative' &&
                           self.css('padding-right') === '16px' &&
                           self.css('display') === 'flex';
                }).remove();
            };
            document.getElementsByTagName("head")[0].appendChild(script);
            })();"""
            self.url = url


class LeagueFriendRunePage(toga.WebView):
    def __init__(self, client_data, *args, **kwargs):
        super(LeagueFriendRunePage, self).__init__(*args, **kwargs)
        self.client_data = client_data
        self.site = "Runes"
        self.url = "file://" + os.path.realpath('./resources/runes/index.html')
        self.client_data.add_listener_on_myTeamPlayers_change(self.updateChampions1)
        self.client_data.add_listener_on_theirTeamPlayers_change(self.updateChampions2)


    def updateChampions1(self):
        team1 = []
        for player in self.client_data.myTeamPlayers:
            if player['champion_id'] != 0:
                team1.append(DATA_CHAMPION_ID_TO_NAME[str(player['champion_id'])])
        self.evaluate("app.team1={};".format(str(team1)))

    def updateChampions2(self):
        team2 = []
        for player in self.client_data.theirTeamPlayers:
            if player['champion_id'] != 0:
                team2.append(DATA_CHAMPION_ID_TO_NAME[str(player['champion_id'])])
        self.evaluate("app.team2={};".format(str(team2)))






