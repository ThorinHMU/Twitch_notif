import threading
import webbrowser
import requests
from win11toast import toast
from queue import Empty
import os
import asyncio
import multiprocessing
from werkzeug import Request, Response, run_simple
from config import FileConfig
import time
import datetime
import secrets


class NotifProgram:
    def __init__(self, notif_signal, config_file):
        self.notif_signal = notif_signal
        self.config_file: FileConfig = config_file
        self.sleep: threading.Event = threading.Event()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.path = os.path.abspath(".") + "\\"
        self.table_live = {}
        self.running = True
        self.table_live_is_set = False
        self.in_live = {}
        self.old_in_live = {}

    def loop_notif(self):
        self.access_token, self.refresh_token = self.get_access_token()
        if not self.access_token:
            self.notif_signal.emit({"type": "cmd", "content": "fail_starting"})
            return

        self.user_id = self.get_user_id_from_token()
        while self.running:
            params = {"user_id": self.user_id}
            response = self.twitch_req("https://api.twitch.tv/helix/streams/followed", params)

            if response.status_code == 401:
                self.access_token = self.refresh_access_token()
                response = self.twitch_req("https://api.twitch.tv/helix/streams/followed", params)

            if response.status_code != 200:
                raise f"ERREUR {response.status_code}: {response.content}"
            data: list[dict] = response.json().get("data")
            self.in_live = {}

            # Rajoute les live qui commence
            for live in data:
                self.in_live.update({f"{live.get("user_id")}": (live.get("game_name"), live.get("title"))})
                if self.table_live.get(live.get('user_id')):
                    continue
                if self.table_live_is_set:
                    self.notif(live.get("user_id"), live.get("user_name"), live.get("game_id"), live.get("game_name"),
                               live.get("title"))
                self.table_live.update({live.get('user_id'): True})
            if not self.table_live_is_set:
                self.table_live_is_set = True

                self.notif_signal.emit({"type": "cmd", "content": "is_starting"})

            # Enleve les streame terminé
            for streamer in list(self.table_live.keys()):
                if streamer not in [live.get('user_id') for live in data]:
                    self.table_live.pop(streamer)
            if self.in_live != self.old_in_live:
                self.notif_signal.emit({"type": "inlive", "content": self.in_live})
            self.old_in_live = self.in_live.copy()

            self.sleep.wait(10)

    def get_access_token(self):
        myid = secrets.token_urlsafe()
        webbrowser.open(f"https://connect.thorin-56.fr/connect_twitch?state={myid}")
        access_token, refresh_token = self.get_code(myid)
        if not access_token:
            return None, None
        else:
            return access_token, refresh_token

    @staticmethod
    def get_code(myid):
        time_1 = datetime.datetime.now().timestamp().__int__()
        access_token = None
        refresh_token = None

        while not access_token:
            response = requests.get("https://connect.thorin-56.fr/get_code", params={"id": myid}).json()
            access_token = response.get("access_token")
            refresh_token = response.get("refresh_token")
            time.sleep(1)  # Vérifie toutes les secondes
            time_2 = datetime.datetime.now().timestamp().__int__()
            if time_2 - time_1 > 30 and not access_token:
                return None, None
        return access_token, refresh_token

    def save_icon(self, api_path, params, data_path, file_name):
        response = self.twitch_req(f"https://api.twitch.tv/helix/{api_path}", params=params)
        data = response.json().get("data")
        icon_url = data[0].get(data_path).format(width=0, height=0)
        icon_byte = requests.get(icon_url).content
        open(file_name, "wb").write(icon_byte)

    def get_user_id_from_token(self):
        url = "https://id.twitch.tv/oauth2/validate"
        headers = {
            "Authorization": f"OAuth {self.access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("user_id")  # ID de l'utilisateur
        except requests.RequestException as e:
            print(f"Erreur réseau : {e}")
        return None

    def notif(self, user_id, user_name, game_id, game_name, title):
        user_notif = self.config_file.get_config(["streamer", user_id, "notif"])
        user_notif_priority = self.config_file.get_config(["streamer", user_id, "notif_priority"])
        game_notif = self.config_file.get_config(["games", game_id, "notif"])
        game_notif_priority = self.config_file.get_config(["games", game_id, "notif_priority"]) or 0
        user_game_notif_active = self.config_file.get_config(["streamer", user_id, "games", game_id, "notif_active"])
        user_game_notif = self.config_file.get_config(["streamer", user_id, "games", game_id, "notif"])
        priotity = self.config_file.get_config(["general", "notif_priority"])

        style_priority = self.config_file.get_config(["general", "design_priority"])
        user_style = self.config_file.get_config(["streamer", user_id, "design"])
        game_style = self.config_file.get_config(["games", game_id, "design"])
        user_game_style = self.config_file.get_config(["streamer", user_id, "games", game_id, "design"])

        user_style_priority = self.config_file.get_config(["streamer", user_id, "design_priority"])
        game_style_priority = self.config_file.get_config(["games", game_id, "design_priority"]) or 0
        user_game_style_active = self.config_file.get_config(["streamer", user_id, "games", game_id, "design_active"])

        if user_style_priority != game_style_priority:
            style = user_style if user_style_priority >= game_style_priority else game_style
        else:
            style = user_style if style_priority == "streamer" else game_style
        if user_game_style_active:
            style = user_game_style

        notif_enable = False

        if user_notif == game_notif:
            notif_enable = user_notif
        elif game_notif_priority != user_notif_priority:
            notif_enable = user_notif if user_notif_priority > game_notif_priority else game_notif
        elif game_notif_priority == user_notif_priority:
            notif_enable = user_notif if priotity == "streamer" else game_notif if priotity == "game" else priotity
        if user_game_notif_active:
            notif_enable = user_game_notif
        if not notif_enable:
            return

        self.save_icon("users", {"id": user_id},
                       "profile_image_url", "tempori_user_icon.png")
        self.save_icon("games", {"id": game_id},
                       "box_art_url", "tempori_game_icon.png")
        self.save_icon("streams", {"id": user_id},
                       "thumbnail_url", "tempori_stream_icon.png")

        user_icon = {'src': self.path + "tempori_user_icon.png",
                     'placement': 'appLogoOverride'}
        game_icon = {'src': self.path + "tempori_game_icon.png"}

        if style:
            icons_table = {"Profil du streamer": self.path + "tempori_user_icon.png",
                           "Image du jeu": self.path + "tempori_game_icon.png",
                           "Preview du stream": self.path + "tempori_stream_icon.png"}

            style = self.config_file.get_config(["general", "styles"]).get(style)
            text: str = style["text"].format(title=title, streamer=user_name, game=game_name)
            icon = icons_table.get(style["little_icon"])

            user_icon = {'src': icon,
                         'placement': 'appLogoOverride'} if icon else None
            img = icons_table.get(style["img"])
            game_icon = {'src': img} if img else None

            toast(text,
                  image=user_icon, icon=game_icon, on_click=f'https://www.twitch.tv/{user_name}',
                  audio={"silent": "true"})
        else:
            toast(f"{user_name} est en live sur {game_name}{title}",
                  image=user_icon, icon=game_icon, on_click=f'https://www.twitch.tv/{user_name}',
                  audio={"silent": "true"})

    def refresh_access_token(self) -> str | None:
        params = {"refresh_token": self.refresh_token}
        response = requests.get("https://connect.thorin-56.fr/refresh_token", params=params)
        access_token = response.json().get("access_token")
        return access_token

    def get_streamers_followed(self):
        url = "https://api.twitch.tv/helix/channels/followed"
        params = {
            "user_id": self.user_id,
            "first": 100
        }

        try:
            response = self.twitch_req(url, params=params)
            if response.status_code == 200:
                data = response.json()["data"]
                followers = [(streamer["broadcaster_id"], streamer["broadcaster_name"]) for streamer in data]
                return followers
            else:
                print(f"Erreur lors de la validation du token : {response.status_code}")
                print(response.json())
        except requests.RequestException as e:
            print(f"Erreur réseau : {e}")
        return None

    def get_profil_img(self, user_id, width=0, height=0):
        params = {"id": user_id}
        print(params)
        response = self.twitch_req("https://api.twitch.tv/helix/users", params=params)
        data = response.json().get("data")
        icon_url = data[0].get("profile_image_url").format(width=width, height=height)
        response = requests.get(icon_url)
        return response.content

    def get_game_img(self, game_id=None, width=0, height=0, url=None):
        if game_id:
            params = {"id": game_id}
            response = self.twitch_req("https://api.twitch.tv/helix/games", params=params)
            data = response.json().get("data")
            icon_url = data[0].get("box_art_url").format(width=width, height=height)
        else:
            icon_url = url
        response = requests.get(icon_url)
        return response.content

    def search_game(self, text):
        params = {"query": text, "first": 100}
        response = self.twitch_req("https://api.twitch.tv/helix/search/categories", params=params)
        data = response.json().get("data")
        return data

    def twitch_req(self, url, params):
        headers = {"url": url, "token": self.access_token}
        params = params
        return requests.get("https://connect.thorin-56.fr/get_twitch", params=params, headers=headers)
