import discord
import random
import json
from dotenv import load_dotenv
import time
import keep_alive
import os
import datetime as dt

client = discord.Client()

# 開啟各種資料夾
with open("datas/sentence_library.json", encoding="utf-8") as f:
    lib = json.load(f)

with open("datas/datas.json", 'r', encoding="utf-8") as f:
    datas = json.load(f)

with open("datas/ban_word.json", 'r', encoding="utf-8") as f:
    ban_words = json.load(f)

with open("datas/find_library.json", 'r', encoding="utf-8") as f:
    findlib = json.load(f)

if datas["bot_token"] == "token":
    datas["bot_token"] = os.getenv("token", None)
if datas["master_signal"] == "signal":
    datas["master_signal"] = os.getenv("signal", None)

# 功能函式區

# 學習回答

async def learn(message, sents):
    if datas["ban_common"]:
        for key in ban_words.keys():
            for i in ban_words[key]:
                if i in sents[1]:
                    await message.channel.send(datas["ban_word"])
                    return
    elif message.guild.name in ban_words.keys():
        for i in ban_words[message.guild.name]:
            if i in sents[1]:
                await message.channel.send(datas["ban_word"])
                return

    for i in range(len(sents)-2):
        cont = False
        if datas["ban_common"]:
            for key in ban_words.keys():
                for j in ban_words[key]:
                    if j in sents[2+i]:
                        await message.channel.send(datas["ban_word"])
                        cont = True
                        break
        elif message.guild.name in ban_words.keys():
            for j in ban_words[message.guild.name]:
                if j in sents[2+i]:
                    await message.channel.send(datas["ban_word"])
                    cont = True
                    break
        if not cont:
            cont = True
            if sents[1] in lib:
                for j in range(len(lib[sents[1]])):
                    if lib[sents[1]][j]["回答"] == sents[2+i] and lib[sents[1]][j]["伺服器"] == message.guild.name:
                        await message.channel.send(datas["have_learnt"])
                        cont = False
                        break
            if cont:
                if sents[1] in lib:
                    lib[sents[1]].append(
                        {"回答": sents[2+i], "時間": time.ctime(), "老師": message.author.name, "伺服器": message.guild.name})
                else:
                    lib[sents[1]] = [
                        {"回答": sents[2+i], "時間":time.ctime(), "老師":message.author.name, "伺服器":message.guild.name}]
                await message.channel.send(datas["learnt"].format(sents[2+i]))
    with open("datas/sentence_library.json", 'w', encoding="utf-8") as f:
        json.dump(lib, f, ensure_ascii=False)

# 忘記回答


async def forget(message, sents):
    if message.author.id in datas["master_id"] or datas["can_forget"] and len(sents) > 1:
        if sents[1] in lib or sents[1] in findlib.keys():
            if sents[1] in lib:
                for i in range(len(sents)-2):
                    cont = True
                    for j in range(len(lib[sents[1]])):
                        if lib[sents[1]][j]["回答"] == sents[2+i]:
                            lib[sents[1]].pop(j)
                            if len(lib[sents[1]]) == 0:
                                del lib[sents[1]]
                            await message.channel.send(datas["forget"].format(sents[2+i]))
                            cont = False
                            break
                    if cont and not sents[1] in findlib.keys():
                        await message.channel.send(datas["do_not_know"].format(sents[2+i]))
                with open("datas/sentence_library.json", 'w', encoding="utf-8") as f:
                    json.dump(lib, f, ensure_ascii=False)
            if sents[1] in findlib.keys():
                for i in range(len(sents)-2):
                    cont = True
                    for j in range(len(findlib[sents[1]])):
                        if findlib[sents[1]][j]["回答"] == sents[2+i]:
                            findlib[sents[1]].pop(j)
                            await message.channel.send(datas["forget"].format(sents[2+i]))
                            if len(findlib[sents[1]]) == 0:
                                del findlib[sents[1]]
                            cont = False
                            break
                    if cont and not sents[1] in lib:
                        await message.channel.send(datas["do_not_know"].format(sents[2+i]))
                with open("datas/find_library.json", 'w', encoding="utf-8") as f:
                    json.dump(findlib, f, ensure_ascii=False)
        else:
            await message.channel.send(datas["do_not_know"].format(sents[1]))

# 禁字設定


async def ban_word(message, sents):
    if message.author.id in datas["master_id"] or datas["can_add_ban"]:
        if not message.guild.name in ban_words.keys():
            ban_words[message.guild.name] = []
            with open("datas/datas.json", 'w', encoding="utf-8") as f:
                json.dump(datas, f, ensure_ascii=False)
        for i in range(len(sents)-1):
            if sents[1+i] in ban_words[message.guild.name]:
                await message.channel.send(datas["knew_ban_word"])
            else:
                ban_words[message.guild.name].append(sents[1+i])
                await message.channel.send(datas["learn_ban_word"].format(sents[1+i]))
        with open("datas/ban_word.json", 'w', encoding="utf-8") as f:
            json.dump(ban_words, f, ensure_ascii=False)

