import asyncio
import os
import webbrowser
from notif import NotifProgram
import requests
import sys
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QMainWindow, QFrame, QStackedWidget,
                             QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QScrollArea, QLineEdit, QSpacerItem)
from PyQt5.QtGui import QIcon, QCloseEvent, QImage, QKeyEvent, QCursor
from PyQt5.QtCore import QRect, QEvent, pyqtSignal, pyqtSlot, QByteArray, QThread
import threading
from ui import *
import time
from config import FileConfig, FileImg
from collections import OrderedDict


class ConnectPage(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.top_bar_widget = QWidget()
        self.top_bar_layout = QHBoxLayout()

        self.title = QLabel(self)
        self.delimit = QFrame(self)

        self.body_layout = QVBoxLayout()
        self.body_widget = QWidget()
        self.connect_button = CustomButton(self, "assets/ui/connected_button.png", 100)
        self.be_connected = False
        self.init_ui()

    def init_ui(self):
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(0)

        self.title.setText("Twitch Notif")
        self.title.setStyleSheet("color: rgb(144, 40, 255); font-size: 75px")

        self.delimit.setStyleSheet("background: rgb(127, 127, 127)")
        self.delimit.setFixedHeight(3)

        self.top_bar_layout.addStretch(20)
        self.top_bar_layout.addWidget(self.title, 60, Qt.AlignCenter)
        self.top_bar_layout.addStretch(20)

        self.top_bar_widget.setLayout(self.top_bar_layout)

        self.body_widget.setLayout(self.body_layout)
        self.body_layout.addWidget(self.delimit, 1, alignment=Qt.AlignTop)
        self.body_layout.addWidget(self.connect_button, 9, alignment=Qt.AlignCenter)
        self.connect_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.connect_button.clicked.connect(self.connection)

        self.main_layout.addWidget(self.top_bar_widget, 1, alignment=Qt.AlignTop)
        self.main_layout.addWidget(self.body_widget, 9)
        self.setLayout(self.main_layout)

    def block_connect_button(self):
        self.be_connected = True
        self.connect_button.setCursor(Qt.WaitCursor)

    def unblock_connect_button(self):
        self.be_connected = False
        self.connect_button.setCursor(Qt.PointingHandCursor)

    def connection(self, _):
        if not self.be_connected:
            self.clicked.emit()
            self.block_connect_button()


class MainConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        # Pages

        self.my_parent: MainWindows | None = my_parent

        self.general_label = QLabel("Générale")
        self.general_button = CircleButton()
        self.generalPage = GeneralConfigPage(self)

        self.streamer_label = QLabel("Streamer")
        self.streamer_button = CircleButton()
        self.streamerPage = StreamerConfigPage(self)

        self.game_label = QLabel("Jeux")
        self.game_button = CircleButton()
        self.gamePage = GameConfigPage(self)

        self.addGamePage = AddGamePage(self.gamePage, self, self.my_parent.config_file.get_games())

        self.main_layout = QVBoxLayout()
        self.top_bar_widget = QWidget()
        self.top_bar_layout = QHBoxLayout()

        self.top_left_layout = QVBoxLayout()

        self.label_buttons_layout = QHBoxLayout()

        self.table_page = {"general": self.generalPage, "game": self.gamePage, "streamer": self.streamerPage,
                           "add_game": self.addGamePage}

        self.buttons_layout = QHBoxLayout()

        self.choice = MutlipleChoice()

        self.title = QLabel(self)
        self.delimit = QFrame(self)

        self.body_widget = QStackedWidget()
        self.init_ui()

    def init_ui(self):
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(0)

        self.game_label.setAlignment(Qt.AlignCenter)
        self.general_label.setStyleSheet("color: white; font-size: 20px")
        self.general_label.setAlignment(Qt.AlignCenter)
        self.streamer_label.setStyleSheet("color: white; font-size: 20px")
        self.streamer_label.setAlignment(Qt.AlignCenter)
        self.game_label.setStyleSheet("color: white; font-size: 20px")

        self.buttons_layout.addWidget(self.general_button, 1, Qt.AlignCenter)
        self.buttons_layout.addWidget(self.streamer_button, 1, Qt.AlignCenter)
        self.buttons_layout.addWidget(self.game_button, 1, Qt.AlignCenter)

        self.label_buttons_layout.addWidget(self.general_label, 3, Qt.AlignCenter)
        self.label_buttons_layout.addWidget(self.streamer_label, 3, Qt.AlignCenter)
        self.label_buttons_layout.addWidget(self.game_label, 3, Qt.AlignCenter)

        self.choice.add(self.general_button, "general")
        self.choice.add(self.streamer_button, "streamer")
        self.choice.add(self.game_button, "game")
        self.choice.choising.connect(self.change_config_page)

        self.top_left_layout.addLayout(self.label_buttons_layout, 40)
        self.top_left_layout.addLayout(self.buttons_layout, 80)

        self.title.setText("Twitch Notif")
        self.title.setStyleSheet("color: rgb(144, 40, 255); font-size: 75px")

        self.delimit.setStyleSheet("background: rgb(127, 127, 127)")
        self.delimit.setFixedHeight(3)

        self.top_bar_layout.addLayout(self.top_left_layout, 20)
        self.top_bar_layout.addWidget(self.title, 60, Qt.AlignCenter)
        self.top_bar_layout.addStretch(20)

        self.top_bar_widget.setLayout(self.top_bar_layout)

        self.main_layout.addWidget(self.top_bar_widget, 1, alignment=Qt.AlignTop)
        self.main_layout.addWidget(self.delimit, 1)
        self.main_layout.addWidget(self.body_widget, 9)

        self.body_widget.addWidget(self.generalPage)
        self.body_widget.setCurrentWidget(self.generalPage)

        self.setLayout(self.main_layout)

        self.addGamePage.addgame.connect(self.gamePage.add_new_game)

    def change_config_page(self, key=None, page=None):
        if key:
            page = self.table_page.get(key)
        if not page:
            return
        self.body_widget.removeWidget(self.body_widget.currentWidget())
        self.body_widget.addWidget(page)
        self.body_widget.setCurrentWidget(page)


class GeneralConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        self.my_parent: MainConfigPage | None = my_parent
        self.layout = QVBoxLayout()
        self.frame = QFrame()

        self.frame.setStyleSheet('border: 5px solid white')
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        self.vbox = QVBoxLayout()
        self.frame.setLayout(self.vbox)

        self.title_sound = QLabel("Sons enregistrés:")
        self.title_sound.setStyleSheet("color: white; font-size: 50px; border: None")

        self.frame_sound = QFrame()
        self.frame_sound.setStyleSheet("border: 2px solid grey;")
        self.frame_sound.setFixedHeight(300)

        self.layout_main_sound = QVBoxLayout()
        self.layout_content_sound = QHBoxLayout()
        self.scroll_area_content_sound = QScrollArea()
        self.scroll_area_content_sound.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area_content_sound.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area_content_sound.setWidgetResizable(True)

        self.layout_content_sound.addWidget(self.scroll_area_content_sound)
        self.grid = HGridLayout()
        self.widget = QWidget()
        self.scroll_area_content_sound.setWidget(self.widget)
        self.widget.setLayout(self.grid)

        self.layout_main_sound.setContentsMargins(0, 0, 0, 0)

        self.frame_sound.setLayout(self.layout_main_sound)
        self.layout_main_sound.addLayout(self.layout_content_sound, 1)

        self.sounds = self.my_parent.my_parent.config_file.get_config(["general", "sounds"])
        if not self.sounds:
            label = QLabel("Aucun son enregistré")
            label.setStyleSheet("border: None; color: grey; font-size: 30px")
            self.grid.add_element(label)
        else:
            for name, path in self.sounds:
                frame = QFrame()
                frame.setFixedSize(300, 56)
                frame.setStyleSheet("border: 2px solid grey;")
                label_name = QLabel(name, frame)
                label_name.setStyleSheet("color: white; font-size: 20px; border: None;")
                label_path = QLabel(path, frame)
                label_path.setStyleSheet("color: white; font-size: 16px; border: None;")
                label_name.setGeometry(3, 3, 294, 25)
                label_path.setGeometry(3, 25, 294, 25)
                label_name.setAlignment(Qt.AlignCenter)
                label_path.setAlignment(Qt.AlignCenter)

                delete_button = CustomButton(frame, "assets/ui/delete.png", 20)
                delete_button.move(250, 5)

                edit_button = CustomButton(frame, "assets/ui/edit_button.png", 20)
                edit_button.move(275, 5)

                self.grid.add_element(frame)

        self.add_sound_frame = QFrame()
        self.add_sound_button = CustomButton(self.add_sound_frame, path="assets/ui/add_button.png")
        self.add_sound_label = QLabel("Ajouter un son", self.add_sound_frame)

        self.add_sound_frame.setFixedHeight(70)
        self.add_sound_frame.setStyleSheet("border: None")

        self.add_sound_button.move(10, 10)

        self.add_sound_label.move(70, 20)
        self.add_sound_label.setStyleSheet("color: white; font-size: 25px; border: None")

        self.layout_main_sound.addWidget(self.add_sound_frame, alignment=Qt.AlignBottom)

        self.vbox.addWidget(self.title_sound, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.vbox.addWidget(self.frame_sound, 1, alignment=Qt.AlignTop)


class StreamerConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        self.lock_scroll = False
        self.my_parent: MainConfigPage | None = my_parent
        self.config_file = self.my_parent.my_parent.config_file
        self.my_parent.streamer_button.lock()
        self.file = []
        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.top_frame = QFrame()
        self.layout.addWidget(self.top_frame)
        self.layout.addWidget(self.scroll_area, 4)
        self.setLayout(self.layout)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.wheelEvent = self.scroll_event
        self.table: dict[str, StreamerBox] = {}
        self.thread = None
        self.is_load = None

    def scroll_event(self, event):
        if self.lock_scroll:
            return
        else:
            super(QScrollArea, self.scroll_area).wheelEvent(event)

    def load(self):
        self.thread = LoadImagesThread(self.config_file, self.my_parent.my_parent.notif_programe)
        self.thread.images_loaded.connect(self.update_ui)
        self.thread.start()

    def move_element(self, widget, sens):
        index = self.vbox.indexOf(widget)
        if index == len(self.table) - 1 and sens == 1:
            index = 0
        elif index == 0 and sens == -1:
            index = -1
        else:
            index = index + sens
        self.vbox.removeWidget(widget)
        self.vbox.insertWidget(index, widget)
        if index == 0:
            self.scroll_area.verticalScrollBar().setValue(0)
        elif index == -1:
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        else:
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value()+207*sens)

    def update_ui(self, images):
        self.top_frame.setFixedHeight(50)
        test_button = CustomButton(self.top_frame, "assets/ui/add_button.png")
        test_button.move(200, 0)
        test_button.clicked.connect(lambda _: self.my_parent.my_parent.notif_programe.table_live.clear())
        all_notif_switch_button = SwitchButton(self.top_frame, 40)
        all_notif_switch_button.move(300, 0)
        streamer_id = None
        for streamer_id, img_data in images.items():
            try:
                frame = StreamerBox(img_data, streamer_id, self.config_file, self)
                frame.setFixedHeight(200)
                self.table.update({streamer_id: frame})
                self.vbox.addWidget(frame, 1)
            except Exception as erreur:
                print(erreur)

        all_notif_switch_button.clicked.connect(self.toogle_all)
        self.my_parent.streamer_button.unlock()
        if self.table and self.file:
            self.table[streamer_id].finish.connect(lambda: self.file.pop(0)())

        self.is_load = True

    def toogle_all(self, state):
        for frame in list(self.table.values()):
            frame.notif_switch_button.toogle_state(state)

    def state_live(self, data: dict):
        for streamer_id, frame in self.table.items():
            if streamer_id in data.keys():
                frame.change_color("red")
                frame.label.enterEvent = \
                    lambda _, title=data[streamer_id][1], game=data[streamer_id][0], f_frame=frame: (
                        f_frame.aff_info_bulle(title, game))
                frame.label.leaveEvent = lambda _, f_frame=frame: f_frame.hide_info_bule()
            else:
                frame.change_color("white")
                frame.label.enterEvent = None
                frame.label.leaveEvent = None


class StreamerBox(QFrame):
    finish = pyqtSignal()

    def __init__(self, img_data, streamer_id, config_file, my_parent: StreamerConfigPage | None = None):
        super().__init__()
        self.games_imgs = []
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.my_parent = my_parent
        self.config_file: FileConfig = config_file

        self.setStyleSheet("border: 3px solid white; ")

        self.streamer_id = streamer_id

        self.first_frame = QFrame()
        self.first_frame.setObjectName("noburder")
        self.first_frame.setStyleSheet("#noburder { border-top: none; border-bottom: none; border-left: none; }")
        self.first_frame.setFixedWidth(575)

        self.label = QLabel(self.first_frame)
        self.label.setObjectName("noburder")

        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pixmap = QPixmap()
        pixmap.loadFromData(img_data, "")
        pixmap = pixmap.scaled(194, 194, Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.setCursor(Qt.PointingHandCursor)

        nom = self.config_file.file.get("streamer").get(streamer_id).get("name")

        def open_page(_):
            webbrowser.open(f"www.twitch.tv/{nom}")

        self.label.mousePressEvent = open_page

        self.nom = QLabel(self.first_frame)
        self.nom.setText(nom)
        self.nom.move(225, 15)
        self.nom.setStyleSheet("color: white; font-size: 30px; border: none; ")
        self.nom.adjustSize()

        self.notif_label = QLabel("Notifs", self.first_frame)
        self.notif_label.move(225, 55)
        self.notif_label.setStyleSheet("color: white; font-size: 20px; border: none; ")
        self.notif_label.adjustSize()

        self.notif_switch_button = SwitchButton(self.first_frame, 30)
        self.notif_switch_button.move(300, 55)
        self.notif_switch_button.clicked.connect(lambda state:
                                                 self.config_file.edit_config(["streamer", streamer_id, "notif"],
                                                                              state))
        self.notif_switch_button.toogle_state(self.config_file.get_config(["streamer", streamer_id, "notif"]))

        self.notif_priority = NbrSelecteur(self.first_frame, 30)
        self.notif_priority.move(515, 55)
        self.notif_priority.set_value(self.config_file.get_config(["streamer", streamer_id, "notif_priority"]))
        self.notif_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["streamer", streamer_id, "notif_priority"],
                                                                         self.notif_priority.value))

        self.sound_label = QLabel("Sons", self.first_frame)
        self.sound_label.move(225, 95)
        self.sound_label.setStyleSheet("color: white; font-size: 20px; border: none; ")
        self.sound_label.adjustSize()

        self.sound_select_label = QLabel("Pas de son", self.first_frame)
        self.sound_select_label.move(280, 95)
        self.sound_select_label.setStyleSheet("color: grey; font-size: 20px; border: none; ")
        self.sound_select_label.adjustSize()

        self.sound_select_button = CustomButton(self.first_frame, "assets/ui/choice_sound.png", 30)
        self.sound_select_button.move(400, 95)

        self.sound_priority = NbrSelecteur(self.first_frame, 30)
        self.sound_priority.move(515, 95)
        self.sound_priority.set_value(self.config_file.get_config(["streamer", streamer_id, "sound_priority"]))
        self.sound_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["streamer", streamer_id, "sound_priority"],
                                                                         self.sound_priority.value))

        self.design_label = QLabel("Style", self.first_frame)
        self.design_label.move(225, 135)
        self.design_label.setStyleSheet("color: white; font-size: 20px; border: none; ")
        self.design_label.adjustSize()

        self.design_select_label = QLabel("Pas de style", self.first_frame)
        self.design_select_label.move(280, 135)
        self.design_select_label.setStyleSheet("color: grey; font-size: 20px; border: none; ")
        self.design_select_label.adjustSize()

        self.design_select_button = CustomButton(self.first_frame, "assets/ui/choice_style.png", 30)
        self.design_select_button.move(400, 135)

        self.design_priority = NbrSelecteur(self.first_frame, 30)
        self.design_priority.move(515, 135)
        self.design_priority.set_value(self.config_file.get_config(["streamer", streamer_id, "design_priority"]))
        self.design_priority.clicked.connect(lambda:
                                             self.config_file.edit_config(["streamer", streamer_id, "design_priority"],
                                                                          self.design_priority.value))

        self.frame_add = QFrame()
        self.frame_add.setFixedWidth(75)
        self.frame_add.setObjectName("noburder")
        self.frame_add.setStyleSheet("#noburder { border-top: none; border-bottom: none; border-left: none; }")

        games = self.config_file.get_config(["streamer", streamer_id, "games"])
        if games:
            games = list(games.keys())
        self.game_page = AddGamePage(self.my_parent.my_parent.streamerPage, self.my_parent.my_parent, games)
        self.game_page.addgame.connect(self.add_new_game)

        self.button_add_game = CustomButton(self.frame_add, "assets/ui/add_button.png", 40)
        self.button_add_game.move(16, 80)
        self.button_add_game.clicked.connect(self.aff_add_game)
        self.up = CustomButton(self.frame_add, "assets/ui/arrow_up.png", 30)
        self.up.move(4, 10)
        self.up.clicked.connect(lambda: self.move_element(-1))
        self.down = CustomButton(self.frame_add, "assets/ui/arrow_down.png", 30)
        self.down.move(4, 150)
        self.down.clicked.connect(lambda: self.move_element(1))

        self.scroll_area = QScrollArea()
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; ")
        self.vbox = QHBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.widget = QWidget()
        self.widget.setStyleSheet("border: none; ")
        self.scroll_area.setWidget(self.widget)
        self.widget.setLayout(self.vbox)

        self.scroll_area.wheelEvent = self.scroll_wheel_event
        self.scroll_area.enterEvent = self.lock_parent
        self.scroll_area.leaveEvent = self.unlock_parent

        self.scroll_area.move(650, 0)

        self.info_bull = QLabel(self)
        self.info_bull.setStyleSheet("border: none; background: red; font-size: 20px; ")
        self.info_bull.hide()
        self.info_bull.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.first_frame, alignment=Qt.AlignLeft)
        self.main_layout.addWidget(self.frame_add, alignment=Qt.AlignLeft)
        self.main_layout.addWidget(self.scroll_area)
        self.info_bull.raise_()

        self.thread = None
        self.launch_get_img_game()

    def move_element(self, sens):
        self.config_file.move(self.streamer_id, sens)
        self.my_parent.move_element(self, sens)

    def lock_parent(self, _):
        if len(self.games_imgs) > 2:
            self.my_parent.lock_scroll = True

    def unlock_parent(self, _):
        if self.my_parent.lock_scroll:
            self.my_parent.lock_scroll = False

    def scroll_wheel_event(self, event):
        if event.angleDelta().y() != 0:  # Molette en Y (haut/bas)
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() -
                                                            event.angleDelta().y())

    def change_color(self, color):
        self.setStyleSheet(self.styleSheet() + f"border-color: {color}; ")
        for frame in self.games_imgs:
            frame.setStyleSheet(frame.styleSheet() + f"border-color: {color}; ")

    def launch_get_img_game(self):
        self.thread = LoadImagesGameStreamerThread(self.config_file, self.my_parent.my_parent.my_parent.notif_programe,
                                                   self.streamer_id)
        self.thread.images_loaded.connect(self.set_img_game)
        self.thread.start()

    def set_img_game(self, images):
        for game, img_data in images.items():
            self.add_img_game(game, img_data)
        self.vbox.addWidget(QLabel(""), 1)
        self.finish.emit()

    def remove_game(self, widget):
        self.config_file.delete_config(["streamer", widget.streamer_id, "games", widget.game_name])
        self.vbox.removeWidget(widget)
        widget.setParent(None)
        self.games_imgs.remove(widget)
        self.game_page.game_filter.remove(widget.game_name)

    def add_img_game(self, game, img_data):
        frame = StreamerGameBox(img_data, game, self.config_file, self.streamer_id)
        frame.delete_button.clicked.connect(lambda _, fframe=frame: self.remove_game(fframe))
        frame.setStyleSheet("border-right: 3px solid white; ")
        frame.setFixedHeight(194)
        self.games_imgs.append(frame)
        self.vbox.insertWidget(len(self.games_imgs) - 1, frame, alignment=Qt.AlignLeft)

    def add_new_game(self, data):
        game, img_data = data
        self.config_file.add_streamer_game(self.streamer_id, game)
        self.add_img_game(game, img_data)

    def aff_add_game(self):
        self.my_parent.my_parent.general_button.lock()
        self.my_parent.my_parent.game_button.lock()
        self.my_parent.my_parent.streamer_button.lock()
        self.my_parent.my_parent.change_config_page(page=self.game_page)

    def aff_info_bulle(self, text, game):
        self.info_bull.show()
        self.info_bull.setText(f"{text} - {game}")
        self.info_bull.adjustSize()

    def hide_info_bule(self):
        self.info_bull.hide()
        self.info_bull.setText("")
        self.info_bull.adjustSize()


