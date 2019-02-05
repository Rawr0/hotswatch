from abc import ABCMeta, abstractmethod
from multiprocessing.dummy import Pool as ThreadPool
import threading
import sys


# Imports used by plugins
import requests         # NotifyByPushover
import datetime         # NotifyByPushover
import random           # NotifyByPushover

import time             # NotifyByChromecast
import pychromecast     # NotifyByChromecast

import soco             # NotifyBySonos

import json             # NotifyBySMS


# Import Custom Classes
import config as cfg

class Notifier:
    """Base class for all plugins. Singleton instances of subclasses are created automatically and stored in Notifier.plugins class field."""
    plugins = []   

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins.append(cls())

    def internalNotify(self, obj):
        print("Triggering plugin: " + type(obj).__name__ + '\n')
        sys.stdout.flush()
        obj.notify()

    def triggerNotificationThreaded(self):
        enabledPlugins = []

        # Get enabled plugins
        for plugin in self.plugins:
            if type(plugin).__name__ in cfg.PLUGINS_ENABLED:
                enabledPlugins.append(plugin)

        pool = ThreadPool(4)
        pool.map(self.internalNotify, enabledPlugins)
        pool.close()
        pool.join()

    def triggerNotification(self):
        for plugin in self.plugins:
            if type(plugin).__name__ in cfg.PLUGINS_ENABLED:
                print("Triggering plugin: " + type(plugin).__name__)
                plugin.notify()

    @abstractmethod
    def notify(self, *test):
        raise NotImplementedError       

#######################################
## ADD NEW SUBCLASSES BELOW THE LINE
#######################################

# class NotifyByEmail(Notifier):
#     def notify(self):
#       [Put your python code here]

class NotifyByPushover(Notifier):
    def getMessage(self):
        if(hasattr(cfg, 'PUSHOVER_QUOTEFILE') and cfg.PUSHOVER_QUOTEFILE is not None):
            quotes = requests.get(cfg.PUSHOVER_QUOTEFILE)
            message = random.choice(str(quotes.text).split('\n'))
        else:
            message = "It\'s game time"

        return message

    def notify(self):
        # Send a notification
        time = datetime.datetime.now().strftime("%H:%M:%S")
        priority = (1 if cfg.PUSHOVER_HIGHPRIORITY else 0)

        postdata = {'token':cfg.PUSHOVER_TOKEN,
            'user':cfg.PUSHOVER_USER,
            'title':"Heroes of the Storm",
            'message':'👾 ' + self.getMessage() + ' 👾 (' + time + ')',
            'device':cfg.PUSHOVER_DEVICE,
            'priority':priority
        }
        requests.post('https://api.pushover.net/1/messages.json', postdata)

class NotifyByChromecast(Notifier):
    def notify(self):
        chromecasts = pychromecast.get_chromecasts()
        [cc.device.friendly_name for cc in chromecasts]

        try:
            cast = next(cc for cc in chromecasts if cc.device.friendly_name == cfg.CHROMECAST_TARGET)
                
            # Wait for cast device to be ready
            cast.wait()
            mc = cast.media_controller

            cast.set_volume(cfg.CHROMECAST_VOLUME)

            mc.play_media(cfg.CHROMECAST_AUDIO_FILE, 'audio/mp3')        
            mc.block_until_active()        

            mc.pause()
            time.sleep(1)
            mc.play()

        except StopIteration:
            print("NotifyByChromecast Failed - Check CHROMECAST_TARGET and try again (note: variable is case sensitive)")


class NotifyBySonos(Notifier):
    debug = False

    def notify(self):
        players = soco.discover()
        groupleader = None
        speakervolumes = {}     # Take note of all original speaker volumes

        for player in players:
            state = player.get_current_transport_info()["current_transport_state"]
            if(self.debug): print(player.player_name + " " + state)
                        
            if(player.player_name in cfg.SONOS_TARGET_SPEAKERS and (state == "STOPPED" or state == "PAUSED_PLAYBACK")):
                if(groupleader is None):
                    if(self.debug): print(player.player_name + " will be the group leader")
                    groupleader = player
                    groupleader.unjoin()
                else:
                    player.unjoin()
                    player.join(groupleader)

                speakervolumes[player] = player.volume
                player.volume = cfg.SONOS_VOLUME
                
            else:
                if(self.debug): print("Skipping " + player.player_name + " " + state)

        if(groupleader is not None):
            groupleader.volume = cfg.SONOS_VOLUME
            groupleader.play_uri(cfg.SONOS_AUDIO_FILE)
            
            time.sleep(15)

            # Tidy Up
            groupleader.stop()
            for player in groupleader.group:
                player.unjoin()
                player.volume = speakervolumes[player]
              

class NotifyBySMS(Notifier):
    debug = False

    def getMessage(self):
        if(hasattr(cfg, 'PUSHOVER_QUOTEFILE') and cfg.PUSHOVER_QUOTEFILE is not None):
            quotes = requests.get(cfg.PUSHOVER_QUOTEFILE)
            message = random.choice(str(quotes.text).split('\n'))
        else:
            message = "It\'s game time"

        return message

    def notify(self):
        # Send a notification
        time = datetime.datetime.now().strftime("%H:%M:%S")

        postdata = {
            'from':cfg.SMS_SOURCE,
            'to':[cfg.SMS_TARGET],
            'body':'👾 ' + self.getMessage() + ' 👾 (' + time + ')'
        }
        
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(cfg.SMS_TOKEN)
        }

        res = requests.post('https://api.clxcommunications.com/xms/v1/{}/batches'.format(cfg.SMS_PLAN_ID), data=json.dumps(postdata), headers=headers)
        if(self.debug): print(res.text)
