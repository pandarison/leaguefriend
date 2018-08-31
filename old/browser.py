# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-02 10:22:39
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-27 10:37:11

import toga
from toga.style.pack import *
import time, threading
import PyObjCTools.AppHelper
import subprocess
from xmlrpc.server import SimpleXMLRPCServer
from processors import *
from league_champions import DATA_CHAMPION_ID_TO_NAME

__DEBUG__ = True
__LOG__ = ""





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
    def log(self, info):
        global __LOG__
        __LOG__ = __LOG__ + info + "\n"
        self.debug_webview.set_content("", __LOG__)

    def setSummoners(self, summoners):
        self.summoners = summoners

    def change_option(self, *args, **kwargs):
        args[0].refresh()
        self.view = kwargs['option'].children[0]
        #self.view = kwargs[0]

    def rpc_process(self, data):

        data = eval(data)
        if data['option'] == "ChampSelect-Update":
            team1 = []
            for champID in data['data']['team1']:
                team1.append(DATA_CHAMPION_ID_TO_NAME[str(champID)])
            PyObjCTools.AppHelper.callLater(0.1, self.webview_runes.evaluate, "app.team1={}".format(str(team1)))
            team2 = []
            for champID in data['data']['team2']:
                team2.append(DATA_CHAMPION_ID_TO_NAME[str(champID)])
            PyObjCTools.AppHelper.callLater(0.1, self.webview_runes.evaluate, "app.team2={}".format(str(team2)))
        return None
            


    def rpc_server(self):
        print("started rpc.")
        server = SimpleXMLRPCServer(("localhost", 8913))
        server.register_function(self.rpc_process, "call")
        server.serve_forever()

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
            for func in [processor_ProfessorGG,processor_OPGG, processor_LeagueFriend]:
                url, script, site = func(self.summoners['data'], self.summoners['region'])
                webview = BrowserWebview(style=Pack(flex=1))
                webview.setData(url, script)
                container.add(site, toga.Box(children=[webview], style=Pack(flex=1)))
                if not self.view:
                    self.view = webview
                if func == processor_LeagueFriend:
                    self.webview_runes = webview


        if self.summoners['option'] == 'postgame':
            for func in [processor_BlitzPostGame]:
                url, script, site = func(self.summoners['data'], self.summoners['region'])
                webview = BrowserWebview(style=Pack(flex=1))
                webview.setData(url, script)
                #webview.url = url
                container.add(site, toga.Box(children=[webview], style=Pack(padding="5")))
                if not self.view:
                    self.view = webview

        global __DEBUG__
        if __DEBUG__:
            self.debug_webview = toga.WebView(style=Pack(flex=1))
            container.add("DEBUG", toga.Box(children=[self.debug_webview], style=Pack(flex=1)))
            self.log("Started. 1")
            self.log("Started. 2")

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

        # start rpc
        if self.summoners['option'] == 'pregame':
            rpc_thread = threading.Thread(target=self.rpc_server)
            rpc_thread.start()

        # Show the main window
        self.main_window.show()








def open_browser(summoner_str):
    print(summoner_str)
    browser = Browser('League Friend', 'org.leaguefriend', icon="resources/app.icns")
    browser.setSummoners(eval(summoner_str))
    browser.main_loop()

if __name__ == '__main__':
    import sys
    import AppKit
    AppKit.NSBundle.mainBundle().infoDictionary()['NSAppTransportSecurity'] = dict(NSAllowsArbitraryLoads = True)

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
