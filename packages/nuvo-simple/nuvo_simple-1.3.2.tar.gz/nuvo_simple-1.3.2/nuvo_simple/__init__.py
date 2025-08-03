import functools
import logging
import re
import io
import serial
import string
import time
import asyncio
import threading
import numpy as np
import queue
from functools import wraps
from typing import Callable, Coroutine
from threading import RLock

_LOGGER = logging.getLogger(__name__)
'''
#ZxxPWRppp,SRCs,GRPt,VOL-yy
'''
CONSR_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'PWR(?P<power>ON|OFF),'
                     'SRC(?P<source>\\d),'
                     'GRP(?P<group>0|1),'
                     'VOL(?P<volume>-\\d\\d|-MT|-XM)')
'''
#ZzzPWRonoff,SRCs,VOLvvv
'''
STATUS_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'PWR(?P<power>ON|OFF),'
                     'SRC(?P<source>\\d),'
                     'VOL(?P<volume>-\\d\\d|-MT|-XM)')
'''
#ZzzPWROFF
'''
SIMPLESE_OFF_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'PWR(?P<power>ON|OFF)')
'''
#ZxxORp,BASSyy,TREByy,GRPq,VRSTr
'''
ESSENTIA_D_SETSR_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'OR(?P<override>\\d),'
                     'BASS(?P<bass>[+-]?\\d{2}),'
                     'TREB(?P<treble>[+-]?\\d{2}),'
                     'GRP(?P<group>0|1),'
                     'VRST(?P<volume_reset>1|0)')
'''
#Z0x,BASSyy,TREByy,GRPq
'''
SIMPLESE_SETSR_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     '(?P<override>.)'
                     'BASS(?P<bass>[+-]?\\d{2}),'
                     'TREB(?P<treble>[+-]?\\d{2}),'
                     'GRP(?P<group>0|1)')
'''
#ZzzBASSequ,TREBequ,BALbal,Gg,MAXVOLmax,INIVOLini
'''
CONCERTO_SETSR_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'BASS(?P<bass>[+-]?\\d{2}),'
                     'TREB(?P<treble>[+-]?\\d{2}),'
                     'BAL(?P<balance>C|L+\\d|R+\\d),'
                     'G(?P<group>\\d),'
                     'MAXVOL(?P<maxvol>-\\d\\d),'
                     'INIVOL(?P<inivol>-\\d\\d)')
'''
#MPU_E6D_vx.yy
'''
ESSENTIA_D_VERSION = re.compile('MPU_E6D[A-Za-z\t .]+')
'''
#MPU_A4D_vx.yy
'''
SIMPLESE_VERSION = re.compile('MPU_A4D[A-Za-z\t .]+')
'''
#MPU-I8_FWvx.yy
'''
CONCERTO_VERSION = re.compile('MPU-I8_[A-Za-z\t .]+')
'''
#NV-I8G FWvx.yy HWvx
'''
CONCERTO_VERSION2 = re.compile('NV-I8G[A-Za-z\t .]+')
'''
#ALLOFF
'''
ALL_OFF_PATTERN = re.compile('ALLOFF')
'''
#ZxxLKlll
'''
KEYPAD_LOCK_PATTERN = re.compile('Z(?P<zone>\\d{2})'
                     'LK(?P<lock>ON|OFF)')
'''
#?
'''
ERROR_PATTERN = re.compile('\\?')


