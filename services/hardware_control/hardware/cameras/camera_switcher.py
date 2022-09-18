# -*- coding: utf-8 -*-
"""Support for camera switcher hardware."""
# Part of Booth Remote (https://github.com/whutch/booth-remote)
# :copyright: (c) 2022 Will Hutcheson
# :license: MIT (https://github.com/whutch/booth-remote/blob/main/LICENSE.txt)

from enum import Enum

import PyATEMMax


class CameraTransitions(Enum):

    NONE = 0
    FADE = 10


class CameraSwitcher:

    def __init__(self):
        self._cameras = {}

    def add_camera(self, key, switcher_key, camera):
        self._cameras[key] = (switcher_key, camera)

    def change_camera(self, key, transition=CameraTransitions.FADE):
        raise NotImplementedError


class ATEMCameraSwitcher(CameraSwitcher):

    def __init__(self, ip):
        super().__init__()
        self._ip = ip
        self._switcher = PyATEMMax.ATEMMax()
    
    def connect(self):
        self._switcher.connect(self._ip)
        self._switcher.waitForConnection()
    
    def disconnect(self):
        self._switcher.disconnect()
    
    def change_camera(self, key, transition=CameraTransitions.FADE):
        switcher_key, camera = self._cameras[key]
        if transition == CameraTransitions.FADE:
            self._switcher.setPreviewInputVideoSource(0, switcher_key)
            self._switcher.execAutoME(0)
