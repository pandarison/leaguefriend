# -*- coding: utf-8 -*-
# @Author: Pandarison
# @Date:   2018-08-27 20:24:10
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-31 22:40:57

from AppKit import NSStatusBar, NSVariableStatusItemLength, NSLog, NSImage, NSMenu, NSMenuItem
import PyObjCTools.AppHelper

import os, shutil
import threading,time
import tempfile

import toga
from toga.style.pack import *
from toga_cocoa.libs import objc_method
from toga_cocoa.window import WindowDelegate
from toga_cocoa.app import AppDelegate
from rubicon.objc.eventloop import EventLoopPolicy, CocoaLifecycle
import requests

from client_data import ClientData
from monitor import LeagueMonitor
from views import *
import updater

__VERSION__ = 1.3




class MyWindowDelegate(WindowDelegate):
    @objc_method
    def windowShouldClose_(self, notification) -> bool:
        self.impl._impl.native.orderOut(None)
        return False

class MyAppDelegate(AppDelegate):
    @objc_method
    def applicationOpenUntitledFile_(self, sender) -> bool:
        self.interface.main_window._impl.native.orderFront(None)
        return True

    @objc_method
    def update_(self):
        self.interface.on_update()

    @objc_method
    def quit_(self):
        self.interface.on_quit()

    @objc_method
    def about_(self):
        self.interface.on_about()

    @objc_method
    def applicationDidFinishLaunching_(self, notification):
        self.native.activateIgnoringOtherApps(True)
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusItem.setHighlightMode_(True)
        self.statusItem.setEnabled_(True)

        self.icon = NSImage.alloc().initByReferencingFile_("resources/app.icns")
        self.icon.setSize_((20,20))
        self.statusItem.setImage_(self.icon)

        self.menu = NSMenu.alloc().init()

        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Check For Updates", "update:", "")
        self.menu.addItem_(item)
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("About", "about:", "")
        self.menu.addItem_(item)
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "quit:", "")
        self.menu.addItem_(item)

        self.statusItem.setMenu_(self.menu)




class Browser(toga.App):

    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)
        self.client_data = ClientData()
        self.monitor = LeagueMonitor(self.client_data)
        self.client_data.add_listener_on_region_change(self.on_title_should_change)
        self.client_data.add_listener_on_player_change(self.on_title_should_change)
        self.client_data.add_listener_on_game_phase_change(self.on_title_should_change)
        self.client_data.add_listener_on_myTeamPlayers_change(self.on_title_should_change)
        self.monitor.start()

    def on_title_should_change(self):
        self.debug_label.text = "League Friend [{}] [{}] [{}] [{}]".format(self.client_data.player['display_name'].value, self.client_data.region, self.client_data.game_phase.value, self.client_data.previous_game_id)
        self.debug_label.refresh()

    def change_option(self, *args, **kwargs):
        try:
            args[0].refresh()
        except Exception as e:
            pass

    def on_about(self):
        self.about_window = toga.Window(title="About", size=(200,100))
        
        text = "League Friend\n\nVersion: {}".format(__VERSION__)
        textbox = toga.Label(text=text, style=Pack(flex=1, padding_left="30"))
        self.about_window.content = toga.Box(children=[
                textbox
            ], style=Pack(direction=COLUMN, flex=1, padding="10"))

        self.about_window.show()
    
    def on_update(self):
        global __VERSION__
        latest = updater.getLatestRelease()
        if latest['version'] <= __VERSION__:
            self.main_window.info_dialog(title="Information", message="No update available.")
            return
        self.update_window = toga.Window(title="Update", size=(400,100))

        textbox = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        textbox.value = latest['notes']

        progress_bar = toga.ProgressBar(max=latest['size'], value=0)

        def on_btn_click_later(e):
            self.update_window._impl.close()

        def on_btn_click_now(e):
            def addBarValue(v):
                progress_bar.value += v
            def thread_update_task():
                bundlePath = updater.getBundlePath()
                response = requests.get(latest['url'], stream=True)
                progress_value = 0
                tempFolder = tempfile.TemporaryDirectory()
                with open(tempFolder.name + "/patch.zip", "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            PyObjCTools.AppHelper.callAfter(addBarValue, 1024)

                zip_ref = updater.MyZipFile(tempFolder.name + "/patch.zip", 'r')
                zip_ref.extractall(tempFolder.name + "/patches/")
                zip_ref.close()
                shutil.rmtree(bundlePath)
                shutil.copytree(tempFolder.name + "/patches/LeagueFriend.app", bundlePath)
                tempFolder.cleanup()
                os.system("open -n " + bundlePath)
                self.exit()
            t = threading.Thread(target=thread_update_task)
            t.start()
            




        btn_update_now = toga.Button(label="Update Now", on_press=on_btn_click_now, style=Pack(padding_left="50"))
        btn_update_later = toga.Button(label="Later", on_press=on_btn_click_later, style=Pack(padding_left="10"))

        self.update_window.content = toga.Box(children=[
                toga.Box(children=[
                        toga.Label(text="New update available.", style=Pack(padding_bottom="20", padding_left="5")),
                        btn_update_now,
                        btn_update_later
                    ], style=Pack(direction=ROW, flex=1)),
                toga.Label(text="Release Notes:", style=Pack(padding_bottom="5", padding_left="5")),
                textbox,
                progress_bar
            ], style=Pack(direction=COLUMN, flex=1, padding="10"))

        self.update_window.show()

    def on_quit(self):
        self.exit()

    def startup(self):
        self.main_window = toga.MainWindow(title=self.name, size=(1280,800))
        self.debug_label = toga.Label("Waiting For League of Legends Client.")

        
        #self.main_window.on_close = self.on_window_close
        container = toga.OptionContainer(on_select=self.change_option, style=Pack(flex=1))
        

        # views
        self.webview_professorgg = ProfessorGG(self.client_data, style=Pack(flex=1))
        container.add(self.webview_professorgg.site, toga.Box(children=[self.webview_professorgg], style=Pack(flex=1)))

        self.webview_leaguefriendrunepage = LeagueFriendRunePage(self.client_data, style=Pack(flex=1))
        container.add(self.webview_leaguefriendrunepage.site, toga.Box(children=[self.webview_leaguefriendrunepage], style=Pack(flex=1)))

        self.webview_blitzggpostgame = BlitzGG(self.client_data, style=Pack(flex=1))
        container.add(self.webview_blitzggpostgame.site, toga.Box(children=[self.webview_blitzggpostgame], style=Pack(flex=1)))


        box = toga.Box(
            children=[
                container,
                self.debug_label
            ],
            style=Pack(
                direction=COLUMN,
                padding="5",
                flex=1
            )
        )

        self.main_window.content = box

        # Show the main window
        self.main_window.show()
        
        

    def launch_app(self):
        self._impl.create()
        # When click close button, the following code asks before closing the app
        # Modify window on close
        self.main_window.delegate = MyWindowDelegate.alloc().init()
        self.main_window.delegate.interface = self.main_window
        self.main_window.delegate.impl = self.main_window
        self.main_window._impl.native.setDelegate_(self.main_window.delegate)

        appDelegate = MyAppDelegate.alloc().init()
        appDelegate.interface = self._impl.interface
        appDelegate.native = self._impl.native
        self._impl.native.setDelegate_(appDelegate)
        # End modification
        self._impl.loop.run_forever(lifecycle=CocoaLifecycle(self._impl.native))

        
if __name__ == '__main__':
    browser = Browser('League Friend', 'org.leaguefriend', icon="resources/app.icns")
    #print(dir(browser.main_loop))
    browser.launch_app()


