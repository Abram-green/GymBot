import dbcontrol
import discord

eventMember = {}

def check(member):
    p = dbcontrol.load_profile(member)
    if eventMember.get(member) is None:
        eventMember.update({member: p["VoiceTime"]})
    else:
        if p["VoiceTime"] - eventMember.get(member) >= 7200:
            p["xp"] += 20000
        else:
            pass
    dbcontrol.save_profile(p, member)