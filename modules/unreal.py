import ConfigParser
import os.path
import sys
import urllib
import subprocess
import tarfile
from jinja2 import Template
from screenutils import list_screens, Screen

from modules.gameserver import GameServer

parser = ConfigParser.RawConfigParser()

class Unreal(GameServer):
    def __init__(self, gsconfig):
        # Bring the gsconfig and path variables over
        super(GameServer, self).__init__()
        self.steam_appid = self.gsconfig['steamcmd']['appid']

    def configure(self):
        config_options = [
            {'option': 'ip', 'info': 'Gameserver IP: [0.0.0.0] ', 'default': '0.0.0.0'},
            {'option': 'hostname', 'info': 'Gameserver Hostname: [My Gameserver] ', 'default': 'My Gameserver'},
        ]
