# -*- coding: utf-8 -*-
"""App configuration for main app."""
# Part of Booth Remote (https://github.com/whutch/booth-remote)
# :copyright: (c) 2022 Will Hutcheson
# :license: MIT (https://github.com/whutch/booth-remote/blob/main/LICENSE.txt)

from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "booth_remote.apps.main"
