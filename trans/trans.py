from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import *
from discord import app_commands, SelectOption
import discord
import requests
import openpyxl


bot = commands.Bot(command_prefix="=", intents=discord.Intents.all(), help_command=None)
tree = bot.tree


def check_info(key: str, target: str = 'B'):
    openxl = openpyxl.load_workbook('lang.xlsx')
    wb = openxl.active

    for i in range(2, 20):
        if wb['A' + str(i)].value == key:
            return wb[target + str(i)].value


def setup_choices(input_t: bool):
    openxl = openpyxl.load_workbook('lang.xlsx')
    wb = openxl.active

    return_list = []

    if input_t is True:
        return_list.append(Choice(name="🔎 언어 감지", value="sr"))

    for i in range(2, 20):
        if wb['A' + str(i)].value is not None:
            return_list.append(Choice(name=f"{wb['C' + str(i)].value} {wb['B' + str(i)].value}", value=wb['A' + str(i)].value))

    return return_list


@bot.event
async def on_guild_join(guild):
    await bot.get_channel(int(831444237596753920)).send(f"{str(guild)} | 서버에 참가했습니다.\n현재 서버 : {len(bot.guilds)}")
    return


@bot.event
async def on_guild_remove(guild):
    await bot.get_channel(int(831444237596753920)).send(f"{str(guild)} | 서버에서 나갔습니다.\n현재 서버 : {len(bot.guilds)}")
    return


@bot.event
async def on_ready():
    await tree.sync()
    game = discord.Game("'/번역 문장' 명령어를 사용해보세요.")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print(f"파파고 API를 이용한 번역기 가동")


@tree.context_menu(name="📟 해당 메세지 번역")
async def translate_this_message(interaction: discord.Interaction, message: discord.Message):
    _client_id = "ggMmuA4b69gftAhECbHW"
    _client_secret = "HajFlzmagI"

    _url = "https://openapi.naver.com/v1/papago/detectLangs"
    _headers = {"X-Naver-Client-Id": _client_id,
                "X-Naver-Client-Secret": _client_secret}

    _data = {'query': message.content.encode('utf-8')}

    _res = requests.post(_url, data=_data, headers=_headers)

    client_id = "STiBgFXmrOL7xroLTa3Q"
    client_secret = "otZpQN3EqY"

    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {"X-Naver-Client-Id": client_id,
               "X-Naver-Client-Secret": client_secret}

    data = {'source': _res.json()['langCode'],
            'target': 'ko',
            'text': message.content.encode('utf-8')}

    res = requests.post(url, data=data, headers=headers)
    try:
        embed = discord.Embed(title=f"{bot.user.name} / 번역 결과", description=f"\✅ 번역이 완료되었습니다.", color=0x00FFBF)
        embed.add_field(name=f"{check_info(_res.json()['langCode'], 'C')} {check_info(_res.json()['langCode'])}", value=f"```\n{message.content}```",
                    inline=False)
        embed.add_field(name=f"{check_info('ko', 'C')} {check_info('ko')}", value=f"```\n{res.json()['message']['result']['translatedText']}```",
                    inline=False)
        embed.set_footer(
        text=f"전 문장 : {len(message.content)}자ㅣ후 문장 : {len(res.json()['message']['result']['translatedText'])}자")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except KeyError:
        await interaction.response.send_message("\❗ 해당 메세지의 언어도 **한국어**입니다.", ephemeral=True)


class 번역(app_commands.Group):
    @app_commands.command(name="문장", description="입력된 문장을 번역하는 명령어")
    @app_commands.describe(input_언어="번역할 문장의 언어를 선택하세요.", output_언어="번역될 문장의 언어를 선택해주세요.")
    @app_commands.choices(input_언어=setup_choices(True), output_언어=setup_choices(False))
    async def translate(self, interaction: discord.Interaction, input_언어: Choice[str], output_언어: Choice[str]):
        class words(Modal, title=f"{bot.user.name} / 문장 번역"):
            content = TextInput(
                label=f"{input_언어.name} -> {output_언어.name}",
                min_length=1,
                max_length=1000,
                required=True,
                placeholder="번역할 문장을 입력하세요.",
                style=discord.TextStyle.long
            )

            async def on_submit(self, inter: discord.Interaction):
                def input_():
                    if input_언어.value == "sr":
                        _client_id = "ggMmuA4b69gftAhECbHW"
                        _client_secret = "HajFlzmagI"

                        _url = "https://openapi.naver.com/v1/papago/detectLangs"
                        _headers = {"X-Naver-Client-Id": _client_id,
                                    "X-Naver-Client-Secret": _client_secret}

                        _data = {'query': self.content.value.encode('utf-8')}

                        _res = requests.post(_url, data=_data, headers=_headers)

                        return _res.json()['langCode']

                    else:
                        return input_언어.value

                client_id = "STiBgFXmrOL7xroLTa3Q"
                client_secret = "otZpQN3EqY"

                url = "https://openapi.naver.com/v1/papago/n2mt"
                headers = {"X-Naver-Client-Id": client_id,
                           "X-Naver-Client-Secret": client_secret}

                data = {'source': input_(),
                        'target': output_언어.value,
                        'text': self.content.value.encode('utf-8')}

                res = requests.post(url, data=data, headers=headers)

                try:
                    embed = discord.Embed(title=f"{bot.user.name} / 번역 결과", description=f"\✅ 번역이 완료되었습니다.", color=0x00FFBF)
                    embed.add_field(name=f"{check_info(input_(), 'C')} {check_info(input_())}", value=f"```\n{self.content.value}```", inline=False)
                    embed.add_field(name=f"{output_언어.name}", value=f"```\n{res.json()['message']['result']['translatedText']}```", inline=False)
                    embed.set_footer(text=f"전 문장 : {len(self.content.value)}자ㅣ후 문장 : {len(res.json()['message']['result']['translatedText'])}자")
                    await inter.response.send_message(embed=embed, ephemeral=True)
                
                except Exception as e:
                    await inter.response.send_message(f"\❗ 오류 발생, 다시 시도해주세요.\n```\n- {e}```")

        await interaction.response.send_modal(words())


    @app_commands.describe(url="한국어로 번역할 웹사이트 URL을 입력해주세요.")
    @app_commands.command(name="웹사이트", description="웹사이트 자체를 번역하는 명령어")
    async def site(self, interaction: discord.Interaction, url: str):
        if "https://" not in url:
            await interaction.response.send_message("\❗ 올바른 웹사이트 URL이 아닙니다.", ephemeral=True)

        embed = discord.Embed(description=f"[여기](https://papago.naver.net/website?locale=ko&source=auto&target=ko&url={url})를 클릭하여 이동하세요.", color=0x00FFBF)
        await interaction.response.send_message(embed=embed, ephemeral=True)


tree.add_command(번역())


bot.run("your token")
