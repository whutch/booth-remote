# -*- coding: utf-8 -*-
"""Support for camera hardware."""
# Part of Booth Remote (https://github.com/whutch/booth-remote)
# :copyright: (c) 2022 Will Hutcheson
# :license: MIT (https://github.com/whutch/booth-remote/blob/main/LICENSE.txt)

from datetime import datetime
import socket
import time

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


def hex_to_int(_bytes):
    _int = 0
    for index, byte in enumerate(_bytes[::-1]):
        _int += byte * (16 ** index)
    return _int


def int_to_hex(_int, min_length=1):
    _bytes = []
    power = 0
    while _int > 0:
        power += 1
        remainder = _int % (16 ** power)
        byte = remainder // (16 ** (power - 1))
        _bytes.append(byte)
        _int -= remainder
    while len(_bytes) < min_length:
        _bytes += b"\x00"
    return bytes(_bytes)[::-1]


def get_position(camera):
    msg = b"\x81\x09\x06\x12\xFF"
    data = send_inquiry(camera, msg)
    pan = hex_to_int(data[1:5])
    tilt = hex_to_int(data[5:])
    return (pan, tilt)


def set_position(camera, pan, tilt, speed=10):
    msg = b"\x81\x01\x06\x02"
    # speed 1-20 tilt, 1-24 pan
    msg += bytes((speed, speed))
    msg += int_to_hex(pan, min_length=4)
    msg += int_to_hex(tilt, min_length=4)
    msg += b"\xFF"
    send_command(camera, msg)


def get_zoom(camera):
    msg = b"\x81\x09\x04\x47\xFF"
    data = send_inquiry(camera, msg)
    zoom = hex_to_int(data[1:5])
    return zoom


def set_zoom(camera, zoom):
    msg = b"\x81\x01\x04\x47"
    msg += int_to_hex(zoom, min_length=4)
    msg += b"\xFF"
    send_command(camera, msg)


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


def stop(camera, speed=10):
    msg = b"\x81\x01\x06\x01"
    msg += bytes((speed, speed))
    msg += b"\x03\x03\xFF"
    send_command(camera, msg)


def home(camera):
    msg = b"\x81\x01\x06\x04\xFF"
    send_command(camera, msg)


def reset(camera):
    msg = b"\x81\x01\x06\x05\xFF"
    send_command(camera, msg)


def _move_direction(camera, direction, allow_time=0.3, speed=10):
    msg = b"\x81\x01\x06\x01"
    msg += bytes((speed, speed))
    msg += direction
    msg += b"\xFF"
    send_command(camera, msg)
    if (allow_time):
        time.sleep(allow_time)
    stop(camera, speed)


def up(camera, allow_time=0.3, speed=10):
    _move_direction(camera, b"\x03\x01", allow_time=allow_time, speed=speed)


def down(camera, allow_time=0.3, speed=10):
    _move_direction(camera, b"\x03\x02", allow_time=allow_time, speed=speed)


def left(camera, allow_time=0.3, speed=10):
    _move_direction(camera, b"\x01\x03", allow_time=allow_time, speed=speed)


def right(camera, allow_time=0.3, speed=10):
    _move_direction(camera, b"\x02\x03", allow_time=allow_time, speed=speed)


def zoom_in(camera, amount=500):
    zoom = get_zoom(camera)
    new_zoom = max(0, min(16384, zoom + amount))
    set_zoom(camera, new_zoom)


def zoom_out(camera, amount=500):
    zoom = get_zoom(camera)
    new_zoom = max(0, min(16384, zoom - amount))
    set_zoom(camera, new_zoom)


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
