import os
import json
from collections import OrderedDict


class FileImg:
    def __init__(self, path):
        self.path = path

    def get_profil_img(self, user_id):
        if os.path.exists(f"{self.path}/{user_id}.png"):
            return open(f"{self.path}/{user_id}.png", "rb").read()
        else:
            return None

    def get_game_img(self, game_name):
        if os.path.exists(f"{self.path}/{game_name}.png"):
            return open(f"{self.path}/{game_name}.png", "rb").read()
        else:
            return None

    def save_profil_img(self, user_id, content):
        open(f"{self.path}/{user_id}.png", "wb").write(content)


class FileConfig:
    def __init__(self, path=""):
        self.path = path

    @property
    def file(self) -> dict:
        with open(self.path, "r") as file:
            return json.load(file)

    def write_file(self, content):
        with open(self.path, 'w') as file:
            json.dump(content, file, indent=2)

    def get_streamers(self):
        streamers = [streamer for streamer in self.file.get("streamer")]
        print("ok", streamers)
        order = self.file.get("general").get("streamer_order")
        new_order = order+list(set(streamers)-set(order))
        if order != new_order:
            self.edit_config(["general", "streamer_order"], new_order)
        return new_order

    def get_games(self):
        games = [self.file.get("games")[game].get("name") for game in self.file.get("games")]
        return games

    def get_streamer_game(self, streamer_id):
        games = [game for game in self.file.get("streamer").get(streamer_id).get("games")]
        return games

    def add_streamer(self, user_id, name, **kwargs):
        file = self.file
        if file.get("streamer").get(user_id):
            return None
        content = {"name": name,
                   "id": user_id,
                   "sound": 0 if not kwargs.get("sound") else kwargs.get("sound"),
                   "design": 0,
                   "notif": True,
                   "notif_priority": 0,
                   "sound_priority": 0,
                   "design_priority": 0,
                   "games": {}
                   }
        content.update(kwargs)
        file["streamer"].update(
            {user_id: content})
        order: list = self.file.get("general").get("streamer_order")
        order.append(user_id)
        file["general"]["streamer_order"] = order
        self.write_file(file)

    def add_game(self, name, **kwargs):
        file = self.file
        if file.get("games").get(name):
            return None
        content = {"name": name,
                   "sound": 0 if not kwargs.get("sound") else kwargs.get("sound"),
                   "design": 0,
                   "notif": True,
                   "notif_priority": 0,
                   "sound_priority": 0,
                   "design_priority": 0,
                   }
        content.update(kwargs)
        file["games"].update(
            {name: content})
        self.write_file(file)

    def add_streamer_game(self, streamer_id, name, **kwargs):
        file = self.file
        content = {
          "sound": 0,
          "design": 0,
          "notif": True,
          "sound_active": False,
          "design_active": False,
          "notif_active": False,
        }
        content.update(kwargs)
        file["streamer"][streamer_id]["games"][name] = content
        self.write_file(file)

    def edit_config(self, path, content):
        file = [self.file]
        for key in path:
            file.append(file[-1].get(key))
            if not file:
                raise "Key Error"
        file[-1] = content
        for i in range(len(file)-1, 1, -1):
            file[i-1][path[i-1]] = file[i]
        self.write_file(file[0])

    def get_config(self, path):
        file = self.file
        for i in path:
            file = file.get(i)
            if file is None:
                return None
        return file

    def delete_config(self, path):
        file = [self.file]
        for key in path[:-1]:
            file.append(file[-1].get(key))
            if not file:
                raise "Key Error"
        file[-1].pop(path[-1])
        for i in range(len(file) - 1, 1, -1):
            file[i - 1][path[i - 1]] = file[i]
        self.write_file(file[0])

    def move(self, streamer_id, sens=1):
        order: list = self.file.get("general").get("streamer_order")
        file = self.file
        if streamer_id not in order:
            return
        index = order.index(streamer_id)
        if sens == 1 and index == len(order) - 1:
            index = 0
        elif sens == -1 and index == 0:
            index = - 1
        else:
            index = index + sens

        order.remove(streamer_id)
        order.insert(index, streamer_id)
        file["general"]["streamer_order"] = order
        self.write_file(file)

