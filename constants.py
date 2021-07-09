import discord
import config

VoiceMembers = {}
ColorMembers = {}
locations = [859609879210360852, 859609880453447710, 859609881539379210, 859609882646413322]
reactions = [858447122861260820, 858447126274375710, 858447129936789524, 858447133203234848, 858447136587513886, 858447139658924085, 858447145287417916, 858447148767903794]
roles = [856944858946338837, 856944780122128394, 856944897026424852, 857001482134093824, 856945680442589195, 856945820162064416]
colors = [discord.Color.red(), discord.Color.orange(), discord.Color.gold(), discord.Color.green(), discord.Color.blue(), discord.Color.purple(), discord.Color.from_rgb(1, 1, 1), discord.Color.from_rgb(255, 255, 254)]
colorEmoji = ["❤", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍"]
gymHistory = {
    roles[0]: "Slaves вcегда были подчинеными своих мастеров и боссов, но они ещё смогут показать кто лучше делает finger in ur ass",
    roles[1]: "Dungeon master - это тот персонаж, который готов и поиздеваться над slaves и самому принять dick",
    roles[2]: "Boss of this gym не имеет при себе прислужников в виде slaves, но ему всегда есть что показать boys",
    roles[3]: "Full masters - это великие мастера fisting и sex им служат все dungeon master и boss of this gym.\nОни всегда готовы сходить в качалвку и провести осмотр fucking slaves",
    roles[4]: "Главный Dungeon master всегда соревнуется с заклетым врагом",
    roles[5]: "Этот человек готов на всё чтоб завладеть чужим ass!\nНастолько сильно, что смог одолеть dungeon master и стать boss of this gym",
}
locationDesc = {
    locations[0]: "Место обитания boss of this gym и Billy Herengton\nЗдесь проводится эпичные битвы",
    locations[1]: "Сюда стекаются все slaves\nКаждый dungeon master должен оказаться внутри своего подопечного",
    locations[2]: "просто анал",
    locations[3]: "Нипримечательное местечко, можно отдохнуть и покататься на мотоцикле"
}
shopList = {
    "лист": 0,
    "пк": 1,
    "откреп": 2,
    "закреп": 3,
    "ник": 4
}
ytdl_format_options = {
    'format': 'bestaudio',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_before_opts = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
ffmpeg_options = {
    'options': '-vn'
}

token = config.TOKEN