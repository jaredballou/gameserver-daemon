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
CONFIG_FILE = "server.conf"

# Dictionary of game subdirectories for configuration
# Also used for the game name in srcds launching
GAME = {
    '4020': 'garrysmod',
}

class GSModServer(GameServer):
    def __init__(self, gsconfig):
        # Bring the gsconfig and path variables over
        super(GameServer, self).__init__()
        self.gsconfig = gsconfig
        self.steam_appid = self.gsconfig['steamcmd']['appid']
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
        config_options =  [
            {'option': 'workshop', 'info': 'Workshop collection ID: ', 'default': '0'},
            {'option': 'gamemode', 'info': 'Desired Gamemode: [none] ', 'default': 'ignore'},
        ]
        parser.read(CONFIG_FILE)
        myid = {'id': self.steam_appid}
        self.configure_list(myid,config_options)
        parser.write(open(CONFIG_FILE, 'w'))
        print "Configuration saved as {}".format(CONFIG_FILE)

    def status(self):
        """
        Method to check the server's status
        """
        steam_appid = self.gsconfig['steamcmd']['appid']
        s = Screen(steam_appid)
        is_server_running = s.exists
        return is_server_running

    def start(self):
        steam_appid = self.gsconfig['steamcmd']['appid']
        # Steamapi key provided, check for workshop content
        if self.gsconfig['steamcmd']['steamapi'] != 'ignore' and self.gsconfig[steam_appid]['workshop'] != 'ignore':
            srcds_launch = '-game {game} ' \
                           '-console -usercon -secure -autoupdate '\
                           '-steam_dir {steam_dir} ' \
                           '-steamcmd_script {runscript} '\
                           '-maxplayers {maxplayers} '\
                           '+port {port} '\
                           '+ip {ip} ' \
                           '+map {map} ' \
                           '+gamemode {gamemode} ' \
                           '+host_workshop_collection {workshop} ' \
                           '-authkey {authkey}' \
                           .format(game=GAME[steam_appid],
                                   steam_dir=self.path['steamcmd'],
                                   runscript='runscript.txt',
                                   maxplayers=self.gsconfig[steam_appid]['maxplayers'],
                                   port=self.gsconfig[steam_appid]['port'],
                                   ip=self.gsconfig[steam_appid]['ip'],
                                   map=self.gsconfig[steam_appid]['map'],
                                   workshop=self.gsconfig[steam_appid]['workshop'],
                                   gamemode=self.gsconfig[steam_appid]['gamemode'],
                                   authkey=self.gsconfig['steamcmd']['steamapi'],
                                  )
            extra_parameters = ''
        else:
            srcds_launch = '-game {game} ' \
                           '-console -usercon -secure -autoupdate ' \
                           '-steam_dir {steam_dir} ' \
                           '-steamcmd_script {runscript} ' \
                           '-maxplayers {maxplayers} ' \
                           '+port {port} ' \
                           '+ip {ip} ' \
                           '+map {map} ' \
                           .format(game=GAME[steam_appid],
                                   steam_dir=self.path['steamcmd'],
                                   runscript='runscript.txt',
                                   maxplayers=self.gsconfig[steam_appid]['maxplayers'],
                                   port=self.gsconfig[steam_appid]['port'],
                                   ip=self.gsconfig[steam_appid]['ip'],
                                   map=self.gsconfig[steam_appid]['map'],
                                  )
            extra_parameters = ''

        srcds_run = '{path}/srcds_run {launch} {extra}' \
                    .format(path=self.path['game'],
                            launch=srcds_launch,
                            extra=extra_parameters
                           )
        s = Screen(steam_appid, True)
        s.send_commands(srcds_run)


    def stop(self):
        """
        Method to stop the server.
        """
        # Steam appid
        steam_appid = self.gsconfig['steamcmd']['appid']
        if self.status():
            s = Screen(steam_appid)
            s.kill()
            print "Server stopped."
        else:
           print "Server is not running."
