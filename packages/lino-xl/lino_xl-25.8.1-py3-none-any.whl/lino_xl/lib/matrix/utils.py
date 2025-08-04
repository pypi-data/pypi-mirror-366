# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime as dt
import json
from requests import Session
from uuid import uuid4
from lino.api import rt, dd

matrix_server = "https://matrix.org"


def matrix_creds():
    with dd.plugins.matrix.credentials_file.open() as f:
        creds = json.load(f)
    now = dt.datetime.now().astimezone()
    with Session() as ses:
        if (access_token := creds.get("access_token", None)) is None:
            resp = ses.post(f"{matrix_server}/_matrix/client/v3/login", json={
                "identifier": {
                    "type": "m.id.user",
                    "user": creds['user_id'][1:].split(":")[0]},
                "password": creds['user_password'],
                "type": "m.login.password",
                "refresh_token": True,
                "device_id": creds.get('device_id', None),
            })
            resp.raise_for_status()

            json_resp = resp.json()
            creds['access_token'] = json_resp['access_token']
            creds['refresh_token'] = json_resp['refresh_token']
            creds['device_id'] = json_resp['device_id']
            creds['user_id'] = json_resp['user_id']
            creds['expires_at'] = (now + dt.timedelta(
                milliseconds=int(json_resp['expires_in_ms'])
            ) - dt.timedelta(minutes=5)).isoformat()

        elif dt.datetime.fromisoformat(creds['expires_at']) < now:
            resp = ses.post(f"{matrix_server}/_matrix/client/v3/refresh", json={
                "refresh_token": creds['refresh_token']})
            resp.raise_for_status()

            json_resp = resp.json()
            creds['access_token'] = json_resp['access_token']
            creds['refresh_token'] = json_resp['refresh_token']
            creds['expires_at'] = (now + dt.timedelta(
                milliseconds=int(json_resp['expires_in_ms'])
            ) - dt.timedelta(minutes=5)).isoformat()

        with dd.plugins.matrix.credentials_file.open('w') as f:
            json.dump(creds, f)

    return creds


def send_notification_to_matrix_room(msg, room_id=None):
    if room_id is None:
        room_id = dd.plugins.matrix.broadcast_room_id
    with Session() as ses:
        resp = ses.put(f"{matrix_server}/_matrix/client/v3/rooms/"
                       f"{room_id}/send/m.room.message/{uuid4()}",
                       data=json.dumps({"body": msg, "msgtype": "m.text"}),
                       headers={"Authorization": f"Bearer {matrix_creds()['access_token']}"})
        resp.raise_for_status()


def send_notification_direct(msg, user):
    try:
        ut = user.matrix
    except rt.models.matrix.UserTrait.DoesNotExist:
        return

    if not ut.direct_room:
        with Session() as ses:
            resp = ses.post(f"{matrix_server}/_matrix/client/v3/createRoom",
                            data=json.dumps({
                                "invite": [ut.matrix_user_id], "is_direct": True,
                                "preset": "trusted_private_chat"
                            }),
                            headers={"Authorization": f"Bearer {matrix_creds()['access_token']}"})
            resp.raise_for_status()

            json_resp = resp.json()
            ut.direct_room = json_resp["room_id"]
            ut.full_clean()
            ut.save()

    send_notification_to_matrix_room(msg, ut.direct_room)
