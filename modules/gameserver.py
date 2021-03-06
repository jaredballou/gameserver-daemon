import ConfigParser
import os.path
import sys
import urllib
import subprocess
import tarfile
from jinja2 import Template
from screenutils import list_screens, Screen

# Important constants within the class
CONFIG_FILE = "server.conf"
STEAMCMD_DOWNLOAD = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"

# Dictionary of game subdirectories for configuration
# Also used for the game name in srcds launching
GAME = {
    '232250': 'tf',
    '740': 'csgo',
    '232370': 'hl2mp',
    '346680': 'bms',
    '222860': 'left4dead2',
    '376030': 'ShooterGame',
    '4020': 'gsmod',
    '276060': 'svencoop',
}

# Configuration parser variable. Don't touch this.
parser = ConfigParser.RawConfigParser()

class GameServer(object):
    """docstring for GameServer"""
    def __init__(self, gsconfig):
        super(GameServer, self).__init__()
        self.gsconfig = gsconfig
        if self.gsconfig:
            self.path = {
                'steamcmd': os.path.join(self.gsconfig['steamcmd']['path'], ''),
                'game': os.path.join(self.gsconfig['steamcmd']['path'], self.gsconfig['steamcmd']['appid']),
            }
    def configure_list(self, group, options):
        """
        Method used to loop through configuration lists and prompt the user
        """
        for config_object in options:
            while True:
                user_input = raw_input(config_object['info'])
                if user_input:
                    if config_object.get('valid_option') and not user_input in config_object['valid_option']:
                        print "Invalid option. Please chose one of the following: {}".format(config_object['valid_option'])
                    else:
                        group[config_object['option']] = user_input
                        break
                if not config_object.get('default', None):
                    #loop back and ask again
                    pass
                else:
                    # Default value set!
                    group[config_object['option']] = config_object['default']
                    break
            parser.set(group['id'], config_object['option'], group[config_object['option']])

    def configure(self):
        """
        configure docstring
        """
        # Configure the base srcds setup
        configure_options = [
            {'option': 'user', 'info': 'Steam login: [anonymous] ', 'default': 'anonymous'},
            {'option': 'password', 'info': 'Steam password: [anonymous] ', 'default': 'anonymous'},
            {'option': 'path', 'info': 'Gameserver base path: (example: /home/steam/mygame.mydomain.com) '},
            {'option': 'appid', 'info': 'Steam AppID: '},
            {'option': 'steamapi', 'info': 'Steam API Key (for workshop content) [none] ', 'default': 'ignore'},
            {'option': 'engine', 'info': 'Gameserver engine (srcds / unreal / hlds): [srcds] ', 'default': 'srcds', 'valid_option': ['unreal', 'srcds', 'hlds']},
        ]
        steamcmd = {'id': 'steamcmd'}
        parser.add_section('steamcmd')
        self.configure_list(steamcmd,configure_options)
        parser.write(open(CONFIG_FILE, 'w'))
        print "Base configuration file saved as {}".format(CONFIG_FILE)

    def install_steamcmd(self):
        """
        Method to install steamcmd from the web. Modify STEAMCMD_DOWNLOAD if the
        link changes. STEAMCMD_DOWNLOAD can be found at the top of this class file.
        """
        if self.gsconfig:
            while True:
                if os.path.exists(self.path['steamcmd']):
                    INSTALL_DIR = os.path.dirname(self.path['steamcmd'])
                    #Download steamcmd and extract it
                    urllib.urlretrieve(STEAMCMD_DOWNLOAD, os.path.join(INSTALL_DIR, 'steamcmd_linux.tar.gz'))
                    steamcmd_tar = tarfile.open(os.path.join(INSTALL_DIR, 'steamcmd_linux.tar.gz'), 'r:gz')
                    steamcmd_tar.extractall(INSTALL_DIR)
                    break
                else:
                    # Create the directory
                    os.makedirs(self.path['steamcmd'])
            print "Steamcmd installed to {dir}".format(dir=self.path['steamcmd'])
        else:
            print "Error: No configuration file found. Please run with the --configure option"

    def update_game_validate(self):
        """
        Method to update game files with the validate option
        """
        steamcmd_run = '{steamcmdpath}steamcmd.sh ' \
                       '+login {login} {password} ' \
                       '+force_install_dir {installdir} ' \
                       '+app_update {id} ' \
                       'validate ' \
                       '+quit' \
                       .format(steamcmdpath=self.path['steamcmd'],
                               login=self.gsconfig['steamcmd']['user'],
                               password=self.gsconfig['steamcmd']['password'],
                               installdir=self.path['game'],
                               id=self.gsconfig['steamcmd']['appid']
                              )
        subprocess.call(steamcmd_run, shell=True)

    def update_game_novalidate(self):
        """
        Method to update game files without the validate option
        """
        steamcmd_run = '{steamcmdpath}steamcmd.sh ' \
                       '+login {login} {password} ' \
                       '+force_install_dir {installdir} ' \
                       '+app_update {id} '\
                       '+quit' \
                       .format(steamcmdpath=self.path['steamcmd'],
                               login=self.gsconfig['steamcmd']['user'],
                               password=self.gsconfig['steamcmd']['password'],
                               installdir=self.path['game'],
                               id=self.gsconfig['steamcmd']['appid']
                              )
        subprocess.call(steamcmd_run, shell=True)

    def install_content(self):
        """
        Installs content for a game. Doesn't care about the content.
        This is useful for installing garry's mod content
        """
        # Query the user for information regarding the content install
        while True:
            path = raw_input('Content path: ')
            if path:
                if os.path.exists(path):
                    break
                else:
                    os.makedirs(path)
                    break
        while True:
            appid = raw_input('Steam APPID: ')
            if appid:
                break

        steamcmd_run = '{steamcmdpath}steamcmd.sh ' \
                       '+login {login} {password} ' \
                       '+force_install_dir {installdir} ' \
                       '+app_update {id} ' \
                       '+quit' \
                       .format(steamcmdpath=self.path['steamcmd'],
                               login=self.gsconfig['steamcmd']['user'],
                               password=self.gsconfig['steamcmd']['password'],
                               installdir=path,
                               id=appid
                              )
        subprocess.call(steamcmd_run, shell=True)
