import os
import time
import json
import sqlite3
from constants import *


class unicode:
    def Decode(text):
        return str.encode(text, encoding="utf-8").decode("utf-8", "ignore")
    def Encode(text):
        return str.encode(text, encoding="utf-8")


def connect(name):
    con = sqlite3.connect(name)
    cursor = con.cursor()
    return cursor


def close(cursor):
    cursor.close()


def convert(p):
    data = {
        "level": p[0],
        "xp": p[1],
        "xp_l": p[2],
        "VoiceTime": p[3],
        "VoiceDate": p[4],
        "VoiceDate1": p[5]
    }
    return data


def new_member(member):
    data = {
        "level": 1,
        "xp": 0,
        "xp_l": 100,
        "VoiceTime": 0,
        "VoiceDate": 0,
        "VoiceDate1": 0
    }
    new_profile(member)
    save_profile(data, member)


def new_profile(member):
    cur = connect("db.db")
    try:
        sql_request = f"INSERT INTO users (id) VALUES ({member.id})"
        cur.execute(sql_request)
        cur.connection.commit()
    except Exception:
        pass
    close(cur)


def load_profile(member):
    cur = connect("db.db")
    sql_request = f"SELECT * FROM users WHERE `id` = {member.id}"
    user = cur.execute(sql_request).fetchall()
    cur.connection.commit()
    close(cur)
    return convert(list(list(user)[0]))


def save_profile(data, member):
    cur = connect("db.db")
    sql_request = f"UPDATE users SET `level`={data['level']}, `xp`={data['xp']} WHERE `id`={member.id}"
    cur.execute(sql_request)
    cur.connection.commit()
    sql_request = f"UPDATE users SET `xp_l`={data['xp_l']}, `VoiceTime`={data['VoiceTime']} WHERE `id`={member.id}"
    cur.execute(sql_request)
    cur.connection.commit()
    sql_request = f"UPDATE users SET `VoiceDate`={time.time()}, `VoiceDate1`={time.time()} WHERE `id`={member.id}"
    cur.execute(sql_request)
    cur.connection.commit()
    close(cur)


def time_to_second(time, time1):
    return time - time1


async def update_voice_time(member, date, t=False):
    p = load_profile(member)
    if p.get("VoiceTime") is None:
        p.update({"VoiceTime": 0})
    if t:
        p.update({"VoiceDate1": date})
        second = time_to_second(date, p["VoiceDate"])
        if second >= 2:
            second = 1
        p['xp'] += 0.1
        p.update({"VoiceTime": p.get("VoiceTime") + int(second)})
        ids = []
        for r in member.roles:
            ids.append(r.id)
        if p["xp"] >= 300:
            p["level"] = 2
            p["xp_l"] = 600
        if p["xp"] >= p["xp_l"]:
            p["level"] = 3
            p["xp_l"] = 1200
        if p["xp"] >= p["xp_l"]:
            p["level"] = 4
            p["xp_l"] = 2400
        if p["xp"] >= p["xp_l"]:
            p["level"] = 5
            p["xp_l"] = 3600
        if p["level"] == 5 and 856945820162064416 not in ids:
            try:
                role = member.guild.get_role(roles[roles.index(member.roles[1].id) + 1])
                await member.edit(roles=[role])
                await member.send(f"Ого! Ты уже {role.mention}")
                data = {
                    "level": 1,
                    "xp": 0,
                    "xp_l": 100,
                    "gym_emoji": 0
                }
                p["level"] = data["level"]
                p["xp"] = data["xp"]
                p["xp_l"] = data["xp_l"]
            except Exception:
                pass
        if p["level"] == 5 and 856945820162064416 in ids:
            p["xp_l"] = 1000000
    else:
        p.update({"VoiceDate": date})
    save_profile(p, member)