# 解除禁字


async def lift_ban_word(message, sents):
    if message.author.id in datas["master_id"] or datas["can_lift_ban"]:
        if not message.guild.name in ban_words.keys():
            await message.channel.send(datas["no_ban_word"].format(sents[1]))
            return
        for i in range(len(sents)-1):
            if not sents[i+1] in ban_words[message.guild.name]:
                await message.channel.send(datas["no_ban_word"].format(sents[1]))
                continue
            for j in range(len(ban_words[message.guild.name])):
                if ban_words[message.guild.name][j] == sents[i+1]:
                    ban_words[message.guild.name].pop(j)
                    await message.channel.send(datas["lift_ban_word"].format(sents[i+1]))
                    if len(ban_words[message.guild.name]) == 0:
                        del ban_words[message.guild.name]
                    with open("datas/ban_word.json", 'w', encoding="utf-8") as f:
                        json.dump(ban_words, f, ensure_ascii=False)
                    break


# 偵測字設定


async def find(message, sents):
    if len(sents) < 2:
        return
    if datas["ban_common"]:
        for key in ban_words.keys():
            for i in ban_words[key]:
                if i in sents[1]:
                    await message.channel.send(datas["ban_word"])
                    break
    elif message.guild.name in ban_words.keys():
        for i in ban_words[message.guild.name]:
            if i in sents[1]:
                await message.channel.send(datas["ban_word"])
                return
    for i in range(len(sents)-2):
        cont = False
        if message.guild.name in ban_words.keys():
            for j in ban_words[message.guild.name]:
                if j in sents[2+i]:
                    await message.channel.send(datas["ban_word"])
                    cont = True
                    break
        if not cont:
            cont = True
            if sents[1] in findlib.keys():
                for j in range(len(findlib[sents[1]])):
                    if findlib[sents[1]][j]["回答"] == sents[2+i]:
                        await message.channel.send(datas["have_learnt"])
                        cont = False
                        break
            if cont:
                if sents[1] in findlib.keys():
                    findlib[sents[1]].append(
                        {"回答": sents[2+i], "時間": time.ctime(), "老師": message.author.name, "伺服器": message.guild.name})
                else:
                    findlib[sents[1]] = [
                        {"回答": sents[2+i], "時間":time.ctime(), "老師":message.author.name, "伺服器":message.guild.name}]
                await message.channel.send(datas["learnt"].format(sents[2+i]))

    with open("datas/find_library.json", 'w', encoding="utf-8") as f:
        json.dump(findlib, f, ensure_ascii=False)

# 抽籤


async def draw(message, sents):
    await message.channel.send(datas["draw_word"].format(random.choice(sents[1:len(sents)-1])))
    
# 紀念拉比
async def memory(message):
    today = dt.date.today()
    that_date = dt.datetime(2021, 5, 15).date()
    days = (today - that_date).days
    await message.channel.send("拉比已經回深淵{}天了，祝她在深淵過的開心".format(days))

# 查詢句子


async def search(message, sents):
    if sents[1] in lib:
        if datas["learn_common"]:
            for key in lib[sents[1]]:
                await message.channel.send("回答：{}; 時間：{}; 老師：{}; 伺服器：{}".format(key["回答"], key["時間"], key["老師"], key["伺服器"]))
        else:
            for key in lib[sents[1]]:
                if key["伺服器"] == message.guild.name():
                    await message.channel.send("回答：{}; 時間：{}; 老師：{}".format(key["回答"], key["時間"], key["老師"]))
    else:
        await message.channel.send(datas["do_not_know"].format(sents[1]))



# 設定系統通知頻道


async def set_system_channel(message, sents):
    datas["system_channels"].append(message.channel.id)
    await message.channel.send(datas["set_system_channels_word"])
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)

# 設定通知頻道


async def set_announce_channel(message, sents):
    datas["announce_channels"].append(message.channel.id)
    await message.channel.send(datas["set_announce_channels_word"])
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)

# 廣域通知


async def announce(message, sents):
    for channel in datas["announce_channels"]:
        await client.get_channel(channel).send(' '.join(sents[1:]))

# 指令列表


async def help(message, sents):
    await message.channel.send(
        '''
        ```
        {} 觸發詞 回答1 回答2
        {} 觸發詞 要刪掉的回答1 要刪掉的回答2
        {} 新禁字1 新禁字2 
        {} 解除的禁字1 解除的禁字2
        {} 觸發詞（有包含就行） 回答1 回答2
        {} 籤1 籤2 籤3 (抽籤）
        {} 察看目前有的指令
        ```
        '''.format(datas["learn_command"], datas["forget_command"], datas["ban_command"], datas["lift_ban_command"], datas["find_command"],
                   datas["draw_command"], datas["help_command"])
    )


