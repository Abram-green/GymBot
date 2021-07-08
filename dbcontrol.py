import os
import time
import json


locations = [859609879210360852, 859609880453447710, 859609881539379210, 859609882646413322]
roles = [856944858946338837, 856944780122128394, 856944897026424852, 857001482134093824, 856945680442589195, 856945820162064416]


class unicode:
    def Decode(text):
        return str.encode(text, encoding="utf-8").decode("utf-8", "ignore")
    def Encode(text):
        return str.encode(text, encoding="utf-8")


def new_profile(member):
    data = {
        "level": 1,
        "xp": 0,
        "xp_l": 100,
        "gym_emoji": 0,
        "VoiceTime": 0,
    }
    save_profile(data, member)


def load_profile(member):
    with open("UserData/" + str(member) + ".json", "r") as file:
        json_data = file.read()
    profile = json.loads(json_data)
    return profile


def save_profile(json_data, member):
    json_data = json.dumps(json_data)
    with open("UserData/" + str(member) + ".json", "w") as file:
        file.write(json_data)


def time_to_second(time, time1):
    time = time.split(":")
    day = int(time[0])
    hour = int(time[1])
    minute = int(time[2])
    second = int(time[3])
    time1 = time1.split(":")
    day1 = int(time1[0])
    hour1 = int(time1[1])
    minute1 = int(time1[2])
    second1 = int(time1[3])
    return (second + (minute * 60) + (hour * 60 * 60) + (day * 24 * 60 * 60)) - (second1 + (minute1 * 60) + (hour1 * 60 * 60) + (day1 * 24 * 60 * 60))


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