class LoadImagesThread(QThread):
    images_loaded = pyqtSignal(dict)

    def __init__(self, config_file, notif_programe):
        super().__init__()
        self.config_file = config_file
        self.profil_img_file = FileImg("assets/profil_img")
        self.notif_programe = notif_programe

    def run(self):
        images = {}

        streamers = self.config_file.get_streamers()
        for streamer_id in streamers:
            img_data = self.profil_img_file.get_profil_img(streamer_id)
            if not img_data:
                img_data = self.notif_programe.get_profil_img(streamer_id)
                self.profil_img_file.save_profil_img(streamer_id, img_data)

            images[streamer_id] = img_data

        self.images_loaded.emit(images)


class LoadImagesGameStreamerThread(QThread):
    images_loaded = pyqtSignal(dict)

    def __init__(self, config_file, notif_programe, streamer_id):
        super().__init__()
        self.config_file = config_file
        self.profil_img_file = FileImg("assets/game_img")
        self.notif_programe = notif_programe
        self.streamer_id = streamer_id

    def run(self):
        images = {}

        games = self.config_file.get_streamer_game(self.streamer_id)
        for game_name in games:
            img_data = self.profil_img_file.get_game_img(game_name)
            if not img_data:
                img_data = self.notif_programe.get_game_img(game_name)
                self.profil_img_file.save_profil_img(game_name, img_data)

            images[game_name] = img_data

        self.images_loaded.emit(images)


class GridLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.elements: list[QWidget] = []
        self.layouts: list[QHBoxLayout] = []
        self._space: list[QLabel] = []

    def add_element(self, widget):
        index = len(self.elements) % 3
        if index == 0:
            layout = QHBoxLayout()
            layout.addWidget(widget, alignment=Qt.AlignCenter)
            label = QLabel()
            label2 = QLabel()
            layout.addWidget(label, alignment=Qt.AlignCenter)
            layout.addWidget(label2, alignment=Qt.AlignCenter)
            self.addLayout(layout)
            self.layouts.append(layout)
            self._space.append(label)
            self._space.append(label2)
        elif index == 1:
            layout: QHBoxLayout = self.layouts[-1]
            label2 = self._space.pop(0)
            layout.removeWidget(label2)
            layout.insertWidget(1, widget, alignment=Qt.AlignCenter)
        elif index == 2:
            layout: QHBoxLayout = self.layouts[-1]
            label1 = self._space.pop(0)
            layout.removeWidget(label1)
            layout.addWidget(widget, alignment=Qt.AlignCenter)
        self.elements.append(widget)

    def remove_element(self, widget):
        try:
            index = self.elements.index(widget)
            if index is None:
                return
            self.elements.remove(widget)

            for i in range(index // 3 + 1, len(self.layouts)):
                element = self.elements[i * 3 - 1]
                self.layouts[i].removeWidget(element)
                self.layouts[i - 1].addWidget(element, alignment=Qt.AlignCenter)
            if len(self.elements) % 3:
                label = QLabel()
                self.layouts[-1].addWidget(label)
                self._space.append(label)
            else:
                label = self._space.pop(-1)
                label2 = self._space.pop(-1)
                self.layouts[-1].removeWidget(label)
                self.layouts[-1].removeWidget(label2)
                self.removeItem(self.layouts[-1])
                self.layouts.pop(-1)
        except Exception as errror:
            print(errror)


class HGridLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.elements: list[QWidget] = []
        self.layouts: list[QVBoxLayout] = []
        self._space: list[QLabel] = []

    def add_element(self, widget):
        index = len(self.elements) % 2
        if index == 0:
            layout = QVBoxLayout()
            layout.addWidget(widget, alignment=Qt.AlignCenter)
            label = QLabel()
            label.setStyleSheet("border: None;")
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            layout.addWidget(label, alignment=Qt.AlignCenter)
            self.addLayout(layout)
            self.layouts.append(layout)
            self._space.append(label)
        else:
            label = self._space.pop(0)
            layout = self.layouts[-1]
            layout.removeWidget(label)
            layout.addWidget(widget, alignment=Qt.AlignCenter)

        self.elements.append(widget)

    def remove_element(self, widget):
        index = self.elements.index(widget)
        if not index:
            return
        self.elements.pop(index)
        widget.setParent(None)

        for i in range(index // 2 + 1, len(self.layouts)):
            element = self.elements[i * 2 - 1]
            self.layouts[i].removeWidget(element)
            self.layouts[i - 1].addWidget(element, alignment=Qt.AlignCenter)
        if len(self.elements) % 2:
            label = QLabel()
            self.layouts[-1].addWidget(label)
            self._space.append(label)
        else:
            label = self._space.pop(-1)
            self.layouts[-1].removeWidget(label)
            self.removeItem(self.layouts[-1])
            self.layouts.pop(-1)


class GameConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        self.my_parent: MainConfigPage | None = my_parent
        self.config_file = self.my_parent.my_parent.config_file
        self.my_parent.game_button.lock()

        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.vbox = GridLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.top_frame = QFrame()
        self.layout.addWidget(self.top_frame)
        self.layout.addWidget(self.scroll_area, 4)
        self.setLayout(self.layout)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        self.table: list[StreamerBox] = []
        self.table_layout: list[QHBoxLayout] = []
        self.table_space: list[QSpacerItem] = []
        self.thread = None

    def load(self):
        self.thread = LoadImagesGameThread(self.config_file, self.my_parent.my_parent.notif_programe)
        self.thread.images_loaded.connect(self.init_ui)
        self.thread.start()

    def init_ui(self, images):
        self.top_frame.setFixedHeight(50)
        all_notif_switch_button = SwitchButton(self.top_frame, 40)
        all_notif_switch_button.move(250, 0)
        add_game = CustomButton(self.top_frame, "assets/ui/add_button.png")
        add_game.move(50, 0)
        for game, image_data in images.items():
            self.add_game(game, image_data)

        self.my_parent.game_button.unlock()
        all_notif_switch_button.clicked.connect(self.toogle_all)
        add_game.clicked.connect(self.change_add_game_page)

    def add_game(self, game, img_data):
        try:
            frame = GameGameBox(img_data, game, self.config_file)
            frame.delete_button.clicked.connect(lambda _, f_frame=frame: self.remove_game(f_frame, game))
            frame.setFixedHeight(200)
            frame.setStyleSheet("border: 3px solid white")
            self.vbox.add_element(frame)
            self.table.append(frame)
        except Exception as erreur:
            print(erreur)

    def remove_game(self, widget: QFrame, name):
        self.config_file.delete_config(["games", name])
        self.vbox.remove_element(widget)
        widget.setParent(None)
        self.my_parent.addGamePage.game_filter.remove(name)

    def toogle_all(self, state):
        for frame in self.table:
            frame.notif_switch_button.toogle_state(state)

    def change_add_game_page(self, _):
        self.my_parent.general_button.lock()
        self.my_parent.game_button.lock()
        self.my_parent.streamer_button.lock()
        self.my_parent.change_config_page("add_game")

    def add_new_game(self, data):
        self.config_file.add_game(data[0])
        self.add_game(data[0], data[1])


class SuperGameBox(QFrame):
    def __init__(self, img_data, game_name, confil_file):
        super().__init__()

        self.setFixedWidth(525)

        self.img_data = img_data
        self.game_name = game_name
        self.config_file: FileConfig = confil_file

        self.label = QLabel(self)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.img_data, "")
        self.pixmap = self.pixmap.scaled(194, 194, Qt.AspectRatioMode.KeepAspectRatio)

        pixamp = self.pixmap.copy()
        image = QPixmap.toImage(pixamp)
        graysacle = image.convertToFormat(QImage.Format_Grayscale8)
        self.greyscale_pixmap = QPixmap.fromImage(graysacle)
        self.label.setPixmap(self.pixmap)

        self.nom_whidth = 300

        self.nom = QLabel(self)
        self.nom.setText(self.game_name)
        self.nom.move(210, 15)
        self.nom.setStyleSheet("color: white; font-size: 30px; border: none")
        self.nom.adjustSize()
        while self.nom.width() > self.nom_whidth:
            self.nom.setText(f"{self.nom.text().rstrip("...")[:-1].rstrip()}...")
            self.nom.adjustSize()
        self.nom.setFixedWidth(self.nom_whidth)

        self.delete_button = CustomButton(self, "assets/ui/delete.png", 30)
        self.delete_button.move(175, 15)

        self.notif_label = QLabel("Notifs", self)
        self.notif_label.move(175, 55)
        self.notif_label.setStyleSheet("color: white; font-size: 20px; border: none")
        self.notif_label.adjustSize()

        self.notif_switch_button = SwitchButton(self, 30)
        self.notif_switch_button.move(250, 55)

        self.sound_label = QLabel("Sons", self)
        self.sound_label.move(175, 95)
        self.sound_label.setStyleSheet("color: white; font-size: 20px; border: none")
        self.sound_label.adjustSize()

        self.sound_select_label = QLabel("Pas de son", self)
        self.sound_select_label.move(230, 95)
        self.sound_select_label.setStyleSheet("color: grey; font-size: 20px; border: none")
        self.sound_select_label.adjustSize()

        self.sound_select_button = CustomButton(self, "assets/ui/choice_sound.png", 30)
        self.sound_select_button.move(350, 95)

        self.design_label = QLabel("Style", self)
        self.design_label.move(175, 135)
        self.design_label.setStyleSheet("color: white; font-size: 20px; border: none")
        self.design_label.adjustSize()

        self.design_select_label = QLabel("Pas de style", self)
        self.design_select_label.move(230, 135)
        self.design_select_label.setStyleSheet("color: grey; font-size: 20px; border: none")
        self.design_select_label.adjustSize()

        self.design_select_button = CustomButton(self, "assets/ui/choice_style.png", 30)
        self.design_select_button.move(350, 135)


class GameGameBox(SuperGameBox):
    def __init__(self, img_data, game_name, confil_file):
        super().__init__(img_data, game_name, confil_file)

        self.notif_switch_button.clicked.connect(lambda state:
                                                 self.config_file.edit_config(["games", game_name, "notif"],
                                                                              state))
        self.notif_switch_button.toogle_state(self.config_file.get_config(["games", game_name, "notif"]))

        self.notif_priority = NbrSelecteur(self, 30)
        self.notif_priority.move(465, 55)
        self.notif_priority.set_value(self.config_file.get_config(["games", game_name, "notif_priority"]))
        self.notif_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["games", game_name, "notif_priority"],
                                                                         self.notif_priority.value))

        self.sound_priority = NbrSelecteur(self, 30)
        self.sound_priority.move(465, 95)
        self.sound_priority.set_value(self.config_file.get_config(["games", game_name, "sound_priority"]))
        self.sound_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["games", game_name, "sound_priority"],
                                                                         self.sound_priority.value))

        self.design_priority = NbrSelecteur(self, 30)
        self.design_priority.move(465, 135)
        self.design_priority.set_value(self.config_file.get_config(["games", game_name, "design_priority"]))
        self.design_priority.clicked.connect(lambda:
                                             self.config_file.edit_config(["games", game_name, "design_priority"],
                                                                          self.design_priority.value))


