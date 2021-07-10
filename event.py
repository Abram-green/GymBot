import dbcontrol
import discord
import sqlite3


def convert(p):
    data = {
        "res": p[1]
    }
    return data


def connect(name):
    con = sqlite3.connect(name)
    cursor = con.cursor()
    return cursor


def close(cursor):
    cursor.close()


def new_profile(member):
    cur = connect("event.db")
    try:
        sql_request = f"INSERT INTO event (id) VALUES ({member.id})"
        cur.execute(sql_request)
        cur.connection.commit()
    except Exception:
        pass
    close(cur)


def load_profile(member):
    cur = connect("event.db")
    sql_request = f"SELECT * FROM event WHERE `id` = {member.id}"
    user = cur.execute(sql_request).fetchall()
    cur.connection.commit()
    close(cur)
    return convert(list(list(user)[0]))


def save_profile(data, member):
    cur = connect("event.db")
    sql_request = f"UPDATE event SET `res`={data['res']} WHERE `id`={member.id}"
    cur.execute(sql_request)
    cur.connection.commit()
    close(cur)


def check(member):
    p = dbcontrol.load_profile(member)
    try:
        m = load_profile(member)
        res = int(m["res"])
        if res >= 200:
            p["xp"] += 25000
            m = {"res": 10 ** 100 * -1}
            save_profile(m, member)
        else:
            pass
        dbcontrol.save_profile(p, member)
    except Exception:
        data = {
            "res": 0
        }
        new_profile(member)
        save_profile(data, member)
