# -*- coding: utf-8 -*-
# @Author: Pandarison
# @Date:   2018-08-31 14:18:46
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-31 16:56:19

from Foundation import NSBundle
import requests
from zipfile import ZipFile, ZipInfo
import os

class MyZipFile(ZipFile):

    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        os.chmod(ret_val, attr)
        return ret_val

    def extractall(self, path=None, members=None, pwd=None):
        """Extract all members from the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' is optional and must be a subset of the list returned
           by namelist().
        """
        if members is None:
            members = self.namelist()

        if path is None:
            path = os.getcwd()
        else:
            path = os.fspath(path)

        for member in members:
            self.extract(member, path, pwd)

def getBundlePath():
    return NSBundle.mainBundle().bundlePath()

def getLatestRelease():
    r = requests.get("https://api.github.com/repos/pandarison/leaguefriend/releases/latest").json()
    latest_version = float(r['tag_name'])
    latest_version_url = r['assets'][0]['browser_download_url']
    latest_file_size = r['assets'][0]['size']
    latest_release_notes = r['body']
    return {
        "version":latest_version,
        "url":latest_version_url,
        "size":latest_file_size,
        "notes":latest_release_notes
    }