class StreamerGameBox(SuperGameBox):
    def __init__(self, img_data, game_name, confil_file, streamer_id):
        super().__init__(img_data, game_name, confil_file)

        self.streamer_id = streamer_id
        self.delete_button.move(210, 15)

        self.nom.move(245, 15)
        self.nom_whidth = 265
        self.nom.setMinimumSize(0, 0)
        self.nom.adjustSize()
        while self.nom.width() > self.nom_whidth:
            self.nom.setText(f"{self.nom.text().rstrip("...")[:-1].rstrip()}...")
            self.nom.adjustSize()
        self.nom.setFixedWidth(self.nom_whidth)

        self.notif_switch_button.toogle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                           "games", game_name, "notif"]))
        self.notif_switch_button.clicked.connect(lambda state:
                                                 self.config_file.edit_config(["streamer", self.streamer_id,
                                                                               "games", game_name, "notif"], state))

        self.notif_priority = CircleButton(self, 30)
        self.notif_priority.move(465, 55)
        self.notif_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                      "games", game_name, "notif_active"]))
        self.notif_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                            self.config_file.edit_config(["streamer", self.streamer_id, "games",
                                                                          game_name, "notif_active"],
                                                                         self.notif_priority.is_select)))

        self.sound_priority = CircleButton(self, 30)
        self.sound_priority.move(465, 95)
        self.sound_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                      "games", game_name, "sound_active"]))
        self.sound_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                            self.config_file.edit_config(["streamer", self.streamer_id, "games",
                                                                          game_name, "sound_active"],
                                                                         self.sound_priority.is_select)))

        self.design_priority = CircleButton(self, 30)
        self.design_priority.move(465, 135)
        self.design_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                       "games", game_name, "design_active"]))
        self.design_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                             self.config_file.edit_config(["streamer", self.streamer_id, "games",
                                                                           game_name, "design_active"],
                                                                          self.design_priority.is_select)))

        if True not in [self.notif_priority.is_select, self.sound_priority.is_select, self.design_priority.is_select]:
            self.label.setPixmap(self.greyscale_pixmap)

    def button_propertie(self, func):
        func()
        if self.notif_priority.is_select == self.sound_priority.is_select == self.design_priority.is_select is False:
            self.switch_button(False, self.game_name)
        elif [self.notif_priority.is_select, self.sound_priority.is_select,
              self.design_priority.is_select].count(True) == 1:
            self.switch_button(True, self.game_name)

    def switch_button(self, state, game_name):
        self.config_file.edit_config(["streamer", self.streamer_id, "games",
                                      game_name, "is_active"], state)
        if not state:
            self.label.setPixmap(self.greyscale_pixmap)
        else:
            self.label.setPixmap(self.pixmap)


