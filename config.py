from __future__ import print_function

import os
import json
import jsonmerge
import platform

from os.path import sep as os_sep

def overlay_image(l_img, s_img, x_offset, y_offset):
    for c in range(0,3):
        l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] = s_img[:,:,c] * (s_img[:,:,3]/255.0) +  l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] * (1.0 - s_img[:,:,3]/255.0)
    return l_img

class Config(object):
    def __init__(self):
        try:
            self._default_config = json.load(Config._get_default_config())
            self._advanced_config = json.load(Config._get_advanced_config())
            self._merged_config = jsonmerge.merge(self._default_config, self._advanced_config) 

            self._games = {}

            for _, game in self._merged_config['games'].items():
                print("Found available game: %s" % game)
                self._games[game] = json.load(Config._get_game_config(game))

            for key, value in self._merged_config.items():
                setattr(self, key, value)

        except ValueError as err:
            print("Failed loading configurations! %s" % err.message)
            exit(1)

    def get_game_title(self, game_name):
        return self._games[game_name]['title']

    def get_game_description(self, game_name):
        return self._games[game_name]['description']

    def get_game_questions(self, game_name):
        return self._games[game_name]['topics'].items()

    def get_game_all(self, game_name):
        return self._games[game_name].items()

    def get_games(self):
        return self._games.items()

    def get_font_file(self, font_name):
        return Config._get_font_dir() + os_sep + font_name + ".ttf"

    @staticmethod
    def _get_current_dir():
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def _get_config_dir():
        return Config._get_current_dir() + os_sep + "config"

    @staticmethod
    def _get_font_dir():
        return Config._get_current_dir() + os_sep + "fonts"

    @staticmethod
    def _get_default_config():
        return open(Config._get_config_dir() + os_sep + "config.json", 'r')

    @staticmethod
    def _get_advanced_config():
        return open(Config._get_config_dir() + os_sep + "advanced.json", 'r')

    @staticmethod
    def _get_game_config(config_json_name):
        return open(Config._get_config_dir() + os_sep + config_json_name + ".json", 'r')

    def __getitem__(self, key):
        try:
            return self._merged_config.__getitem__(key)
        except KeyError as err:
            print("Configuration error! The configuration key %s doesn't exist!" % err.message)
            exit(1)

    @staticmethod
    def get_system_type():
        system_type = str(platform.system())
        if "win" in system_type.lower():
            return "win"
        else:
            return "nix"
