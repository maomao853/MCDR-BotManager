#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
Created on 2021/3/2

@author: Jerry_FaGe
"""
import os
import json
import time
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread

PLUGIN_METADATA = {
    'id': 'bot_manager',
    'version': '1.0.0',
    'name': 'Bot Manager', # RText component is allowed
    'description': {
        'en_us': 'Store and manage carpet bots facilitating command input',
        'zh_cn': '储存假人位置朝向信息并提供昵称映射和简化指令'
    }, # RText component is allowed
    'author': [
        'Jerry-FaGe',
        'maomao853'
    ],
    'link': 'https://github.com/Jerry-FaGe/MCDR-BotKikai',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
        'minecraft_data_api': '*',
    }
}

config_path = './config/BotKikai.json'
prefix = '!!bot'
permission_bot = 1  # 操作假人(spawn,use,kill)的最低权限  guest: 0, user: 1, helper: 2, admin: 3, owner: 4
permission_list = 3  # 操作假人列表(add,remove)的最低权限  guest: 0, user: 1, helper: 2, admin: 3, owner: 4
dimension_convert = {
    '0': 'minecraft:overworld',
    '-1': 'minecraft:the_nether',
    '1': 'minecraft:the_end',
    'overworld': 'minecraft:overworld',
    'the_nether': 'minecraft:the_nether',
    'the_end': 'minecraft:the_end',
    'nether': 'minecraft:the_nether',
    'end': 'minecraft:the_end',
    'minecraft:overworld': 'minecraft:overworld',
    'minecraft:the_nether': 'minecraft:the_nether',
    'minecraft:the_end': 'minecraft:the_end',
    'zhushijie': 'minecraft:overworld',
    'diyu': 'minecraft:the_nether',
    'xiajie': 'minecraft:the_nether',
    'modi': 'minecraft:the_end'
}
bot_dic = {}
bot_list = []

# Help message
help_msg = '''
========== §bBot Manager §r==========
一个帮助§6管理§r和§6控制§rcarpet假人的插件
§d【使用说明】
§b{prefix} §r显示本帮助信息
§b{prefix} list §r显示假人列表
§b{prefix} reload §r重载插件配置
§b{prefix} add <name> <desc> §r使用当前玩家参数添加一个名为<name>用于<desc>的假人
§b{prefix} add <name> <desc> <dim> <pos> <facing> §r使用自定义参数添加一个名为<name>用于<desc>的假人
§b{prefix} del <desc> §r从假人列表移除用于<desc>的假人
§b{prefix} <name> §r输出一个可点击的界面，自动根据假人是否在线改变选项
§b{prefix} <name> spawn §r召唤一个用于<desc>的假人
§b{prefix} <name> kill §r干掉用于<desc>的假人
§b{prefix} <name> use §r假人右键一次§r（执行此条前无需执行spawn，如假人不在线会自动上线）
'''.format(prefix=prefix)

help_msg_en = '''
========== §bBot Manager §r==========
A plugin that helps §6manage §rand §6control §rcarpet bots.
§d[Commands]
§b{prefix} §r显示本帮助信息
§b{prefix} list §r显示假人列表
§b{prefix} reload §r重载插件配置
§b{prefix} add <name> <desc> §r使用当前玩家参数添加一个名为<name>用于<desc>的假人
§b{prefix} add <name> <desc> <dim> <pos> <facing> §r使用自定义参数添加一个名为<name>用于<desc>的假人
§b{prefix} del <desc> §r从假人列表移除用于<desc>的假人
§b{prefix} <name> §r输出一个可点击的界面，自动根据假人是否在线改变选项
§b{prefix} <name> spawn §r召唤一个用于<desc>的假人
§b{prefix} <name> kill §r干掉用于<desc>的假人
§b{prefix} <name> use §r假人右键一次§r（执行此条前无需执行spawn，如假人不在线会自动上线）
'''.format(prefix=prefix)

# Help message separated
help_head = """
========== §bBot Manager §r==========
一个帮助§6管理§r和§6控制§rcarpet假人的插件
"""

help_head_en = """
========== §bBot Manager §r==========
A plugin that helps §6manage §rand §6control §rcarpet bots.
"""

help_body = {
    f"§d【使用说明】": "",
    f"§b{prefix}": "§r显示本帮助信息",
    f"§b{prefix} list": "§r显示假人列表",
    f"§b{prefix} reload": "§r重载插件配置",
    f"§b{prefix} add <name> <desc>": "§r使用当前玩家参数添加一个名为<name>用于<desc>的假人",
    f"§b{prefix} add <name> <desc> <dim> <pos> <facing>": "§r使用自定义参数添加一个名为<name>用于<desc>的假人",
    f"§b{prefix} del <desc>": "§r从假人列表移除用于<desc>的假人",
    f"§b{prefix} <name>": "§r输出一个可点击的界面，自动根据假人是否在线改变选项",
    f'§b{prefix} <name> spawn': "§r召唤一个用于<desc>的假人",
    f"§b{prefix} <name> kill": "§r干掉用于<desc>的假人",
    f"§b{prefix} <name> use": "§r假人右键一次§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
    f"§b{prefix} <name> huse": "§r假人持续右键(内测)§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
    f"§b{prefix} <name> hattack": "§r假人持续左键(内测)§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
}

help_body_en = {
    f"§d[Commands]": "",
    f"§b{prefix}": "§r显示本帮助信息",
    f"§b{prefix} list": "§r显示假人列表",
    f"§b{prefix} reload": "§r重载插件配置",
    f"§b{prefix} add <name> <desc>": "§r使用当前玩家参数添加一个名为<name>用于<desc>的假人",
    f"§b{prefix} add <name> <desc> <dim> <pos> <facing>": "§r使用自定义参数添加一个名为<name>用于<desc>的假人",
    f"§b{prefix} del <desc>": "§r从假人列表移除用于<desc>的假人",
    f"§b{prefix} <name>": "§r输出一个可点击的界面，自动根据假人是否在线改变选项",
    f'§b{prefix} <name> spawn': "§r召唤一个用于<desc>的假人",
    f"§b{prefix} <name> kill": "§r干掉用于<desc>的假人",
    f"§b{prefix} <name> use": "§r假人右键一次§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
    f"§b{prefix} <name> huse": "§r假人持续右键(内测)§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
    f"§b{prefix} <name> hattack": "§r假人持续左键(内测)§r（执行此条前无需执行spawn，如假人不在线会自动上线）",
}


def read():
    global bot_dic
    with open(config_path, encoding='utf8') as f:
        bot_dic = json.load(f)


def save():
    with open(config_path, 'w', encoding='utf8') as f:
        json.dump(bot_dic, f, indent=4, ensure_ascii=False)


def search(kikai):
    for k, v in bot_dic.items():
        if kikai in v['nick']:
            return k


def auth_player(player):
    """验证玩家是否为bk假人"""
    lower_dic = {i.lower(): i for i in bot_dic}
    bot_name = lower_dic.get(player.lower(), None)
    return bot_name if bot_name else None


def get_pos(server, info):
    api = server.get_plugin_instance('minecraft_data_api')
    pos = api.get_player_info(info.player, 'Pos')
    dim = api.get_player_info(info.player, 'Dimension')
    facing = api.get_player_info(info.player, 'Rotation')
    return pos, dim, facing


def spawn_cmd(server, info, name):
    dim = bot_dic[name]['dim']
    pos = ' '.join([str(i) for i in bot_dic[name]['pos']])
    facing = bot_dic[name]['facing']
    if info.is_player:
        return f'/execute as {info.player} run player {name} spawn at {pos} facing {facing} in {dim}'
    else:
        return f'/player {name} spawn at {pos} facing {facing} in {dim}'


def spawn(server, info, name):
    return spawn_cmd(server, info, name)


def kill(name):
    return f'/player {name} kill'


def use(name):
    return f'/player {name} use'


def hold_attack(name):
    return f'/player {name} attack continuous'


def hold_use(name):
    return f'/player {name} use continuous'


@new_thread(PLUGIN_METADATA["name"])
def operate_bot(server, info, args):
    global bot_dic, bot_list
    permission = server.get_permission_level(info)

    if len(args) == 1:
        # !!bot
        # server.reply(info, help_msg)
        head = [help_head]
        body = [RText(f'{k} {v}\n').c(
            RAction.suggest_command, k.replace('§b', '')).h(v)
                for k, v in help_body.items()]
        server.reply(info, RTextList(*(head + body)))
    elif len(args) == 2:
        # !!bot list
        if args[1] == "list":
            c = ['']
            for name, bot_info in bot_dic.items():
                if name in bot_list:
                    bot_msg = RTextList(
                        '\n'
                        f'§7----------- §6{name} §a在线 §7 -----------\n',
                        f'§7此假人用于:§6 {bot_info["nick"]}\n',
                        # f'§7Dimension:§6 {bot_info["dim"]}\n',
                        # RText(
                        #     f'§7Position:§6 {bot_info["pos"]}\n', ).c(
                        #     RAction.run_command,
                        #     '[x:{}, y:{}, z:{}, name:{}, dim{}]'.format(
                        #         *[int(i) for i in bot_info['pos']], name, bot_info['dim'])).h(
                        #     '点击显示可识别坐标点'),
                        # f'§7Facing:§6 {bot_info["facing"]}\n',
                        RText('§d[点击use]  ').c(
                            RAction.run_command, f'{prefix} {name} use').h(f'§6{name}§7右键一次'),
                        RText('§d[点击下线]  ').c(
                            RAction.run_command, f'{prefix} {name} kill ').h(f'下线§6{name}'),
                        RText('§d[查看详情]  ').c(
                            RAction.run_command, f'{prefix} {name}').h(f'显示§6{name}§r的详细信息')
                    )
                else:
                    bot_msg = RTextList(
                        '\n'
                        f'§7----------- §6{name} §4离线 §7 -----------\n',
                        f'§7此假人用于:§6 {bot_info["nick"]}\n',
                        # f'§7Dimension:§6 {bot_info["dim"]}\n',
                        # RText(
                        #     f'§7Position:§6 {bot_info["pos"]}\n', ).c(
                        #     RAction.run_command,
                        #     '[x:{}, y:{}, z:{}, name:{}, dim{}]'.format(
                        #         *[int(i) for i in bot_info['pos']], name, bot_info['dim'])).h(
                        #     '点击显示可识别坐标点'),
                        # f'§7Facing:§6 {bot_info["facing"]}\n',
                        RText('§d[点击召唤]  ').c(
                            RAction.run_command, f'{prefix} {name} spawn').h(f'召唤§6{name}'),
                        RText('§d[点击use]  ').c(
                            RAction.run_command, f'{prefix} {name} use ').h(f'召唤§6{name}§r并右键一次'),
                        RText('§d[查看详情]  ').c(
                            RAction.run_command, f'{prefix} {name}').h(f'显示§6{name}§r的详细信息')
                    )
                c.append(bot_msg)
            server.reply(info, RTextList(*c))
        # !!bot reload
        elif args[1] == "reload":
            try:
                read()
                server.say('§b[BotKikai]§a由玩家§d{}§a发起的BotKikai重载成功'.format(info.player))
            except Exception as e:
                server.say('§b[BotKikai]§4由玩家§d{}§4发起的BotKikai重载失败：{}'.format(info.player, e))
        # !!bot <Name>
        elif search(args[1]):
            name = search(args[1])
            if name not in bot_list:
                msg = RTextList(
                    '\n'
                    f'§7----------- §6{name} §4离线 §7-----------\n',
                    f'§7此假人用于:§6 {bot_dic.get(name)["nick"]}\n',
                    f'§7维度:§6 {bot_dic.get(name)["dim"]}\n',
                    RText(
                        f'§7坐标:§6 {bot_dic.get(name)["pos"]}\n', ).c(
                        RAction.run_command,
                        '[x:{}, y:{}, z:{}, name:{}, dim{}]'.format(
                            *[int(i) for i in bot_dic.get(name)['pos']], name, bot_dic.get(name)['dim'])).h(
                        '点击显示可识别坐标点'),
                    f'§7朝向:§6 {bot_dic.get(name)["facing"]}\n',
                    RText('§d[点击召唤]  ').c(
                        RAction.run_command, f'{prefix} {name} spawn').h(f'召唤§6{name}'),
                    RText('§d[点击use]  ').c(
                        RAction.run_command, f'{prefix} {name} use ').h(f'召唤§6{name}并右键一次')
                )
            else:
                msg = RTextList(
                    '\n'
                    f'§7----------- §6{name} §a在线 §7-----------\n',
                    f'§7此假人用于:§6 {bot_dic.get(name)["nick"]}\n',
                    f'§7维度:§6 {bot_dic.get(name)["dim"]}\n',
                    RText(
                        f'§7坐标:§6 {bot_dic.get(name)["pos"]}\n', ).c(
                        RAction.run_command,
                        '[x:{}, y:{}, z:{}, name:{}, dim{}]'.format(
                            *[int(i) for i in bot_dic.get(name)['pos']], name, bot_dic.get(name)['dim'])).h(
                        '点击显示可识别坐标点'),
                    f'§7朝向:§6 {bot_dic.get(name)["facing"]}\n',
                    RText('§d[点击use]  ').c(
                        RAction.run_command, f'{prefix} {name} use').h(f'§6{name}§7右键一次'),
                    RText('§d[点击下线]  ').c(
                        RAction.run_command, f'{prefix} {name} kill ').h(f'下线§6{name}')
                )
            server.reply(info, msg)
        # Invalid command
        else:
            server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")
    elif len(args) == 3:
        # !!bot del <Name>
        if args[1] == "del" and permission >= permission_list:
            name = search(args[2])
            if name:
                del bot_dic[name]
                bot_list.remove(name) if name in bot_list else bot_list
                save()
                server.reply(info, f'§b[BotKikai]§a已删除机器人{name}')
            else:
                server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")
        # !!bot <Name> <command>
        else:
            name = search(args[1])
            if name:
                # !!bot <Name> spawn
                if args[2] == "spawn" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已创建假人§d{name}§6（{args[1]}）")
                    else:
                        server.reply(info, f"§b[BotKikai]§4假人§d{name}§6（{args[1]}）§4已经在线")
                # !!bot <Name> kill
                elif args[2] == "kill" and permission >= permission_bot:
                    if name in bot_list:
                        server.execute(kill(name))
                        server.reply(info, f"§b[BotKikai]§a假人§d{name}§6（{args[1]}）§a已被下线")
                # !!bot <Name> use
                elif args[2] == "use" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}§6（{args[1]}）")
                        time.sleep(2)
                    server.execute(use(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§6（{args[1]}）§a右键一次")
                # !!bot <Name> huse
                elif args[2] == "huse" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}§6（{args[1]}）")
                        time.sleep(2)
                    server.execute(hold_use(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§6（{args[1]}）§a持续右键")
                # !!bot <Name> hattack
                elif args[2] == "hattack" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}§6（{args[1]}）")
                        time.sleep(2)
                    server.execute(hold_attack(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§6（{args[1]}）§a持续左键")
                # Invalid command
                else:
                    server.reply(info, f"§b[BotKikai]§4参数输入错误，输入§6{prefix}§4查看帮助信息")
            else:
                server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")
    elif len(args) == 4:
        # !!bot add <Name> <Description>
        if args[1] == 'add' and permission >= permission_list:
            nick_ls = [] if bot_dic.get(args[2], None) is None else bot_dic.get(args[2])['nick']
            if args[2] not in nick_ls:
                nick_ls.append(args[2])
            nick_ls.append(args[3]) if args[3] != args[2] else nick_ls
            pos, dim, facing = get_pos(server, info)
            bot_dic[args[2]] = {
                'nick': nick_ls,
                'dim': dim,
                'pos': pos,
                'facing': f'{facing[0]} {facing[1]}'
            }
            save()
            server.reply(info, f'§b[BotKikai]§a已添加假人{args[2]}')
        # Invalid command
        else:
            server.reply(info, '§b[BotKikai]§4命令格式不正确或权限不足')
    elif len(args) == 10:
        # !!bot add <Name> <Description> <Dim> <Pos-x,y,z> <Facing-yaw,pitch>
        if args[1] == 'add' and permission >= permission_list:
            if args[4] in dimension_convert.keys():
                dim = dimension_convert[args[4]]
                pos = [int(i) for i in [args[5], args[6], args[7]]]
                facing = f'{args[8]} {args[9]}'
                nick_ls = [] if bot_dic.get(args[2], None) is None else bot_dic.get(args[2])['nick']
                if args[2] not in nick_ls:
                    nick_ls.append(args[2])
                nick_ls.append(args[3]) if args[3] != args[2] else nick_ls
                bot_dic[args[2]] = {
                    'nick': nick_ls,
                    'dim': dim,
                    'pos': pos,
                    'facing': facing
                }
                save()
                server.reply(info, f'§b[BotKikai]§a已添加假人{args[2]}')
            else:
                server.reply(info, '§b[BotKikai]§4无法识别的维度')
        else:
            server.reply(info, '§b[BotKikai]§4命令格式不正确或权限不足')


def on_load(server, old):
    global bot_list
    server.register_help_message(f'{prefix}', RText(
        '假人器械映射').c(RAction.run_command, f'{prefix}').h('点击查看帮助'))
    if old is not None and old.bot_list is not None:
        bot_list = old.bot_list
    else:
        bot_list = []
    if not os.path.isfile(config_path):
        save()
    else:
        try:
            read()
        except Exception as e:
            server.say('§b[BotKikai]§4配置加载失败，请确认配置路径是否正确：{}'.format(e))


def on_player_joined(server, player, info):
    bot_name = auth_player(player)
    if bot_name:
        if bot_name not in bot_list:
            bot_list.append(bot_name)


def on_player_left(server, player):
    bot_name = auth_player(player)
    if bot_name:
        if bot_name in bot_list:
            bot_list.remove(bot_name)


def on_info(server, info):
    if info.is_user:
        if info.content.startswith(prefix) or info.content.startswith(prefix):
            info.cancel_send_to_server()
            args = info.content.split(' ')
            operate_bot(server, info, args)


def on_server_stop(server, return_code):
    global bot_list
    bot_list = []