# 設定管理員權限

async def set_administrator(message, sents):
    if not message.author.id in datas["master_id"]:
        datas["master_id"].append(message.author.id)
        await message.channel.send(datas["set_administrator"].format(message.author.name))
        for channel in datas["system_channels"]:
            await client.get_channel(channel).send(datas["set_administrator"]).format(message.author.name)
        with open("datas/datas.json", 'w', encoding="utf-8") as f:
            json.dump(datas, f, ensure_ascii=False)

# 設定新指令/回答


async def change_command(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    global funcs
    in_key = False
    for key in datas.keys():
        if datas[key] == sents[1]:
            datas[key] = sents[2]
            in_key = True
    if not in_key:
        await message.channel.send(datas["no_command_word"])
        return
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)
    funcs[sents[2]] = funcs[sents[1]]
    del funcs[sents[1]]
    await message.channel.send(datas["change_command_word"].format(message.author.name, sents[1], sents[2]))
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_command_word"].format(message.author.name, sents[1], sents[2]))


# 更改普通使用者的權限

async def change_add_ban_permission(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["can_add_ban"] = not datas["can_add_ban"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "can_add_ban", not datas["can_add_ban"], datas["can_add_ban"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


async def change_forget_permission(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["can_forget"] = not datas["can_forget"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "can_forget", not datas["can_forget"], datas["can_forget"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


async def change_lift_ban_permission(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["can_lift_ban"] = not datas["can_lift_ban"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "can_lift_ban", not datas["can_lift_ban"], datas["can_lift_ban"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


async def change_sentence_common(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["sentence_common"] = not datas["sentence_common"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "sentence_common", not datas["sentence_common"], datas["sentence_common"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


async def change_find_common(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["find_common"] = not datas["find_common"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "find_common", not datas["find_common"], datas["find_common"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


async def change_ban_common(message, sents):
    if not message.author.id in datas["master_id"]:
        await message.channel.send(datas["permission_not_enough_word"])
        return
    datas["ban_common"] = not datas["ban_common"]
    for channel in datas["system_channels"]:
        await client.get_channel(channel).send(datas["change_permission_word"].format(message.author.name, "ban_common", not datas["ban_common"], datas["ban_common"]))
    with open("datas/datas.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False)


# 函式庫

funcs = {
    datas["master_signal"]: set_administrator,
    datas["learn_command"]: learn,
    datas["forget_command"]: forget,
    datas["ban_command"]: ban_word,
    datas["lift_ban_command"]: lift_ban_word,
    datas["find_command"]: find,
    datas["draw_command"]: draw,
    datas["memory_command"]: memory,
    datas["search_command"]: search,
    datas["help_command"]: help,
    datas["set_announce_channel"]: set_announce_channel,
    datas["set_system_channel"]: set_system_channel,
    datas["announce_command"]: announce,
    datas["change_command"]: change_command,
    datas["change_add_ban_permission_command"]: change_add_ban_permission,
    datas["change_forget_permission_command"]: change_forget_permission,
    datas["change_lift_ban_permission_command"]: change_lift_ban_permission,
    datas["change_sentence_commom_command"]: change_sentence_common,
    datas["change_find_commom_command"]: change_find_common,
    datas["change_ban_commom_command"]: change_ban_common
}


# 機器人初始化


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    for channel in datas["announce_channels"]:
        await client.get_channel(channel).send(datas["start_word"])
    activity_w = discord.Activity(
        type=discord.ActivityType.watching, name=datas["activity"])
    await client.change_presence(status=discord.Status.online, activity=activity_w)


@client.event
async def on_message(message):

    if message.author == client.user:
        return
    print("{} say : {}".format(message.author.name, message.content))

    sents = message.content.split(datas["split"])
    anss = []
    if sents[0] in funcs.keys():
        await funcs[sents[0]](message, sents)
    elif sents[0] in lib:
        if not datas["sentence_common"]:
            for ans in lib[sents[0]]:
                if ans["伺服器"] == message.guild.name or ans["伺服器"] == "通用":
                    anss.append(ans["回答"])
            if len(anss) != 0:
                await message.channel.send(random.choice(anss))
        else:
            await message.channel.send(random.choice(lib[sents[0]])["回答"])
        return

    for find in findlib:
        if find in sents[0]:
            if datas["find_common"]:
                for ans in findlib[find]:
                    anss.append(ans["回答"])
            else:
                for ans in findlib[find]:
                    if ans["伺服器"] == message.guild.name:
                        anss.append(ans["回答"])
    if len(anss) != 0:
        await message.channel.send(random.choice(anss))

keep_alive.keep_alive()

client.run(datas["bot_token"])
