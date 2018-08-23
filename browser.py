# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-02 10:22:39
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-23 16:15:23

import urllib.parse
import toga
from toga.style.pack import *
import time, threading
import PyObjCTools.AppHelper
import subprocess

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

browser = None

def processor_ProfessorGG(summoners, region):
    url = 'https://porofessor.gg/pregame/{}/'.format(region.lower())
    for player in summoners:
        url = url + "{},".format(urllib.parse.quote(player['internal_name'])) 

    #browser.app
    #$("body").attr("style", "background-color: #FFFFFF"); $(".site-content-bg").attr("style", "background-color: #FFFFFF");
    script = """$("body").attr("style", "background-color: #E3E3E3"); $(".site-content-bg").attr("style", "background-color: #E3E3E3"); $(".site-header").remove();$("#shareinfobanner").remove();$(".site-content-header").remove();$(".site-header-bottom-margin").remove();$("#vmv3-ad-manager").remove(); $(".site-footer").remove(); $("#bigTooltip").remove(); $(".card-5 .cardHeader a").each(
    function(index, element){
"""

    for player in summoners:
        script += "if($(this).html().trim() == \"___SUMMONERNAME___\"){$(this).append(\"<span style='color:rgb(107, 24, 20)'>[___SUMMONERPOSITION___]</span>\");}"
        script = script.replace("___SUMMONERNAME___", player['display_name'])
        script = script.replace("___SUMMONERPOSITION___", player['assigned_role'])
    site = "Professor.GG"
    script += """    }
);"""
    return url, script, site


def processor_OPGG(summoners, region):
    url = 'http://{}.op.gg/multi/query='.format(region.lower())
    for player in summoners:
        url = url + "{}%2C".format(urllib.parse.quote(player['internal_name'])) 

    #$("body").attr("style", "background-color: #FFFFFF"); $(".site-content-bg").attr("style", "background-color: #FFFFFF");
    script = """$("body").attr("style", "background-color: #E3E3E3");
    $(".l-wrap").attr("style", "background-color: #E3E3E3");
    $(".banner_banner--3pjXd").remove();
$("#pnetContVid").remove();
$(".l-header").remove();
$(".l-menu").remove();
$(".PageHeaderWrap").remove();
$(".Header").remove();
$(".life-owner").remove();
$(".l-footer").remove();
$("#hs-beacon").remove();
$("body").attr("style","padding-top:0");"""
    
    site = "OP.GG"
    
    for player in summoners:
        script += "$('.SummonerName').each(function(index, element){if($(this).html() == '___SUMMONERNAME___'){$(this).append(\"<span style='color:rgb(107, 24, 20)'> [___SUMMONERPOSITION___]</span>\");} });"
        script = script.replace("___SUMMONERNAME___", player['display_name'])
        script = script.replace("___SUMMONERPOSITION___", player['assigned_role'])
    return url, script, site


def processor_BlitzPostGame(data, region):
    global REGION_CODE
    url = 'https://app.blitz.gg/lol/match/{}/{}/{}'.format(REGION_CODE[region], urllib.parse.quote(data['playerName']), str(data['gameID']))
    script = """(function() {
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
    site = "Blitz.GG"
    return url, script, site


class BrowserWebview(toga.WebView):

    def __init__(self, *args, **kwargs):
        super(BrowserWebview, self).__init__(*args, **kwargs)
        self.on_webview_load = self.runScript
        

    def setData(self, url, script):
        self.url = url
        self.script = script

    def runScript(self, e):
        PyObjCTools.AppHelper.callLater(0.1, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(1.5, self.evaluate, self.script)
        PyObjCTools.AppHelper.callLater(3, self.evaluate, self.script)



class Browser(toga.App):

    def setSummoners(self, summoners):
        self.summoners = summoners

    def change_option(self, *args, **kwargs):
        args[0].refresh()
        self.view = kwargs['option'].children[0]
        #self.view = kwargs[0]

    def setClipboardData(self, e):
        process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(self.view.url.encode())

    def startup(self):
        self.main_window = toga.MainWindow(title=self.name, size=(1280,800))

        container = toga.OptionContainer(on_select=self.change_option, style=Pack(flex=1))


        copy_url = toga.Command(
            self.setClipboardData,
            label="Copy URL",
            tooltip='Copy the current URL'
        )

        self.commands.add(copy_url)
        self.view = None
        
        if self.summoners['option'] == 'pregame':
            for func in [processor_ProfessorGG,processor_OPGG]:
                url, script, site = func(self.summoners['data'], self.summoners['region'])
                webview = BrowserWebview(style=Pack(flex=1))
                webview.setData(url, script)
                container.add(site, toga.Box(children=[webview], style=Pack(flex=1)))
                if not self.view:
                    self.view = webview

        if self.summoners['option'] == 'postgame':
            for func in [processor_BlitzPostGame]:
                url, script, site = func(self.summoners['data'], self.summoners['region'])
                webview = BrowserWebview(style=Pack(flex=1))
                webview.setData(url, script)
                #webview.url = url
                container.add(site, toga.Box(children=[webview], style=Pack(padding="5")))
                if not self.view:
                    self.view = webview


        box = toga.Box(
            children=[
                container
            ],
            style=Pack(
                direction=COLUMN,
                padding="10",
                flex=1
            )
        )

        self.main_window.content = box

        # Show the main window
        self.main_window.show()








def open_browser(summoner_str):
    print(summoner_str)
    browser = Browser('League Friend', 'org.leaguefriend', icon="resources/app.icns")
    browser.setSummoners(eval(summoner_str))
    browser.main_loop()

if __name__ == '__main__':
    import sys
    arecco = {
        "internal_name":"arecco",
        "display_name":"arecco",
        "assigned_role":"top"
    }
    sonamilol = {
        "internal_name":"sonamilol",
        "display_name":"Sonami LOL",
        "assigned_role":"support"
    }

    summoner_str = str({'option':'pregame', 'region':'EUW', 'data':[arecco, sonamilol]})
    #summoner_str = str({'option':'postgame', 'data':{'gameID':'3728820308', 'playerName':'arecco'}})

    if len(sys.argv) > 1:
        summoner_str = sys.argv[1]
    open_browser(summoner_str)
