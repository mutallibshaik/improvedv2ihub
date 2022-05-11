#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
    Example of automatic vehicle control from client side.
"""

from __future__ import print_function

import argparse
import collections
import datetime
import glob
import logging
import math
import os
import random
import re
import sys
import weakref

import requests
try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_q
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        'cannot import numpy, make sure numpy package is installed')

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass
SUN_PRESETS = {
    'day': (60.0, 0.0),
    'night': (-90.0, 0.0),
    'sunset': (0.5, 180.0)}

WEATHER_PRESETS = {
    'clear': [10.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0],
    'overcast': [80.0, 0.0, 0.0, 50.0, 2.0, 0.0, 10.0],
    'rain': [100.0, 80.0, 90.0, 100.0, 20.0, 0.0, 100.0]}

def apply_sun_presets(args, weather):
    """Uses sun presets to set the sun position"""
    if args.sun is not None:
        if args.sun in SUN_PRESETS:
            weather.sun_altitude_angle = SUN_PRESETS[args.sun][0]
            weather.sun_azimuth_angle = SUN_PRESETS[args.sun][1]
        else:
            print("[ERROR]: Command [--sun | -s] '" + args.sun + "' not known")
            sys.exit(1)
def apply_weather_presets(args, weather):
    """Uses weather presets to set the weather parameters"""
    if args.weather is not None:
        if args.weather in WEATHER_PRESETS:
            weather.cloudiness = WEATHER_PRESETS[args.weather][0]
            weather.precipitation = WEATHER_PRESETS[args.weather][1]
            weather.precipitation_deposits = WEATHER_PRESETS[args.weather][2]
            weather.wind_intensity = WEATHER_PRESETS[args.weather][3]
            weather.fog_density = WEATHER_PRESETS[args.weather][4]
            weather.fog_distance = WEATHER_PRESETS[args.weather][5]
            weather.wetness = WEATHER_PRESETS[args.weather][6]
        else:
            print("[ERROR]: Command [--weather | -w] '" + args.weather + "' not known")
            sys.exit(1)
def apply_weather_values(args, weather):
    """Set weather values individually"""
    if args.azimuth is not None:
        weather.sun_azimuth_angle = args.azimuth
    if args.altitude is not None:
        weather.sun_altitude_angle = args.altitude
    if args.clouds is not None:
        weather.cloudiness = args.clouds
    if args.rain is not None:
        weather.precipitation = args.rain
    if args.puddles is not None:
        weather.precipitation_deposits = args.puddles
    if args.wind is not None:
        weather.wind_intensity = args.wind
    if args.fog is not None:
        weather.fog_density = args.fog
    if args.fogdist is not None:
        weather.fog_distance = args.fogdist
    if args.wetness is not None:
        weather.wetness = args.wetness
        
import carla
import time
import pandas as pd
from carla import ColorConverter as cc
from agents.navigation.roaming_agent import RoamingAgent
from agents.navigation.basic_agent import BasicAgent
from agents.tools.misc import draw_waypoints

from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.global_route_planner_dao import GlobalRoutePlannerDAO
import matplotlib.pyplot as plt


# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name


# ==============================================================================
# -- World ---------------------------------------------------------------
# ==============================================================================

class World(object):
    def __init__(self, carla_world, hud,args):
        self.world = carla_world
        self.actor_role_name = args.rolename
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.imu_sensor = None
        self.camera_manager = None
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = args.filter
        self._gamma = args.gamma
        self.restart()
        self.world.on_tick(hud.on_world_tick)
        self.recording_enabled = False
        self.recording_start = 0
                
        

    def restart(self):
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        # Get a random blueprint.
        blueprint = random.choice(self.world.get_blueprint_library().filter(self._actor_filter))
        blueprint.set_attribute('role_name', self.actor_role_name)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        while self.player is None:
            random.seed(-100099)
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            #spawn_point = carla.Transform(carla.Location(x=25, y=3, z=3), carla.Rotation())
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        self.player.get_world().set_weather(preset[0])

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):
        actors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.imu_sensor.sensor,
            self.player]
        for actor in actors:
            if actor is not None:
                actor.destroy()


# ==============================================================================
# -- KeyboardControl -----------------------------------------------------------
# ==============================================================================


class KeyboardControl(object):
    def __init__(self, world):
        world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

    def parse_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True

    @staticmethod
    def _is_quit_shortcut(key):
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)

# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 12 if os.name == 'nt' else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 24), width, height)
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        liste=[]
        liste_2=[]
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        call="http://api.weatherapi.com/v1/current.json?key=5f90a9ef2691482aa16234703221302&q=canada&aqi=no"
        response = requests.get(call )
        
        location=response.json().get('location').get('name')
        
        weather_descriptions=response.json().get('current').get('condition').get("text")
      
        feelslike=response.json().get('current').get('feelslike_c')


        traffic_lights=world.world.get_actors().filter("*traffic_light*")
     
            
        speed_limits=world.world.get_actors().filter('traffic.speed_limit.*')
        for l in traffic_lights:
            liste.append(math.sqrt((l.get_location().x - t.location.x) ** 2 + (l.get_location().y - t.location.y) ** 2 ))
            
        for s in  speed_limits:
            liste_2.append(math.sqrt((s.get_location().x - t.location.x) ** 2 + (s.get_location().y - t.location.y) ** 2 ))
        
            
        heading = 'N' if abs(t.rotation.yaw) < 89.5 else ''
        heading += 'S' if abs(t.rotation.yaw) > 90.5 else ''
        heading += 'E' if 179.5 > t.rotation.yaw > 0.5 else ''
        heading += 'W' if -0.5 > t.rotation.yaw > -179.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')
        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
           
            'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            'Map:     % 20s' % world.map.name,
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)),
            u'Heading:% 16.0f\N{DEGREE SIGN} % 2s' % (t.rotation.yaw, heading),
            'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            'Height:  % 18.0f m' % t.location.z,
            
            ]
        
        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('Hand brake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
            
       
        self._info_text += [
            '',
            'Collision:',
            collision,
            '',
            'Number of vehicles: % 8d' % len(vehicles),
            
            'Traffic lights in : % 8d m'  % (min(liste)), 
            'Speed Limits % 2s' % ('in %2dm is %2dkm/h' % (min(liste_2), world.player.get_speed_limit() ))
       #     'Speed Limits' % ('(% 5.1f, % 5.1f)'  % (min(liste_2),(world.player.get_speed_limit() )
            ]
        emergency_messages=[" Accident reported in the next street, drive with caution", "Highway Traffic is severely affected, to avoid delays, take a detour",
        "There is a dangerous driver in the next street, please be careful !",
        "Please avoid congestion in the next street!" ]
        
        import random
        speed=(3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2))
        #random.seed(speed)

        emergency_msg=(random.choice(emergency_messages))
        if 60<min(liste)  : 
            self.notification_green_zone ("The weather is %s in %s, it feels like %2d" % (weather_descriptions, location, feelslike))
            
        
        if min(liste)<20:
            self.notification_red_zone(emergency_msg)
        elif  20<min(liste)<100:
            self.notification_green_zone ("The weather is %s in %s, it feels like %2d" % (weather_descriptions, location, feelslike))
            if speed > 1.3*world.player.get_speed_limit() :
                self.notification_green_zone(" Please obey speed limits in this zone, max %2d km/h only" % world.player.get_speed_limit())
            
        
       # self._info_text += [
        #    '',
         #   "The weather is %s in %s, it feels like %2d" % (weather_descriptions[0], location, feelslike), 
           #  ''
        
            #]
         #Get the traffic light affecting a vehicle
        if world.player.is_at_traffic_light():
            traffic_light = world.player.get_traffic_light()
            if traffic_light.get_state() == carla.TrafficLightState.Red:
                self.notification( 'Attention!!! The lights are Red')
           
         
            
            else:
                self.notification ('You can go ahead ! The lights are green')
       
        speed=3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
        if speed < 1.2*world.player.get_speed_limit() : 
            self._info_text += [
            '',
            'You are respecting the ',
            'current speed limit',
            ''
            ]
        else:
            self._info_text += [
            '',
            'You are over-speeding', 
            'can you decrease your speed ?',
            ''
            ] 

            #' % 2d km/h' % (world.player.get_speed_limit()) ]
        if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']

            def distance(l): return math.sqrt(
                (l.x - t.location.x) ** 2 + (l.y - t.location.y) ** 2 + (l.z - t.location.z) ** 2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)
        
    def notification_green_zone(self, text, seconds=2.0):
        self._notifications.set_text_green_zone(text, seconds=seconds)
        
    def notification_red_zone(self, text, seconds=2.0):
        self._notifications.set_text_red_zone(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self.help.render(display)

# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))
        
    def set_text_green_zone(self, text, color=(0, 255, 0), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))
    
    def set_text_red_zone(self, text, color=(255, 0, 0), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)

# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.dim = (680, len(lines) * 22 + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * 22))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)

# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x ** 2 + impulse.y ** 2 + impulse.z ** 2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)

# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        self.hud.notification('Crossed line %s' % ' and '.join(text))

# ==============================================================================
# -- GnssSensor --------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)),
                                        attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude
# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        self.frame=0
        self.timestamp=0.0
        self.simulation_time=0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(
            bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda sensor_data: IMUSensor._IMU_callback(weak_self, sensor_data))
        
# Set the time in seconds between sensor captures (0.05s)
        
        #bp.set_attribute('sensor_tick', '0.05')

    

    @staticmethod
    def _IMU_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)
        self.timestamp=sensor_data.timestamp

        
        self.frame = sensor_data.frame
        

# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.surface = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        self._camera_transforms = [
            carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15)),
            carla.Transform(carla.Location(x=1.6, z=1.7))]
        self.transform_index = 1
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB'],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)'],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)'],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)'],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)'],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
             'Camera Semantic Segmentation (CityScapes Palette)'],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)']]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
            elif item[0].startswith('sensor.lidar'):
                bp.set_attribute('range', '50')
            item.append(bp)
        self.index = None

    def toggle_camera(self):
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.sensor.set_transform(self._camera_transforms[self.transform_index])

    def set_sensor(self, index, notify=True):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None \
            else self.sensors[index][0] != self.sensors[self.index][0]
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index],
                attach_to=self._parent)
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / 100.0
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros(lidar_img_size)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------
# ==============================================================================

def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None
    data = pd.DataFrame()
    start = time.time()
    
    count = 0
    line1=[]
    o=0
    actors_list = []
    vehicles_list = []
    walkers_list = []
    all_id = []
    Speed_Values=[]

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(4.0)
        traffic_manager = client.get_trafficmanager(args.tm_port)
        #traffic_manager.set_global_distance_to_leading_vehicle(0)
        #traffic_manager.global_percentage_speed_difference(-30.0)
    
       

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height)
        world = World(client.get_world(), hud, args)
        WORLD=client.get_world()
        blueprints = world.world.get_blueprint_library().filter(args.filter)
        if args.safe:
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
            blueprints = [x for x in blueprints if not x.id.endswith('isetta')]
            blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
            blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('t2')]
       
        controller = KeyboardControl(world)
        
        

        weather =  WORLD.get_weather()
    # apply presets
        apply_sun_presets(args, weather)
        apply_weather_presets(args, weather)
        
            # apply weather values individually
        apply_weather_values(args, weather)
        WORLD.set_weather(weather)
          ##### THIS WILL CREATE THE PATH FOR THE FOLDER './DATASET3/AGRESSIVE/town3' #####
        file4=os.path.join("RSU_DATASET", "NORMAL",world.map.name)
        if not os.path.exists(file4):
            os.makedirs(file4)  
        def AffectedSpeedLimit(player):
                affected_speed_limit=player.get_speed_limit()
                if math.isnan(affected_speed_limit):
                    return 50
                else :
                    return affected_speed_limit
                
            
        def SpeedLimitByWeather():
                #This function return speed limits conditionned by the weather
            if args.clouds==0 and args.rain==0 and args.wind==0 and args.fog==0 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90: #Sunny&Clear
                return int(AffectedSpeedLimit(world.player))
            elif args.clouds==80 and args.rain==80 and args.wind==50 and args.fog==10 and args.wetness==80 and args.puddles==30 and int(args.altitude)==-90: #STORMY&NIGHT
                return int(AffectedSpeedLimit(world.player)*0.6)
            elif args.clouds==0 and args.rain==50 and args.wind==0 and args.fog==0 and args.wetness==50 and args.puddles==15 and int(args.altitude)==90 : #SoftRain
                return int(AffectedSpeedLimit(world.player))*0.8
            elif args.clouds==100 and args.rain==0 and args.wind==0 and args.fog==100 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90 : #Cloud&Fog
                return int(AffectedSpeedLimit(world.player))*0.7
            else :
                return int(AffectedSpeedLimit(world.player))
            
        def TargetSpeed():
            l3=(os.listdir(file4))
            j=(len(l3))+1
            random.seed(j+1000)
            if WeatherId()==1:
                return int(AffectedSpeedLimit(world.player))*1
            elif WeatherId()==2:
                return int(AffectedSpeedLimit(world.player))*0.7 #speedReductionFactor
            elif WeatherId()==3:
                return int(AffectedSpeedLimit(world.player))*0.85 
            elif WeatherId()==4:
                return int(AffectedSpeedLimit(world.player))*0.6 
            
            else :
                return int(AffectedSpeedLimit(world.player))*random.uniform(0.8,1)
        def WeatherId():
                #This function return the id of the weather 
            if args.clouds==0 and args.rain==0 and args.wind==0 and args.fog==0 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90: #Sunny&Clear
                return 1
            elif args.clouds==80 and args.rain==80 and args.wind==50 and args.fog==10 and args.wetness==80 and args.puddles==30 and int(args.altitude)==-90: #STORMY&NIGHT
                return 2
            elif args.clouds==0 and args.rain==50 and args.wind==0 and args.fog==0 and args.wetness==50 and args.puddles==15 and int(args.altitude)==90 : #SoftRain
                return 3
            elif args.clouds==100 and args.rain==50 and args.wind==0 and args.fog==100 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90 : #Cloud&Fog
                return 4
            else :
                return 1
            
        def msg_weather():
            if args.clouds==0 and args.rain==0 and args.wind==0 and args.fog==0 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90: #Sunny&Clear
                return "Sunny"
            elif args.clouds==80 and args.rain==80 and args.wind==50 and args.fog==10 and args.wetness==80 and args.puddles==30 and int(args.altitude)==-90: #STORMY&NIGHT
                return "STORMY"
            elif args.clouds==0 and args.rain==50 and args.wind==0 and args.fog==0 and args.wetness==50 and args.puddles==15 and int(args.altitude)==90 : #SoftRain
                return "SoftRain"
            elif args.clouds==100 and args.rain==50 and args.wind==0 and args.fog==100 and args.wetness==0 and args.puddles==0 and int(args.altitude)==90 : #Cloud&Fog
                return "Cloudy"
            else :
                return "Sunny"
            
        if args.agent == "Roaming":
            agent = RoamingAgent(world.player)
        else:
            TS=TargetSpeed()
            agent = BasicAgent(world.player,target_speed=TargetSpeed())
      
                
            spawn_point = world.map.get_spawn_points()[0]

        clock = pygame.time.Clock()
        m = world.world.get_map()
        
        w = m.get_waypoint(world.player.get_location())
 
        while True:
            clock.tick_busy_loop(50)
            dt = clock.tick(50)
           
            vitesse=world.player.get_velocity()
            world.player.get_transform().location.x +=   vitesse.x* dt
            world.player.get_transform().location.y +=   vitesse.y* dt
            t = world.player.get_transform()
            c =world.player.get_control() 
           
            v=world.player.get_velocity()
            
            def StateCar(agent):
                State=agent._state
                return (str(State).split('.')[1])
          #      if str(State)=="AgentState.NAVIGATING" :
            #        return 1
           #     elif str(State)=="AgentState.BLOCKED_RED_LIGHT":
             #       return 0
              #  elif str(State)=="AgentState.BLOCKED_BY_VEHICLE": 
               #     return -1
 
           #vehicle_list = actor_list.filter("*vehicle*")
            def Msg_light(agent):
                actor_list =  agent._world.get_actors()
                
                lights_list = actor_list.filter("*traffic_light*")
               
                light_state, traffic_light=agent._is_light_red(lights_list)
                light_state1, traffic_light=agent._is_light_red_europe_style(lights_list)
                light_state2, traffic_light= agent._is_light_red_us_style(lights_list)
                if light_state or light_state1 or light_state2 :
                    return ("Red light")
                else:
                    return ("Green light")
                
            
                
            def LocationTraffic(world):
                actor_list =  world.get_actors()
                LocationListe=[]
                lights_list = actor_list.filter("*traffic_light*")
                for tl in lights_list :
                     LocationListe.append([tl.get_location().x,tl.get_location().y])
                     return(LocationListe)
                
            def Points (agent,i):
                p=agent._map.get_spawn_points()[i]
                return [agent._map.get_spawn_points()[i].location.x , agent._map.get_spawn_points()[i].location.y]
            
            
            def SpeedSigns(agent):
                actor_list =  agent._world.get_actors()
                for speedsign in  actor_list.filter('traffic.speed_limit.*') :
                    return speedsign.type_id
                
            def Traffic_lights(agent):
                liste=[]
                actor_list =  agent._world.get_actors()
                
                lights_list = actor_list.filter("*traffic_light*")
                
                for l in lights_list:
                   # return math.sqrt((l.get_location().x - agent.get_location().x) ** 2 + (l.get_location().y - agent.get_location().y) ** 2 )
                    
                   liste.append(math.sqrt((l.get_location().x - agent._vehicle.get_location().x) ** 2 + (l.get_location().y - agent._vehicle.get_location().y) ** 2 ))
                return(min(liste))
                
            def Traffic_speed_limits(agent):
                liste=[]
                actor_list =  agent._world.get_actors()
                
                
                speed_limits_list = actor_list.filter('traffic.speed_limit.*')
                
                for l in speed_limits_list:
                    #return(speed_sign.get_location())
                    liste.append(math.sqrt((l.get_location().x - agent._vehicle.get_location().x) ** 2 + (l.get_location().y - agent._vehicle.get_location().y) ** 2 ))
                return(min(liste))
            
            #for waypoint in world.map.get_spawn_points():
                #world.draw_string(waypoint.location, 'o', draw_shadow=False,
				#							 color=carla.Color(r=255, g=255, b=255), life_time=0.2,
				#							 persistent_lines=True)
            def LaneChange(waypoint):
                if str (waypoint.lane_change) =="carla.libcarla.LaneChange.Right":
                    return 1
                elif str (waypoint.lane_change) =="carla.libcarla.LaneChange.Left":
                    return -1
                elif str (waypoint.lane_change) =="carla.libcarla.LaneChange.NONE": 
                    return 0
                else : 
                    return 2
            def IsJunction(waypoint):
                if waypoint.is_junction:
                    return 1
                else :
                    return 0
            if controller.parse_events():
                return

            # as soon as the server is ready continue!
         #<   world.world.wait_for_tick(10.0)
           
            world.tick(clock)
            world.render(display)
         
            m = world.world.get_map()
        
            w = m.get_waypoint(world.player.get_location())
            print("ROAD ID ..... ",w.road_id)
            print("LOCATION IS ...",world.player.get_location())
            actor_list =  agent._world.get_actors()
            vehicles_list = actor_list.filter("*vehicle*") #liste of vehicule with id and type 
            traffic_manager = client.get_trafficmanager(args.tm_port)
            
            #Change a red traffic light to green
            #Get the traffic light affecting a vehicle
            
            lights_list = actor_list.filter("*traffic_light*")
            #if IsRedLight(agent)==1:
               
               # light_state, traffic_light = agent._is_light_red(lights_list)
              #  if light_state==True:
                   # traffic_light.set_state(carla.TrafficLightState.Green)
                #traffic_light.set_green_time(4.0)
           
            SpeedLimits=actor_list.filter('traffic.speed_limit.*') 
            vehicles = world.world.get_actors().filter('vehicle.*')
            def distance(l):
                t=world.player.get_transform()
                return math.sqrt(
                (l.x - t.location.x) ** 2 + (l.y - t.location.y) ** 2 + (l.z - t.location.z) ** 2)
            def distanceAhead():
                vehicles = world.world.get_actors().filter('vehicle.*')
                if len(vehicles)>1:
                
                    liste = [distance(x.get_location()) for x in vehicles if x.id != world.player.id]
                    return(sorted(liste)[0])
                else :
                    return 2
            
            
            def exit_game():
                """Shuts down program and PyGame"""
                pygame.quit()
                sys.exit()
         
            
            def Msg_speed():
                speed=3.6*math.sqrt(world.player.get_velocity().x**2 + world.player.get_velocity().y**2 + world.player.get_velocity().z**2)
                if speed < 1.2*int(SpeedSigns(agent).split('.')[2]) :
                    return ("You are respecting the current speed limits")
                else:
                    return ("You are over-speeding, can you deacrease your speed ? ")
            def factor_overspeed():
                speed=3.6*math.sqrt(world.player.get_velocity().x**2 + world.player.get_velocity().y**2 + world.player.get_velocity().z**2)
                f=( speed-world.player.get_speed_limit()) *100
                return (f)
            v=world.player.get_velocity()
            low_data = {#"waypoint":w,
                        #"LocationTraffic":LocationTraffic(world),
                        #"RoadOptions":r(1),
                        #"agent_location_x": agent._vehicle.get_location().x, 
                         "TimePygame": str(datetime.timedelta(seconds=float(time.time() - start))).split()[-1],
                        
                        "Speed":(3.6*math.sqrt(world.player.get_velocity().x**2 + world.player.get_velocity().y**2 + world.player.get_velocity().z**2)),
                        "SpeedLimits":world.player.get_speed_limit(),
                        
                       # "Percentage of over-speed":factor_overspeed(), 
                        
                        "Percentage of over-speed":((3.6*math.sqrt(v.x**2 + v.y**2 + v.z**2))-AffectedSpeedLimit(world.player))/AffectedSpeedLimit(world.player)*100,
                        "Speed Msg": Msg_speed(),
                        
                        "State Car": StateCar(agent), 
                        "Traffic_lights": Traffic_lights(agent),
                        "Msg_light":Msg_light(agent), 
                       
                        
                       # "TargetSpeed":agent._target_speed,
                        
                       # "WeatherId":WeatherId(),
                       # "SpeedLimit":AffectedSpeedLimit(world.player),
                        #"SpeedLimitWeather":SpeedLimitByWeather(),
                        
                          #speed in km/h 

                      #  "Traffic_lights":math.sqrt((Traffic_lights(agent).x - agent._vehicle.get_location().x) ** 2 + (Traffic_lights(agent).y - agent._vehicle.get_location().y) ** 2 ), 
                        #"Traffic_speed_limits": math.sqrt((Traffic_speed_limits(agent).x - agent._vehicle.get_location().x) ** 2 + (Traffic_speed_limits(agent).y - agent._vehicle.get_location().y) ** 2 ), 
                       # "Distance ahead Speed_limits":Traffic_speed_limits(agent), 
                        

                        "Weather msg": msg_weather(), 
                        "map":int(world.map.name[-1]),
                        
                        "Cloud":float(args.clouds),
                        "rain":float(args.rain),
                        "wind":float(args.wind),
                        "fog":float(args.fog),
                        "wetness":float(args.wetness),
                        "puddles":float(args.puddles),
                        
                        "SunAltitude":str(args.altitude),
                        #"distanceAhead":distanceAhead(),
                        
                        #"Location_x":t.location.x,
                        #"Location_y":t.location.y,
                        
                    
                        #"State":StateCar(agent),
                        
                
                       # "road_id":w.road_id,
                       # "lane_id":w.lane_id,
                        #"Junction":IsJunction(w),
                     
                        #"lane_change":LaneChange(w),


                        "Vehicle": get_actor_display_name(world.player)
                        

                        }
            data = data.append(low_data, ignore_index=True)
            print(low_data)
            
            Speed_Values.append((3.6*math.sqrt(world.player.get_velocity().x**2 + world.player.get_velocity().y**2 + world.player.get_velocity().z**2)))
            

            o=o+1
            print("STEP N°",o)
            
            
            pygame.display.flip()
              
            control = agent.run_step()
            
            control.manual_gear_shift = False
            
            
        
            
            #agent.set_destination([139,135,4])
           
            agent.set_speed(TargetSpeed())
            i=1
            world.player.apply_control(control)
            
            
           
                
            
                
 
            def MeanSpeed():
                return(round(df["Speed"].mean()))
         
              ##### THIS WILL CREATE THE PATH FOR THE FOLDER './DATASET3/NORMAL/town3' #####
            file4=os.path.join("RSU_DATASET", "NORMAL",world.map.name)
            if not os.path.exists(file4):
                os.makedirs(file4)  
            
                            
        
            for event in pygame.event.get():
                #if agent.done():
                if( (time.time() - start)>500) :
                    exit_game()
                  
                    #pygame.quit()
        
    finally:
     
          
        if world is not None:
            world.destroy()
        
        
        if( (time.time() - start)>60) :
            l3=(os.listdir(file4))
            j=(len(l3))+1
            file3=os.path.join(file4,str(j))
            if not os.path.exists(file3):
                os.makedirs(file3)
                    
                data.to_csv(os.path.join(file3,r'{}_NORMAL_{}_SPEED_{}_Weather_{}.csv'.format(str(j),world.map.name,int(np.mean(Speed_Values)),WeatherId())))
                print("SUCCESFULLY UPLOADED CSV FILE IN {} FOLDER".format(file3))
                    
                   
                
                    #file_name = os.path.join(file2, "normal_SPEED_50.csv")
                df = pd.read_csv(os.path.join(file3,r'{}_NORMAL_{}_SPEED_{}_Weather_{}.csv'.format(str(j),world.map.name,int(np.mean(Speed_Values)),WeatherId())),index_col="TimePygame",parse_dates=True)
                df = df.drop(columns=['Unnamed: 0'])




        #pygame.quit()
        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.Audi.*',
        help='actor filter (default: "vehicle.Audi.*")')
    
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='pedestrians filter (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=10,
        type=int,
        help='number of vehicles (default: 10)')
  
    
    argparser.add_argument("-a", "--agent", type=str,
                           choices=["Roaming", "Basic"],
                           help="select which agent to run",
                           default="Basic")
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    argparser.add_argument(
        '--name',
        default="Sarra",
        type=str,
        help='Name Of Player')
    #WEATHER
    argparser.add_argument(
        '--sun',
        default='day',
        type=str,
        help='Sun position presets [' + ' | '.join([i for i in SUN_PRESETS]) + ']')
    argparser.add_argument(
        '--weather',
        default='clear',
        type=str,
        help='Weather condition presets [' + ' | '.join([i for i in WEATHER_PRESETS]) + ']')
    argparser.add_argument(
        '--altitude', '-alt',
        metavar='A',
        default=90.0,
        type=float,
        help='Sun altitude [-90.0, 90.0]')
    argparser.add_argument(
        '--azimuth', '-azm',
        metavar='A',
        default=None,
        type=float,
        help='Sun azimuth [0.0, 360.0]')
    argparser.add_argument(
        '--clouds', '-c',
        metavar='C',
        default=0.0,
        type=float,
        help='Clouds amount [0.0, 100.0]')
    argparser.add_argument(
        '--rain', '-r',
        metavar='R',
        default=0.0,
        type=float,
        help='Rain amount [0.0, 100.0]')
    argparser.add_argument(
        '--puddles', '-pd',
        metavar='Pd',
        default=0.0,
        type=float,
        help='Puddles amount [0.0, 100.0]')
    argparser.add_argument(
        '--wind', '-w',
        metavar='W',
        default=0.0,
        type=float,
        help='Wind intensity [0.0, 100.0]')
    argparser.add_argument(
        '--fog', '-f',
        metavar='F',
        default=0.0,
        type=float,
        help='Fog intensity [0.0, 100.0]')
    argparser.add_argument(
        '--fogdist', '-fd',
        metavar='Fd',
        default=0.0,
        type=float,
        help='Fog Distance [0.0, inf)')
    argparser.add_argument(
        '--wetness', '-wet',
        metavar='Wet',
        default=0.0,
        type=float,
        help='Wetness intensity [0.0, 100.0]')
    
    argparser.add_argument(
        '-tm_p', '--tm_port',
        metavar='P',
        default=8000,
        type=int,
        help='port to communicate with TM (default: 8000)')
    
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='avoid spawning vehicles prone to accidents')


    
    
    

    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)
    


    print(__doc__)

    try:

        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
    main()
