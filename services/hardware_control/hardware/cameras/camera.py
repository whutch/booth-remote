# -*- coding: utf-8 -*-
"""Support for camera hardware."""
# Part of Booth Remote (https://github.com/whutch/booth-remote)
# :copyright: (c) 2022 Will Hutcheson
# :license: MIT (https://github.com/whutch/booth-remote/blob/main/LICENSE.txt)

from datetime import datetime
import socket

import requests


CAMERAS = {
    1: "192.168.1.88",
    2: "192.168.1.89",
    3: "192.168.1.90",
}


def get_camera_socket(camera):
    ip = CAMERAS[camera]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((f"{ip}", 5678))
    sock.settimeout(0.1)
    return sock


def get_response(sock):
    data = b""
    while not data or data[-1] != ord("\xFF"):
        try:
            data += sock.recv(1)
        except socket.timeout:
            pass
    if data[0] != ord("\x90"):
        raise ValueError(f"bad camera response: {data}")
    return data[1:-1]


def send_command(camera, msg, get_response=False):
    sock = get_camera_socket(camera)
    sock.sendall(msg)
    response = None
    if get_response:
        response = get_response(sock)
    sock.close()


def send_inquiry(camera, msg):
    sock = get_camera_socket(camera)
    sock.sendall(msg)
    response = get_response(sock)
    sock.close()
    return response


def recall(camera, preset):
    msg = b"\x81\x01\x04\x3F\x02"
    msg += bytes((preset,))
    msg += b"\xFF"
    send_command(camera, msg)


def store(camera, preset):
    msg = b"\x81\x01\x04\x3F\x01"
    msg += bytes((preset,))
    msg += b"\xFF"
    send_command(camera, msg)


def clear(camera, preset):
    msg = b"\x81\x01\x04\x3F\x00"
    msg += bytes((preset,))
    msg += b"\xFF"
    send_command(camera, msg)


def get_still(camera, path=None):
    if not path:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        path = f"snapshot-{timestamp}.jpg"
    ip = CAMERAS[camera]
    response = requests.get(f"http://{ip}/snapshot.jpg", stream=True)
    with open(path, "wb") as f:
        for chunk in response:
            f.write(chunk)