class LoadImagesGameThread(QThread):
    images_loaded = pyqtSignal(dict)

    def __init__(self, config_file, notif_programe):
        super().__init__()
        self.config_file = config_file
        self.profil_img_file = FileImg("assets/game_img")
        self.notif_programe = notif_programe

    def run(self):
        images = {}
        games = self.config_file.get_games()
        for game_name in games:
            img_data = self.profil_img_file.get_game_img(game_name)
            if not img_data:
                img_data = self.notif_programe.get_game_img(game_name)
                self.profil_img_file.save_profil_img(game_name, img_data)

            images[game_name] = img_data

        self.images_loaded.emit(images)


class AddGamePage(QWidget):
    addgame = pyqtSignal(tuple)

    def __init__(self, my_parent=None, config_parent=None, game_filter=None):
        super().__init__()
        self.config_parent: MainConfigPage = config_parent
        self.my_parent = my_parent

        self.game_filter: list = game_filter or []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.main_layout = QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        self.search_game = QLineEdit()
        self.search_game.setFixedSize(300, 50)
        self.search_game.setStyleSheet("font-size: 30px; color: white")
        self.search_game.returnPressed.connect(self.launch_search)
        self.main_layout.addWidget(self.search_game, 1, alignment=Qt.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: 2px solid grey")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(50, 50, 50, 50)
        self.vbox.setSpacing(20)
        self.widget = QWidget()
        self.widget.setStyleSheet("border: none")
        self.scroll_area.setWidget(self.widget)
        self.widget.setLayout(self.vbox)

        self.main_layout.addWidget(self.scroll_area, 9)

        self.finish_button = CustomButton(None, "assets/ui/finish_button.png", 100)
        self.finish_button.clicked.connect(self.quit)

        self.layout.addWidget(self.frame)
        self.layout.addWidget(self.finish_button, alignment=Qt.AlignCenter)
        self.table: dict[str, AddGameBox] = {}
        self.thread: QThread | None = None

        self.load = None

    def quit(self, _):
        if self.thread:
            self.thread.terminate()
        self.config_parent.general_button.unlock()
        self.config_parent.game_button.unlock()
        self.config_parent.streamer_button.unlock()
        self.config_parent.change_config_page(page=self.my_parent)
        self.search_game.setText("")
        for i in reversed(range(self.vbox.count())):
            self.vbox.itemAt(i).widget().deleteLater()
        self.table.clear()

    def launch_search(self):
        self.table.clear()
        for i in reversed(range(self.vbox.count())):
            self.vbox.itemAt(i).widget().deleteLater()
        if self.thread:
            self.thread.terminate()
        if not self.search_game.text():
            return

        data = self.config_parent.my_parent.notif_programe.search_game(self.search_game.text())
        data = list(filter(lambda x: x.get("name") not in self.game_filter, data))
        self.thread = LoadImageGameSearch(self.config_parent.my_parent.notif_programe, data)
        self.thread.image_loaded.connect(self.add_game)
        self.thread.start()
        self.load = QFrame()
        if len(data) == 2:
            self.load.setFixedHeight(200)
        layout = QVBoxLayout()
        spinner = RotatingWidget(100)
        spinner.start_animation()
        self.load.setLayout(layout)
        layout.addWidget(spinner, alignment=Qt.AlignHCenter)
        self.vbox.addWidget(self.load)

    def add_game(self, data, end):
        frame = AddGameBox(data)
        frame.add_button.clicked.connect(lambda: self.add_new_game(data[0], data[1]))
        self.table[data[0]] = frame
        self.vbox.insertWidget(len(self.table) - 1, frame)
        if end:
            self.vbox.removeWidget(self.load)
            self.load.setParent(None)

    def add_new_game(self, game, img_data):
        self.game_filter.append(game)
        self.addgame.emit((game, img_data))
        self.vbox.removeWidget(self.table.get(game))
        self.table.get(game).setParent(None)


class AddGameBox(QFrame):
    def __init__(self, data):
        super().__init__()
        self.setFixedHeight(200)
        self.setStyleSheet("border: 3px solid white")

        self.image = QLabel(self)
        pixmap = QPixmap()
        pixmap.loadFromData(data[1], "")
        pixmap = pixmap.scaled(194, 194, Qt.AspectRatioMode.KeepAspectRatio)
        self.image.setPixmap(pixmap)
        self.image.move(0, 0)

        self.label = QLabel(data[0], self)
        self.label.setStyleSheet("color: white; font-size: 50px; border: none")
        self.label.move(175, 10)
        self.label.adjustSize()

        self.add_button = CustomButton(self, "assets/ui/add_button.png")
        self.add_button.move(175, 125)


class LoadImageGameSearch(QThread):
    images_loaded = pyqtSignal(dict)
    image_loaded = pyqtSignal(tuple, bool)

    def __init__(self, notif_program, data):
        super().__init__()
        self.notif_program: NotifProgram = notif_program
        self.data = data

    def run(self):
        images = {}
        for k, game in enumerate(self.data):
            game = game.get("name")
            img_data = self.notif_program.get_game_img(game_name=game)
            self.image_loaded.emit((game, img_data), k == len(self.data) - 1)
            images[game] = img_data
        self.images_loaded.emit(images)


class MainWindows(QMainWindow):
    notif_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Twitch Notif config")
        self.setStyleSheet("background: rgb(45, 45, 45)")
        self.setWindowState(Qt.WindowMaximized)

        self.notif_signal.connect(self.notif_signal_event)
        self.config_file = FileConfig("twitch-notif-config.json")

        self.notif_programe = NotifProgram(self.notif_signal, self.config_file)
        self.notif_thread = None
        self.pages = {}

        self.staked_widget = QStackedWidget()
        self.connectpage = ConnectPage()
        self.main_config_page = MainConfigPage(self)

        self.closeEvent = lambda event: self.quit(event)
        self.init_ui()

    def init_ui(self):
        self.setCentralWidget(self.staked_widget)

        self.add_page(self.connectpage, "connect_page")
        self.add_page(self.main_config_page, "main_config_page")
        self.pages["connect_page"].clicked.connect(self.connection)

        self.change_page("connect_page")

    def add_page(self, widget, name):
        self.pages[name] = widget
        self.staked_widget.addWidget(widget)

    def change_page(self, name):
        self.staked_widget.setCurrentWidget(self.pages.get(name))

    def quit(self, event: QCloseEvent):
        event.ignore()
        self.hide()

    def quit_all(self):
        self.notif_programe.running = False
        self.notif_programe.sleep.set()
        app.quit()

    def connection(self):
        self.notif_thread = threading.Thread(target=self.notif_programe.loop_notif, daemon=True)
        self.notif_thread.start()

    def notif_signal_event(self, event: dict):
        if event.get("type") == "cmd":
            if event.get("content") == "is_starting":
                for streamer in self.notif_programe.get_streamers_followed():
                    self.config_file.add_streamer(*streamer)
                self.main_config_page.streamerPage.load()
                self.main_config_page.gamePage.load()
                self.change_page("main_config_page")

            elif event.get("content") == "fail_starting":
                self.connectpage.unblock_connect_button()

        elif event.get("type") == "inlive":
            if not self.main_config_page.streamerPage.is_load:
                self.main_config_page.streamerPage.file.append(
                    lambda: self.main_config_page.streamerPage.state_live(event.get("content")))
            else:
                self.main_config_page.streamerPage.state_live(event.get("content"))


if __name__ == '__main__':
    if os.path.exists("twitch-notif-config.template.json") and not os.path.exists("twitch-notif-config.json"):
        os.rename("twitch-notif-config.template.json", "twitch-notif-config.json")

    # Initialiser l'application
    app = QApplication(sys.argv)
    mainwindows = MainWindows()

    # Créer une icône de la barre système
    tray_icon = QSystemTrayIcon(QIcon("assets/twitch_logo.png"), app)
    tray_menu = QMenu()

    # Ajouter une action pour lancer
    launch = tray_menu.addAction("Ouvrir")
    launch.triggered.connect(lambda: mainwindows.showMaximized())
    mainwindows.showMaximized()

    # Ajouter une action pour quitter
    quit_action = tray_menu.addAction("Quitter")
    quit_action.triggered.connect(mainwindows.quit_all)

    # Configurer le menu
    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("Twitch Notif config")
    tray_icon.show()

    sys.exit(app.exec_())