EOL = b'\r'
TIMEOUT_OP       = 0.2   # Number of seconds before serial operation timeout
TIMEOUT_RESPONSE = 1     # Number of seconds before command response timeout
cmd_queue = queue.Queue()
page_active = np.array([0,0])
zoneinit = np.array([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonesetinit = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonepwr = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonepwrsave = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonepwralloff = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonevol = np.array([-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78])
zonevolsave = np.array([-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78,-78])
zonesrc = np.array([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonesrcsave = np.array([0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
zonemute = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonemutesave = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonelock = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonebass = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonetreble = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonebalance = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonegroupsrc = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
zoneoverride = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
zonevolreset = np.array([0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
zonevoloffset = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
setup = False

class ZoneStatus(object):
    def __init__(self
                 ,zone: int
                 ,power: str
                 ,source: int
                 ,volume: float  # -78 -> 0
                 ,from_port: bool
                 ):
        self.source = str(source)
        self.zone = abs(int(zone))
        self.zonegroup_members = []
        try:
            zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
            zoneindex = int(zoneindexobj[0])
            for grpzonembr in groupzone_members[zoneindex]:
                entityindexobj = [i for i, x in enumerate(media_zonetable) if x == grpzonembr]
                entityindex = int(entityindexobj[0])
                self.zonegroup_members.append(entitytable[entityindex])
        except:
            self.zonegroup_members = None

        if 'ON' in power:
           self.power = bool(1)
        else:
           self.power = bool(0)

        if 'MT' in volume:
           self.mute = bool(1)
           self.volume = zonevol[self.zone]
        else:
           self.mute = bool(0)
           self.volume = int(volume)

        zonepwr[self.zone] = self.power
        zonevol[self.zone] = self.volume
        zonesrc[self.zone] = self.source
        zonemute[self.zone] = self.mute

        _LOGGER.debug('Zone: %s, Power: %s, Vol: %sdb, %s%%, Mute: %s, Source: %s, Init: %s', \
           self.zone, self.power, self.volume, db_to_percent(self.volume), \
           self.mute, self.source, zoneinit[int(self.zone)])

        if from_port:
            if self.zone in media_zonetable:
                callbackobj = media_zonetable.index(self.zone)
                callbackint = int(callbackobj)
                media_callback[callbackint]()

    @classmethod
    def from_string(cls, match):
        ZoneStatus(*[str(m) for m in match.groups()], True)

class ZoneConnectStatus(object):
    def __init__(self
                 ,zone: int
                 ,power: str
                 ,source: int
                 ,group: int
                 ,volume: float  # -78 -> 0
                 ,from_port: bool
                 ):
        self.source = str(source)
        self.zone = abs(int(zone))
        self.zonegroup_members = []
        try:
            zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
            zoneindex = int(zoneindexobj[0])
            for grpzonembr in groupzone_members[zoneindex]:
                entityindexobj = [i for i, x in enumerate(media_zonetable) if x == grpzonembr]
                entityindex = int(entityindexobj[0])
                self.zonegroup_members.append(entitytable[entityindex])
        except:
            self.zonegroup_members = None
        if 'ON' in power:
           self.power = bool(1)
           """ Nuvo does not send update from other zones using source
               grouping.  See if is enabled and if so, update the other
               zones that are powered on. """
           if zonegroupsrc[self.zone] == 0:
               for count in range(1,13):
                   if zonegroupsrc[count] == 0 and zonepwr[count] == 1:
                       if int(zonesrc[count]) != int(self.source):
                           zonesrc[count] = self.source
                           if count in media_zonetable:
                               callbackobj = media_zonetable.index(count)
                               callbackint = int(callbackobj)
                               media_callback[callbackint]()

        else:
           self.power = bool(0)

        if 'MT' in volume:
           self.mute = bool(1)
           self.volume = zonevol[self.zone]
        else:
           self.mute = bool(0)
           self.volume = int(volume)

        zonepwr[self.zone] = self.power
        zonevol[self.zone] = self.volume
        zonesrc[self.zone] = self.source
        zonemute[self.zone] = self.mute

        if from_port:
            if self.zone in media_zonetable:
                callbackobj = media_zonetable.index(self.zone)
                callbackint = int(callbackobj)
                media_callback[callbackint]()

        _LOGGER.debug('Zone: %s, Power: %s, Vol: %sdb, %s%%, Mute: %s, Source: %s, Init: %s', \
           self.zone, self.power, self.volume, db_to_percent(self.volume), \
           self.mute, self.source, zoneinit[int(self.zone)])

    @classmethod
    def from_string(cls, match):
        ZoneConnectStatus(*[str(m) for m in match.groups()], True)

class ZonesetStatus(object):
    def __init__(self
             ,zone: int
             ,ovride: str
             ,bass: float
             ,treble: float
             ,group: int
             ,vrset: int
             ,from_port: bool
             ):

        self.zone = abs(int(zone))
        self.bass = bass
        self.treble = treble
        zonebass[self.zone] = self.bass
        zonetreble[self.zone] = self.treble
        zonegroupsrc[self.zone] = group
        self.volume_offset = zonevoloffset[self.zone]
        zonevolreset[self.zone] = vrset

        if MODEL == 'ESSENTIA_D':
            zoneoverride[self.zone] = int(ovride)

        if zoneoverride[self.zone] == 1:
           self.override = bool(1)
        else:
           self.override = bool(0)

        if zonevolreset[self.zone] == 1:
           self.volume_reset = bool(0)
        else:
           self.volume_reset = bool(1)

        if zonegroupsrc[self.zone] == 1:
           self.group = bool(0)
        else:
           self.group = bool(1)

        if zonelock[self.zone] == 0:
           self.keypad_lock = bool(0)
        else:
           self.keypad_lock = bool(1)

        if from_port:
            if 'settings_zonetable' in globals():
                if self.zone in settings_zonetable:
                    callbackindex = [i for i, x in enumerate(settings_zonetable) if x == self.zone]
                    for callbackzone in callbackindex:
                        settings_callback[callbackzone]()

        _LOGGER.debug('Zone: %s, Bass: %s, Treble: %s, Override: %s, VolReset: %s, Group: %s, Init: %s',\
            self.zone, self.bass, self.treble, self.override, \
            self.volume_reset, self.group, zonesetinit[int(self.zone)])

    @classmethod
    def from_string(cls, match):
        if MODEL == 'SIMPLESE':
            ZonesetStatus(*[str(m) for m in match.groups()], '1', True)
        else:
            ZonesetStatus(*[str(m) for m in match.groups()], True)

class ConcertoZonesetStatus(object):
    def __init__(self
             ,zone: int
             ,bass: float
             ,treble: float
             ,balance: str
             ,group: int
             ,maxvol: float
             ,inivol: float
             ,from_port: bool
             ):

        self.zone = abs(int(zone))
        self.bass = bass
        self.treble = treble
        zonebass[self.zone] = self.bass
        zonetreble[self.zone] = self.treble
        strbalance = str(balance)
        if strbalance[0] == 'L':
            self.balance = -int(strbalance[1])
            zonebalance[self.zone] = self.balance
        elif strbalance[0] == 'R':
            self.balance = int(strbalance[1])
            zonebalance[self.zone] = self.balance
        elif strbalance[0] == 'C':
            self.balance = 0
            zonebalance[self.zone] = self.balance
        else:    
            self.balance = balance
        self.volume_offset = zonevoloffset[self.zone]

        if from_port:
            if 'settings_zonetable' in globals():
                if self.zone in settings_zonetable:
                    callbackindex = [i for i, x in enumerate(settings_zonetable) if x == self.zone]
                    for callbackzone in callbackindex:
                        settings_callback[callbackzone]()

        _LOGGER.debug('Zone: %s, Bass: %s, Treble: %s, Balance: %s, Init: %s',\
            self.zone, self.bass, self.treble, self.balance, \
            zonesetinit[int(self.zone)])

    @classmethod
    def from_string(cls, match):
        ConcertoZonesetStatus(*[str(m) for m in match.groups()], True)

class Nuvo(object):
    """
    Nuvo amplifier interface
    """
    def add_callback(self, coro: Callable[..., Coroutine], zone, zone_name) -> None:
        """
        Add entity subscription for updates
        """
        raise NotImplemented()

    def get_model(self):
        """
        Get the Nuvo model from version request
        """
        raise NotImplemented()

    def zone_status(self, zone: int):
        """
        Get the structure representing the status of the zone
        :return: status of the zone or None
        """
        raise NotImplemented()

    def zoneset_status(self, zone: int):
        """
        Get the structure representing the status of the zone
        :return: status of the zone or None
        """
        raise NotImplemented()

    def set_power(self, zone: int, power: bool):
        """
        Turn zone on or off
        :param power: True to turn on, False to turn off
        """
        raise NotImplemented()

    def join_players(self, zone, group_members):
        """
        Join entity to a speaker group
        :param group_members: entity to add
        """
        raise NotImplemented()

    def unjoin_player(self, zone):
        """
        Removes zone from all speaker groups
        """
        raise NotImplemented()

    def set_mute(self, zone: int, mute: bool):
        """
        Mute zone on or off
        :param mute: True to mute, False to unmute
        """
        raise NotImplemented()

    def set_keypad_lock(self, zone: int, lock: bool):
        """
        Lock or unlock zone keypad
        :param mute: True to lock, False to unlock
        """
        raise NotImplemented()

    def set_volume(self, zone: int, volume: float):
        """
        Set volume for zone
        :param volume: float from -78 to 0 inclusive
        """
        raise NotImplemented()

    def set_volume_offset(self, zone: int, volume: float):
        """
        Set volume offset for groups
        :param volume: float from -30 to 30 inclusive
        """
        raise NotImplemented()

    def set_treble(self, zone: int, treble: float):
        """
        Set treble for zone
        :param treble: float from -12 to 12 inclusive
        """
        raise NotImplemented()

    def set_bass(self, zone: int, bass: float):
        """
        Set bass for zone
        :param bass: float from -12 to 12 inclusive
        """
        raise NotImplemented()

    def set_balance(self, zone: int, balance: float):
        """
        Set balance for zone
        :param balance: float from -6 to 6 inclusive
        """
        raise NotImplemented()

    def set_source(self, zone: int, source: int):
        """
        Set source for zone
        :param source: integer from 1 to 6 inclusive
        """
        raise NotImplemented()

    def page_off(self, page_source, page_zones):
        """
        Restores zone to it's previous state prior to page request
        """
        raise NotImplemented()

    def page_on(self, page_source, page_zones, page_volume):
        """
        Power on all zones, set to paging source and volume
        """
        raise NotImplemented()

    def mute_all(self):
        """
        Mutes all zones.
        """
        raise NotImplemented()

    def unmute_all(self):
        """
        Unmutes all zones.
        """
        raise NotImplemented()

    def all_off(self):
        """
        Turn off all zones.
        """
        raise NotImplemented()

# Helpers

def _is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def db_to_percent(db):
    if int(db) > -24:
        return int((( int(db) + 24) / 24 / 2 +.5) * 100)
    else:
        return int((( int(db) + 78) / 54 / 2) * 100)

def percent_to_db(percent):
    if percent > 50:
        return int(((percent / 100) * 48) - 48)
    else:
        return int(((percent / 100) * 108) - 78)

def _parse_response(string: bytes):
   """
   :param request: request that is sent to the nuvo
   :return: regular expression return match(s)
   """
   match = re.search(ESSENTIA_D_SETSR_PATTERN, string)
   if match:
      _LOGGER.debug('Essentia D SETSR received')
      ZonesetStatus.from_string(match)

   if not match:
       match = re.search(CONSR_PATTERN, string)
       if match:
          _LOGGER.debug('CONSR received')
          ZoneConnectStatus.from_string(match)

   if not match:
       match = re.search(STATUS_PATTERN, string)
       if match:
          _LOGGER.debug('STATUS received')
          ZoneStatus.from_string(match)

   if not match:
       match = re.search(SIMPLESE_SETSR_PATTERN, string)
       if match:
          _LOGGER.debug('Simplese SETSR received')
          ZonesetStatus.from_string(match)

   if not match:
       match = re.search(CONCERTO_SETSR_PATTERN, string)
       if match:
          _LOGGER.debug('Concerto SETSR received')
          ConcertoZonesetStatus.from_string(match)

   if not match:
       match = re.search(SIMPLESE_OFF_PATTERN, string)
       if match:
          _LOGGER.debug('Simplese PWROFF received')
          SimpleseZonePwrOff(match)

   if not match:
       match = re.search(ALL_OFF_PATTERN, string)
       if match:
          _LOGGER.debug('ALL OFF received')
          all_off_keypad()

   if not match:
       match = re.search(KEYPAD_LOCK_PATTERN, string)
       if match:
          _LOGGER.debug('Keypad lock status received')
          keypad_lock_recv(match)

   if not match:
       match = re.search(ERROR_PATTERN, string)
       if match:
          _LOGGER.error('Received error response from Nuvo on last command')

   global MODEL

   if not match:
       match = re.search(ESSENTIA_D_VERSION, string)
       if match:
          _LOGGER.info('Nuvo returned model Essentia D')
          MODEL = 'ESSENTIA_D'

   if not match:
       match = re.search(SIMPLESE_VERSION, string)
       if match:
          _LOGGER.info('Nuvo returned model Simplese')
          MODEL = 'SIMPLESE'

   if not match:
       match = re.search(CONCERTO_VERSION, string)
       if match:
          _LOGGER.info('Nuvo returned model Concerto')
          MODEL = 'CONCERTO'

   if not match:
       match = re.search(CONCERTO_VERSION2, string)
       if match:
          _LOGGER.info('Nuvo returned model Concerto (NV-I8G)')
          MODEL = 'CONCERTO'

   if (string == '#Busy'):
       _LOGGER.warn('BUSY RESPONSE - TRY AGAIN')
   return None

   if not match:
       _LOGGER.warn('NO MATCH - %s' , string)
   return None

def _format_version_request():
    return 'VER'.format()

def _format_zone_status_request(zone: int) -> str:
    if MODEL == 'CONCERTO':
        return 'Z{:0=2}STATUS'.format(zone)
    else:
        return 'Z{:0=2}CONSR'.format(zone)

def _format_zoneset_status_request(zone: int) -> str:
    return 'Z{:0=2}SETSR'.format(zone)

def _format_set_power(zone: int, power: bool) -> str:
    zone = int(zone)
    if (power):
       zonepwr[int(zone)] = 1
       return 'Z{:0=2}ON'.format(zone)
    else:
       zonepwr[int(zone)] = 0
       return 'Z{:0=2}OFF'.format(zone)

def _format_set_mute(zone: int, mute: bool) -> str:
    if (mute):
       zonemute[int(zone)] = 1
       return 'Z{:0=2}MTON'.format(int(zone))
    else:
       zonemute[int(zone)] = 0
       return 'Z{:0=2}MTOFF'.format(int(zone))

def _format_set_keypad_lock(zone: int, lock: bool) -> str:
    if (lock):
       zonelock[int(zone)] = 1
       return 'Z{:0=2}LKON'.format(int(zone))
    else:
       zonelock[int(zone)] = 0
       return 'Z{:0=2}LKOFF'.format(int(zone))

def _format_set_group(zone: int, group: bool) -> str:
    if (group):
       return 'Z{:0=2}GRPON'.format(int(zone))
    else:
       return 'Z{:0=2}GRPOFF'.format(int(zone))

def _format_set_volume_reset(zone: int, volreset: bool) -> str:
    if (volreset):
       return 'Z{:0=2}VRSTON'.format(int(zone))
    else:
       return 'Z{:0=2}VRSTOFF'.format(int(zone))

def _format_set_volume(zone: int, volume: float) -> str:
    # If muted, status has no info on volume level
    if _is_int(volume):
       # Negative sign in volume parm produces erronous result
       volume = abs(volume)
       volume = round(volume,0)
    return 'Z{:0=2}VOL{:0=2}'.format(int(zone), volume)

def _format_set_bass(zone: int, bass: float) -> bytes:
    zonebass[int(zone)] = bass
    if bass >= 0:
       return 'Z{:0=2}BASS+{:0=2}'.format(int(zone), int(bass))
    else:
       return 'Z{:0=2}BASS{:0=3}'.format(int(zone), int(bass))

def _format_set_treble(zone: int, treble: float) -> bytes:
    zonetreble[int(zone)] = treble
    if treble >= 0:
       return 'Z{:0=2}TREB+{:0=2}'.format(int(zone), int(treble))
    else:
       return 'Z{:0=2}TREB{:0=3}'.format(int(zone), int(treble))

def _format_set_balance(zone: int, balance: float) -> bytes:
    zonebalance[int(zone)] = balance
    if balance > 0:
       return 'Z{:0=2}BALR{:0=1}'.format(int(zone), int(balance))
    elif balance < 0:
       return 'Z{:0=2}BALL{:0=1}'.format(int(zone), abs(int(balance)))
    else:
       return 'Z{:0=2}BALC'.format(int(zone))

def _format_set_source(zone: int, source: int) -> str:
    source = int(max(1, min(int(source), 6)))
    zonesrc[int(zone)] = source
    return 'Z{:0=2}SRC{}'.format(int(zone),source)

def _format_mute_all() -> str:
    return 'ALLMON'.format()

def _format_unmute_all() -> str:
    return 'ALLMOFF'.format()

def _format_all_off() -> str:
    return 'ALLOFF'.format()

def all_off_keypad():
    zonesalloff = 1
    for count in range(0,21):
        if zonepwr[int(count)] == 1:
            zonesalloff = 0
    for count in range(0,21):
        if zonesalloff == 0:
            zonepwralloff[int(count)] = zonepwr[int(count)]
            zonepwr[int(count)] = 0
        else:
            if zonepwralloff[int(count)] == 1 and ALL_OFF_RECALL:
                zonepwr[int(count)] = 1
        if count in media_zonetable:
            callbackobj = media_zonetable.index(count)
            callbackint = int(callbackobj)
            media_callback[callbackint]()

def SimpleseZonePwrOff(match):
    zone = abs(int(match[1]))
    zonepwr[zone] = 0
    if zone in media_zonetable:
        callbackobj = media_zonetable.index(zone)
        callbackint = int(callbackobj)
        media_callback[callbackint]()

def keypad_lock_recv(match):
    zone = abs(int(match[1]))
    lock = match[2]
    if lock == 'ON':
        zonelock[zone] = 1
    else:
        zonelock[zone] = 0
    if zone in settings_zonetable:
        callbackindex = [i for i, x in enumerate(settings_zonetable) if x == zone]
        for callbackzone in callbackindex:
            settings_callback[callbackzone]()


def get_nuvo(port_url, baud, all_off_recall):
    """
    Return synchronous version of Nuvo interface
    :param port_url: serial port, i.e. '/dev/ttyUSB0,/dev/ttyS0'
    :param baud: baud, i.e '9600'
    :return: synchronous implementation of Nuvo interface
    """

    lock = RLock()

    def synchronized(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper

    class NuvoSync(Nuvo):
        def __init__(self, port_url):
            global ALL_OFF_RECALL
            ALL_OFF_RECALL = all_off_recall

        def get_model(self):
            findmodelcount = 0
            global MODEL
            while findmodelcount < 10:
                self._process_request(_format_version_request())
                time.sleep(TIMEOUT_RESPONSE)
                if 'MODEL' in globals():
                    findmodelcount = 10
                else:
                    findmodelcount += 1
            if not 'MODEL' in globals():
                _LOGGER.error('This does not appear to be a supported Nuvo device.')
                MODEL = 'Unknown'
            return MODEL

        def _send_request():
            """
            :param request: request that is sent to the nuvo
            :return: bool if transmit success
            """
            global port
            request = ''
            # format and send output command
            while request != 'EXIT':
                request = cmd_queue.get(block=True)
                lineout = "*" + request + "\r"
                _LOGGER.debug('Sending "%s"', request)
                try:
                    port.write(lineout.encode())

                    if request == 'ALLOFF':
                        time.sleep(1) # Nuvo does NOT process commands immediately after ALLOFF
                    if request[3:5] == 'ON':
                        time.sleep(0.05) # Give Nuvo zone time to power up
                    time.sleep(0.1)  # Must wait in between commands for MPU to process
                except:
                    _LOGGER.error('Unexpected port error when sending command.')

        SendThread = threading.Thread(target=_send_request, args=(), daemon=True)
        SendThread.start()

        def _process_request(self, request: str):
            """
            :param request: request that is sent to the nuvo
            """
            # Send command to device
            cmd_queue.put(request)

        def _listen():
            start_time = time.time()
            timeout = TIMEOUT_RESPONSE
            _LOGGER.info('Attempting connection - "%s" at %s baud', port_url, baud)
            global listen_init
            listen_init = 1
            # listen for response
            def read_data():
                global listen_init
                global port
                try:
                    port = serial.serial_for_url(port_url, do_not_open=True)
                    port.baudrate = int(baud)
                    port.stopbits = serial.STOPBITS_ONE
                    port.bytesize = serial.EIGHTBITS
                    port.parity = serial.PARITY_NONE
                    port.open()
                except:
                    if listen_init == 1:
                         return False

                no_data = False
                receive_buffer = b''
                message = b''
                listen_init = 0
                try:
                    while (no_data == False):
                    # fill buffer until we get term seperator
                       data = port.read(1)
                       if data:
                          receive_buffer += data
                          if EOL in receive_buffer:
                              message, sep, receive_buffer = receive_buffer.partition(EOL)
                              _LOGGER.debug('Received: %s', message)
                              _parse_response(str(message))
                except:
                    _LOGGER.error('Unexpected port error, retrying.')
                    time.sleep(5)
                    try:
                        port.open()
                        read_data()
                    except:
                        read_data()

            read_data()

        SyncThread = threading.Thread(target=_listen, args=(), daemon=True)
        SyncThread.start()

        def add_callback(self, callback: Callable[..., Coroutine], zone, entity_id, entity_type) -> None:
            global media_zonetable
            global media_callback
            global settings_zonetable
            global settings_callback
            global entitytable
            global groupzone_members
            global setup
            try:
                media_zonetable
            except:
                media_zonetable = []
                media_callback = []
                settings_zonetable = []
                settings_callback = []
                entitytable = []
                groupzone_members = []
            if entity_type == 'media':
                zone = int(zone)
                entitytable.append(entity_id)
                media_zonetable.append(zone)
                media_callback.append(callback)
                groupzone_members.append(zone)
                zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
                zoneindex = int(zoneindexobj[0])
                groupzone_members[zoneindex] = []
                groupzone_members[zoneindex].append(zone)
                setup = True
                _LOGGER.debug('Added %s media callback: %s', entity_id, callback)
            if entity_type == 'settings':
                zone = int(zone)
                settings_zonetable.append(zone)
                settings_callback.append(callback)
                _LOGGER.debug('Added %s settings callback: %s', entity_id, callback)

        @synchronized
        def zone_status(self, zone: int):
            """
            Send status request multiple times on startup to insure we get
            a response
            """
            if zoneinit[int(zone)] == 0:
               try:
                   if MODEL != 'CONCERTO':
                       rtn = ZoneConnectStatus.from_string(self._process_request(
                                    _format_zone_status_request(zone)))
                   else:
                       rtn = ZoneStatus.from_string(self._process_request(
                                    _format_zone_status_request(zone)))
               except:
                  rtn = None
               zoneinit[int(zone)] += 1
               return rtn
            else:
               if zonepwr[int(zone)] == 1:
                  zonestrpwr = 'ON'
               else:
                  zonestrpwr = 'OFF'
               if zonemute[int(zone)] == 1:
                  zonestrvol = 'MT'
               else:
                  zonestrvol = str(zonevol[int(zone)])

            if zonepwralloff[int(zone)] == 1 and zonepwr[int(zone)] == 1:
                self.set_power(int(zone), True)
                zonepwralloff[int(zone)] = 0

            if setup:
                zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
                zoneindex = int(zoneindexobj[0])
                if len(groupzone_members[zoneindex]) > 1:
                    zonecnt = 1
                    while zonecnt < len(groupzone_members[zoneindex]):
                        group_member = int(groupzone_members[zoneindex][zonecnt])
                        _LOGGER.debug('Zone %s: update group member zone %s', \
                            zone, group_member)
                        if zonepwr[int(zone)] != zonepwr[group_member]:
                            if zonepwr[int(zone)] == 1:
                                self.set_power(group_member, True)
                            else:
                                self.set_power(group_member, False)
                        if zonevol[int(zone)] != zonevol[group_member]:
                            if zonevoloffset[group_member] != 0:
                                offsetvolpct = db_to_percent(zonevol[int(zone)]) + \
                                    zonevoloffset[group_member]
                                offsetvol = percent_to_db(offsetvolpct)
                                if offsetvol < -78:
                                    offsetvol = -78
                                else:
                                    if offsetvol > 0:
                                        offsetvol = 0
                                self.set_volume(group_member, offsetvol)
                            else:
                                self.set_volume(group_member, zonevol[int(zone)])
                        if zonemute[int(zone)] != zonemute[group_member]:
                            if zonemute[int(zone)] == 1:
                                self.set_mute(group_member, True)
                            else:
                                self.set_mute(group_member, False)
                        if zonesrc[int(zone)] != zonesrc[group_member]:
                            self.set_source(group_member, zonesrc[int(zone)])
                        zonecnt += 1

            if MODEL == 'CONCERTO':
                return ZoneStatus(int(zone), zonestrpwr,
                    zonesrc[int(zone)], zonestrvol, False)
            else:
                return ZoneConnectStatus(int(zone), zonestrpwr,
                    zonesrc[int(zone)], 0, zonestrvol, False)


        @synchronized
        def zoneset_status(self, zone: int):
            """
            Send status request multiple times on startup to insure we get
            a response
            """
            if zonesetinit[int(zone)] == 0:
                try:
                    if MODEL != 'CONCERTO':
                        rtn = ZonesetStatus.from_string(
                                     self._process_request(
                                     _format_zoneset_status_request(zone)))
                    else:
                        rtn = ConcertoZonesetStatus.from_string(
                                     self._process_request(
                                     _format_zoneset_status_request(zone)))
                except:
                    rtn = None
                zonesetinit[int(zone)] += 1
                return rtn
            else:
                if MODEL != 'CONCERTO':
                    return ZonesetStatus(int(zone), zoneoverride[int(zone)],
                                    zonebass[int(zone)],
                                    zonetreble[int(zone)],
                                    zonegroupsrc[int(zone)],
                                    zonevolreset[int(zone)], False)
                else:     
                    return ConcertoZonesetStatus(int(zone), zonebass[int(zone)],
                                    zonetreble[int(zone)],
                                    zonebalance[int(zone)], 0, 0, 0, False)

        @synchronized
        def join_players(self, zone, group_members):
            zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
            zoneindex = int(zoneindexobj[0])
            for group_member in group_members:
                entityindexobj = [i for i, x in enumerate(entitytable) if x == group_member]
                entityindex = int(entityindexobj[0])
                addedzone = int(media_zonetable[entityindex])
                del groupzone_members[entityindex][:]
                groupzone_members[entityindex].append(media_zonetable[entityindex])
                for zones in media_zonetable:
                    zonesindexobj = [i for i, x in enumerate(media_zonetable) if x == zones]
                    zonesindex = int(zonesindexobj[0])
                    if zones != zone:
                        if zone in groupzone_members[zonesindex]:
                            groupzone_members[zonesindex].remove(zone)
                    if zones != addedzone:
                        if addedzone in groupzone_members[zonesindex]:
                            groupzone_members[zonesindex].remove(addedzone)
                    media_callback[zonesindex]()
                groupzone_members[zoneindex].append(addedzone)
                media_callback[entityindex]()
                _LOGGER.debug('Join zone %s to controller zone %s.  All slave zones: %s', \
                    addedzone, zone, groupzone_members[zoneindex])
            callbackobj = media_zonetable.index(zone)
            callbackint = int(callbackobj)
            media_callback[callbackint]()

        @synchronized
        def unjoin_player(self, zone):
            _LOGGER.debug('Unjoin zone %s from all groups', zone)
            zoneindexobj = [i for i, x in enumerate(media_zonetable) if x == zone]
            zoneindex = int(zoneindexobj[0])
            if len(groupzone_members[zoneindex]) == 1:
                self.set_power(zone, False)
            for control_zone in media_zonetable:
                control_zoneindexobj = \
                    [i for i, x in enumerate(media_zonetable) if x == control_zone]
                control_zoneindex = int(control_zoneindexobj[0])
                if zone != control_zone:
                    if zone in groupzone_members[control_zoneindex]:
                        groupzone_members[control_zoneindex].remove(zone)
                else:
                    del groupzone_members[control_zoneindex][:]
                    groupzone_members[control_zoneindex].append(media_zonetable[control_zoneindex])
                callbackobj = media_zonetable.index(control_zone)
                callbackint = int(callbackobj)
                media_callback[callbackint]()

        @synchronized
        def set_power(self, zone: int, power: bool):
            if zone == 0:
                if power:
                    zonepwr[zone] = 1
                else:
                    zonepwr[zone] = 0
                media_callback[0]()
            else:
                self._process_request(_format_set_power(zone, power))

        @synchronized
        def set_mute(self, zone: int, mute: bool):
            if zone == 0:
                if mute:
                    zonemute[0] = 1
                else:
                    zonemute[0] = 0
                media_callback[0]()
            else:
                self._process_request(_format_set_mute(zone, mute))

        @synchronized
        def set_keypad_lock(self, zone: int, lock: bool):
            if zone == 0:
                if lock:
                    zonelock[0] = 1
                else:
                    zonelock[0] = 0
                media_callback[0]()
            else:
                self._process_request(_format_set_keypad_lock(zone, lock))

        @synchronized
        def set_volume(self, zone: int, volume: float):
            if zone == 0:
                zonevol[0] = volume
                media_callback[0]()
            else:
                self._process_request(_format_set_volume(zone, volume))

        @synchronized
        def set_volume_offset(self, zone: int, volume: float):
            zonevoloffset[zone] = volume
            if zone in settings_zonetable:
                callbackindex = [i for i, x in enumerate(settings_zonetable) if x == zone]
                for callbackzone in callbackindex:
                    settings_callback[callbackzone]()

        @synchronized
        def set_group(self, zone: int, group: bool):
            self._process_request(_format_set_group(zone, group))

        @synchronized
        def set_volume_reset(self, zone: int, volreset: bool):
            self._process_request(_format_set_volume_reset(zone, volreset))

        @synchronized
        def set_treble(self, zone: int, treble: float):
            self._process_request(_format_set_treble(zone, treble))

        @synchronized
        def set_bass(self, zone: int, bass: float):
            self._process_request(_format_set_bass(zone, bass))

        @synchronized
        def set_balance(self, zone: int, balance: float):
            self._process_request(_format_set_balance(zone, balance))

        @synchronized
        def set_source(self, zone: int, source: int):
            if zone == 0:
                zonesrc[0] = source
                media_callback[0]()
            else:
                self._process_request(_format_set_source(zone, source))

        @synchronized
        def page_off(self, page_source, page_zones):
            while page_active[1] == 1:
                _LOGGER.info('Paging on service call currently in progress when paging off service call requested!  This should be ok, but could put zones in the incorrect state.')
            zonecnt = 0
            while zonecnt < len(page_zones):
               self.set_volume(int(page_zones[zonecnt]),
                               zonevolsave[int(page_zones[zonecnt])])
               if zonemutesave[int(page_zones[zonecnt])] == 1:
                   self.set_mute(int(page_zones[zonecnt]), True)
               if zonepwrsave[int(page_zones[zonecnt])] == 0:
                   self.set_power(int(page_zones[zonecnt]), False)
               else:
                   if zonesrcsave[int(page_zones[zonecnt])] != page_source:
                       self.set_source(int(page_zones[zonecnt]),
                                       zonesrcsave[int(page_zones[zonecnt])])
               zonecnt += 1
            page_active[0] = 0

        @synchronized
        def page_on(self, page_source, page_zones, page_volume):
            if page_active[0] == 0:
                page_active[1] = 1
                zonecnt = 0
                while zonecnt < len(page_zones):
                   _LOGGER.debug('Page Zone: %s, Vol: %s, Src: %s', page_zones[zonecnt],\
                       page_volume[zonecnt], page_source)
                   zonepwrsave[int(page_zones[zonecnt])] = zonepwr[int(page_zones[zonecnt])]
                   zonesrcsave[int(page_zones[zonecnt])] = zonesrc[int(page_zones[zonecnt])]
                   zonevolsave[int(page_zones[zonecnt])] = zonevol[int(page_zones[zonecnt])]
                   zonemutesave[int(page_zones[zonecnt])] = zonemute[int(page_zones[zonecnt])]
                   if zonepwr[int(page_zones[zonecnt])] == 0:
                       self.set_power(int(page_zones[zonecnt]), True)
                   if zonesrc[int(page_zones[zonecnt])] != page_source:
                       self.set_source(int(page_zones[zonecnt]), page_source)
                   self.set_volume(int(page_zones[zonecnt]), percent_to_db(int(page_volume[zonecnt])))
                   zonecnt += 1
                   page_active[0] = 1
                page_active[1] = 0
            else:
                _LOGGER.info('Paging already active, ignoring second request.')

        @synchronized
        def mute_all(self):
            self._process_request(_format_mute_all())
            for count in range(1,21):
                zonemute[int(count)] = 1
                if count in media_zonetable:
                    callbackobj = media_zonetable.index(count)
                    callbackint = int(callbackobj)
                    media_callback[callbackint]()

        @synchronized
        def unmute_all(self):
            self._process_request(_format_unmute_all())
            for count in range(1,21):
                zonemute[int(count)] = 0
                if count in media_zonetable:
                    callbackobj = media_zonetable.index(count)
                    callbackint = int(callbackobj)
                    media_callback[callbackint]()

        @synchronized
        def all_off(self):
            self._process_request(_format_all_off())
            for count in range(0,21):
                zonepwralloff[int(count)] = 0
                zonepwr[int(count)] = 0
                if count in media_zonetable:
                    callbackobj = media_zonetable.index(count)
                    callbackint = int(callbackobj)
                    media_callback[callbackint]()

    return NuvoSync(port_url)


