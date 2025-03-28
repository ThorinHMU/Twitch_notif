import os
import sys
import threading
import webbrowser

from config import FileConfig, FileImg
from notif import NotifProgram
from ui import *
from utils import *


class ConnectPage(QWidget):
    clicked = pyqtSignal(name="")

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

        self.body_widget = QStackedWidget(None)
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
        self.sound_page = AddSoundPage(self)
        self.style_page = AddStylePage(self)
        self.layout = QVBoxLayout()

        self.frame = QFrame(None)
        self.frame.setStyleSheet('border: 5px solid white')
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        self.vbox = QVBoxLayout()
        self.frame.setLayout(self.vbox)

        # Sons
        # Titre
        self.title_sound = QLabel("Sons enregistrés:")
        self.title_sound.setStyleSheet("color: rgb(0, 0, 180); font-size: 50px; border: None")

        # Frame Principale (Sons)
        self.frame_sound = QFrame(None)
        self.frame_sound.setStyleSheet("border: 2px solid rgb(0, 0, 180);")
        self.frame_sound.setFixedHeight(300)

        # Layout Principal (Sons)
        self.layout_main_sound = QVBoxLayout()
        self.layout_main_sound.setContentsMargins(0, 0, 0, 0)

        # Layout contenant les Sons
        self.layout_content_sound = QHBoxLayout()

        # Zone pour Scroll (Sons)
        self.scroll_area_content_sound = QScrollArea(None)
        self.scroll_area_content_sound.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area_content_sound.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area_content_sound.setWidgetResizable(True)

        self.widget_sound = QWidget()
        self.grid_sound = HGridLayout()

        # Charge les Sons dans la zone de scroll
        self.sounds = []
        self.load_sounds()

        self.widget_sound.setLayout(self.grid_sound)
        self.scroll_area_content_sound.setWidget(self.widget_sound)
        self.layout_content_sound.addWidget(self.scroll_area_content_sound)

        # Frame Ajouter Sons
        self.add_sound_frame = QFrame(None)
        self.add_sound_frame.setFixedHeight(70)
        self.add_sound_frame.setStyleSheet("border: None")

        # Bouton Ajouter Sons
        self.add_sound_button = CustomButton(self.add_sound_frame, path="assets/ui/add_button.png")
        self.add_sound_button.clicked.connect(self.add_sound)
        self.add_sound_button.move(10, 10)

        # Text Ajouter Sons
        self.add_sound_label = QLabel("Ajouter un son", self.add_sound_frame)
        self.add_sound_label.move(70, 20)
        self.add_sound_label.setStyleSheet("color: white; font-size: 25px; border: None")

        self.layout_main_sound.addLayout(self.layout_content_sound, 1)
        self.layout_main_sound.addWidget(self.add_sound_frame, alignment=Qt.AlignBottom)

        self.frame_sound.setLayout(self.layout_main_sound)

        # Style
        # Titre
        self.title_style = QLabel("Styles Enregistrés:")
        self.title_style.setStyleSheet("color: rgb(150, 0, 180); font-size: 50px; border: None")

        # Frame Principale (Style)
        self.frame_style = QFrame(None)
        self.frame_style.setStyleSheet("border: 2px solid rgb(150, 0, 180);")
        self.frame_style.setFixedHeight(300)

        # Layout Principale (Style)
        self.layout_main_style = QVBoxLayout()
        self.layout_main_style.setContentsMargins(0, 0, 0, 0)

        # Layout contenant les Styles
        self.layout_content_style = QHBoxLayout()

        # Zone pour Scroll (Style)
        self.scroll_area_content_style = QScrollArea(None)
        self.scroll_area_content_style.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area_content_style.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area_content_style.setWidgetResizable(True)

        self.widget_style = QWidget()
        self.grid_style = HGridLayout()

        # Charge les Styles dans la zone de scroll
        self.styles = []
        self.load_styles()

        self.widget_style.setLayout(self.grid_style)
        self.scroll_area_content_style.setWidget(self.widget_style)
        self.layout_content_style.addWidget(self.scroll_area_content_style)

        # Frame Ajouter Styles
        self.add_style_frame = QFrame(None)
        self.add_style_frame.setFixedHeight(70)
        self.add_style_frame.setStyleSheet("border: None")

        # Bouton Ajouter Styles
        self.add_style_button = CustomButton(self.add_style_frame, path="assets/ui/add_button.png")
        self.add_style_button.clicked.connect(self.add_style)
        self.add_style_button.move(10, 10)

        # Text Ajouter Styles
        self.add_style_label = QLabel("Ajouter un style", self.add_style_frame)
        self.add_style_label.move(70, 20)
        self.add_style_label.setStyleSheet("color: white; font-size: 25px; border: None")

        self.layout_main_style.addLayout(self.layout_content_style, 1)
        self.layout_main_style.addWidget(self.add_style_frame, alignment=Qt.AlignBottom)

        self.frame_style.setLayout(self.layout_main_style)

        # Ajoute tous les Elements
        self.vbox.addWidget(self.title_sound, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.vbox.addWidget(self.frame_sound, 1, alignment=Qt.AlignTop)
        self.vbox.addStretch()
        self.vbox.addWidget(self.title_style, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.vbox.addWidget(self.frame_style, 1, alignment=Qt.AlignTop)
        # self.vbox.addWidget(ChoiceSound(self.my_parent.my_parent.config_file), 1, alignment=Qt.AlignTop)

    def add_sound(self):
        self.my_parent.change_config_page(page=self.sound_page)
        self.my_parent.general_button.lock()
        self.my_parent.game_button.lock()
        self.my_parent.streamer_button.lock()

    def edit_sound(self, sound):
        self.my_parent.change_config_page(page=EditSoundPage(self, sound))
        self.my_parent.general_button.lock()
        self.my_parent.game_button.lock()
        self.my_parent.streamer_button.lock()

    def delete_sound(self, name):
        sounds: dict = self.my_parent.my_parent.config_file.get_config(["general", "sounds"])
        sounds.pop(name)
        self.my_parent.my_parent.config_file.edit_config(["general", "sounds"], sounds)
        self.load_sounds()

    def load_sounds(self):
        self.grid_sound.clear()

        self.sounds: dict = self.my_parent.my_parent.config_file.get_config(["general", "sounds"])
        if not self.sounds:
            label = QLabel("Aucun son enregistré")
            label.setStyleSheet("border: None; color: grey; font-size: 30px")
            self.grid_sound.add_element(label)
        else:
            for name in self.sounds.keys():
                path = self.sounds[name]["path"]
                frame = QFrame(None)
                frame.setFixedSize(300, 56)
                frame.setStyleSheet("border: 2px solid grey;")
                label_name = QLineEdit(name, frame)
                label_name.setReadOnly(True)
                label_name.setStyleSheet("color: white; font-size: 20px; border: None;")
                label_path = QLineEdit(path, frame)
                label_path.setReadOnly(True)
                label_path.setStyleSheet("color: white; font-size: 16px; border: None;")
                label_name.setGeometry(3, 3, 240, 30)
                label_path.setGeometry(3, 30, 294, 25)
                label_name.setAlignment(Qt.AlignCenter)
                label_path.setAlignment(Qt.AlignCenter)
                delete_button = CustomButton(frame, "assets/ui/delete.png", 20)
                delete_button.clicked.connect(lambda _, fname=name, fpath=path: self.delete_sound(fname))
                delete_button.move(250, 5)

                edit_button = CustomButton(frame, "assets/ui/edit_button.png", 20)
                edit_button.clicked.connect(lambda _, fname=name, fpath=path: self.edit_sound(fname))
                edit_button.move(275, 5)

                self.grid_sound.add_element(frame)

    def add_style(self):
        self.my_parent.change_config_page(page=self.style_page)
        self.my_parent.general_button.lock()
        self.my_parent.game_button.lock()
        self.my_parent.streamer_button.lock()

    def edit_style(self, style):
        self.my_parent.change_config_page(page=EditStylePage(self, style))
        self.my_parent.general_button.lock()
        self.my_parent.game_button.lock()
        self.my_parent.streamer_button.lock()

    def delete_style(self, name):
        styles: dict = self.my_parent.my_parent.config_file.get_config(["general", "styles"])
        styles.pop(name)
        self.my_parent.my_parent.config_file.edit_config(["general", "styles"], styles)
        self.load_styles()

    def load_styles(self):
        self.grid_style.clear()

        self.styles = self.my_parent.my_parent.config_file.get_config(["general", "styles"])
        if not self.styles:
            label = QLabel("Aucun style enregistré")
            label.setStyleSheet("border: None; color: grey; font-size: 30px")
            self.grid_style.add_element(label)
        else:
            for items in self.styles.items():
                name = items[0]
                frame = QFrame(None)
                frame.setFixedSize(300, 56)
                frame.setStyleSheet("border: 2px solid grey;")
                label_name = QLineEdit(name, frame)
                label_name.setReadOnly(True)
                label_name.setStyleSheet("color: white; font-size: 20px; border: None;")
                label_name.setGeometry(3, 3, 240, 30)
                label_name.setAlignment(Qt.AlignCenter)
                delete_button = CustomButton(frame, "assets/ui/delete.png", 20)
                delete_button.clicked.connect(lambda _, fname=name: self.delete_style(fname))
                delete_button.move(250, 5)

                edit_button = CustomButton(frame, "assets/ui/edit_button.png", 20)
                edit_button.clicked.connect(lambda _, fname=name: self.edit_style(fname))
                edit_button.move(275, 5)

                self.grid_style.add_element(frame)


class AddSoundPage(QWidget):
    def __init__(self, my_parent):
        super().__init__()
        self.layout = QVBoxLayout()
        self.my_parent: GeneralConfigPage = my_parent
        self.path = None

        self.frame = QFrame(None)
        self.frame.setFixedSize(500, 365)

        self.label = QLabel("Enregister un nouveau son", self.frame)
        self.sound_name_text = QLabel("Nom du son: ", self.frame)
        self.sound_name_edit = CustomEdit(self.frame, r'^[\wÀ-ÖØ-öø-ÿ- ]{0,32}$')
        self.sound_path_button = CustomButton(self.frame, path="assets/ui/choice_sound.png")
        self.sound_path_text = QLineEdit(self.frame)
        self.valid_button = CustomButton(self.frame, path="assets/ui/validate.png")
        self.cancel_button = CustomButton(self.frame, path="assets/ui/cancel.png")

        self.label.setStyleSheet("color: white; font-size: 40px")
        self.label.move(10, 10)
        self.sound_name_text.setStyleSheet("color: white; font-size: 20px")
        self.sound_name_text.move(10, 100)
        self.sound_name_edit.setStyleSheet("color: white; font-size: 20px")
        self.sound_name_edit.move(250, 100)
        self.sound_path_button.clicked.connect(self.get_file)
        self.sound_path_button.move(10, 150)
        self.sound_path_text.move(250, 165)
        self.sound_path_text.setText(" " * 15 + "/")
        self.sound_path_text.setReadOnly(True)
        self.sound_path_text.setFixedWidth(250)
        self.sound_path_text.setStyleSheet("color: white; font-size: 20px; border: None")
        self.valid_button.move(175, 250)
        self.cancel_button.move(175, 310)

        self.valid_button.clicked.connect(self.valid)
        self.cancel_button.clicked.connect(self.cancel)

        self.layout.addWidget(self.frame, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def get_file(self):
        dialog = QFileDialog(None)
        dialog.setWindowTitle("Séléctionner un répertoire")
        dialog.setNameFilters(["Fichiers son (*.mp3 *.ogg *.wav *.flac *.aac *.m4a *.wma)"])
        dialog.setLabelText(QFileDialog.Accept, "Valider")
        dialog.setLabelText(QFileDialog.Reject, "Annuler")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QFileDialog.Accepted:
            directory = dialog.selectedFiles()[0]
            self.path = directory
            self.sound_path_text.setText(directory.split("/")[-1])
        else:
            return

    def valid(self):
        if not re.match(r'^[\wÀ-ÖØ-öø-ÿ- ]{1,32}$', self.sound_name_edit.text()) or not self.path:
            return
        sounds: dict = self.my_parent.my_parent.my_parent.config_file.get_config(["general", "sounds"])
        sounds.update({self.sound_name_edit.text(): {"path": self.path}})
        self.my_parent.my_parent.my_parent.config_file.edit_config(["general", "sounds"], sounds)
        self.__init__(self.my_parent)
        self.my_parent.load_sounds()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()

    def cancel(self):
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.__init__(self.my_parent)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)


class AddStylePage(QWidget):
    def __init__(self, my_parent):
        super().__init__()
        self.layout = QVBoxLayout()
        self.my_parent: GeneralConfigPage = my_parent

        self.icon_path = None
        self.img_path = None

        self.frame = QFrame(None)
        self.frame.setFixedSize(520, 500)

        self.title = QLabel("Enregister un nouveau Style", self.frame)
        self.title.setStyleSheet("color: white; font-size: 40px")
        self.title.move(10, 10)

        self.label_name = QLabel("Nom du style:", self.frame)
        self.label_name.setStyleSheet("color: white; font-size: 20px")
        self.label_name.move(10, 100)
        self.enter_name = CustomEdit(self.frame, r'^[\wÀ-ÖØ-öø-ÿ- ]{0,32}$')
        self.enter_name.setStyleSheet("color: white; font-size: 20px")
        self.enter_name.move(260, 100)

        self.label_text = QLabel("Text affiché:", self.frame)
        self.label_text.setStyleSheet("color: white; font-size: 20px")
        self.label_text.move(10, 160)
        self.enter_text = CustomEdit(self.frame, r'^[\S ]{0,500}$')
        self.enter_text.setStyleSheet("color: white; font-size: 20px")
        self.enter_text.move(260, 160)

        self.choices = ["Aucune image", "Profil du streamer", "Image du jeu", "Preview du stream", "Choisir une image"]
        self.label_choice_icon = QLabel("Petite Icon:", self.frame)
        self.label_choice_icon.setStyleSheet("color: white; font-size: 20px")
        self.label_choice_icon.move(10, 220)
        self.selecter_choice_icon = QComboBox(self.frame)
        self.selecter_choice_icon.setStyleSheet("color: white; font-size: 20px")
        self.selecter_choice_icon.addItems(self.choices)
        self.selecter_choice_icon.move(260, 220)
        self.selecter_choice_icon.activated.connect(lambda index, combobox=self.selecter_choice_icon:
                                                    self.activated(index, combobox))

        self.label_choice_img = QLabel("Grand image:", self.frame)
        self.label_choice_img.setStyleSheet("color: white; font-size: 20px")
        self.label_choice_img.move(10, 280)
        self.selecter_choice_img = QComboBox(self.frame)
        self.selecter_choice_img.setStyleSheet("color: white; font-size: 20px")
        self.selecter_choice_img.addItems(self.choices)
        self.selecter_choice_img.move(260, 280)
        self.selecter_choice_img.activated.connect(lambda index, combobox=self.selecter_choice_img:
                                                   self.activated(index, combobox))

        self.valid_button = CustomButton(self.frame, path="assets/ui/validate.png")
        self.cancel_button = CustomButton(self.frame, path="assets/ui/cancel.png")
        self.valid_button.move(175, 320)
        self.cancel_button.move(175, 380)

        self.valid_button.clicked.connect(self.valid)
        self.cancel_button.clicked.connect(self.cancel)

        self.layout.addWidget(self.frame, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    @staticmethod
    def activated(index, combobox):
        if index == 4:
            dialog = QFileDialog(None)
            dialog.setWindowTitle("Séléctionner une image")
            dialog.setNameFilters(["Fichiers d'image (*.png *.jpg *.jpeg)"])
            dialog.setLabelText(QFileDialog.Accept, "Valider")
            dialog.setLabelText(QFileDialog.Reject, "Annuler")
            dialog.setFileMode(QFileDialog.ExistingFile)
            if combobox.count() >= 5:
                combobox.removeItem(5)
            if dialog.exec_() == QFileDialog.Accepted:
                file = dialog.selectedFiles()[0]
                combobox.addItem(file)
                combobox.setCurrentIndex(5)
            else:
                combobox.setCurrentIndex(0)

    def valid(self):
        styles = self.my_parent.my_parent.my_parent.config_file.get_config(["general", "styles"])
        if (not re.match(r'^[\wÀ-ÖØ-öø-ÿ- ]{1,32}$', self.enter_name.text()) or
                not re.match(r'^[\S ]{0,500}$', self.enter_text.text()) or
                self.enter_name.text() in styles.keys() or
                self.selecter_choice_icon.currentIndex() == 4 or self.selecter_choice_img.currentIndex() == 4):
            return

        style = {self.enter_name.text():
                 {"text": self.enter_text.text(),
                  "little_icon": self.selecter_choice_icon.currentText(),
                  "little_icon_type": "value" if self.selecter_choice_icon.currentIndex() != 5 else "path",
                  "img": self.selecter_choice_img.currentText(),
                  "img_type": "value" if self.selecter_choice_img.currentIndex() != 5 else "path"}}

        styles.update(style)
        self.my_parent.my_parent.my_parent.config_file.edit_config(["general", "styles"], styles)
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.__init__(self.my_parent)
        self.my_parent.load_styles()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)

    def cancel(self):
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.__init__(self.my_parent)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)


class EditSoundPage(AddSoundPage):
    def __init__(self, my_parent, sound):
        super().__init__(my_parent)
        self.name = sound
        self.sounds: dict = self.my_parent.my_parent.my_parent.config_file.get_config(["general", "sounds"])
        self.path = self.sounds[self.name]["path"]

        self.sound_name_edit.setText(self.name)
        self.sound_path_text.setText(self.path)

    def valid(self):
        if not re.match(r'^[\wÀ-ÖØ-öø-ÿ- ]{1,32}$', self.sound_name_edit.text()) or not self.path:
            return
        if self.name != self.sound_name_edit.text():
            self.sounds.pop(self.name)
        self.sounds.update({self.sound_name_edit.text(): {"path": self.sound_path_text.text()}})
        self.my_parent.my_parent.my_parent.config_file.edit_config(["general", "sounds"], self.sounds)
        self.my_parent.load_sounds()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()

    def cancel(self):
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)


class EditStylePage(AddStylePage):
    def __init__(self, my_parent, style):
        super().__init__(my_parent)
        self.name = style
        self.styles: list = self.my_parent.my_parent.my_parent.config_file.get_config(["general", "styles"])
        self.style: dict = self.styles[style]

        self.enter_name.setText(style)
        self.enter_text.setText(self.style["text"])
        if self.style["little_icon"] not in self.choices:
            self.selecter_choice_icon.addItem(self.style["little_icon"])
        self.selecter_choice_icon.setCurrentText(self.style["little_icon"])
        if self.style["img"] not in self.choices:
            self.selecter_choice_img.addItem(self.style["img"])
        self.selecter_choice_img.setCurrentText(self.style["img"])

    def valid(self):
        if (not re.match(r'^[\wÀ-ÖØ-öø-ÿ- ]{1,32}$', self.enter_name.text()) or
                not re.match(r'^[\S ]{0,500}$', self.enter_text.text()) or
                self.selecter_choice_icon.currentIndex() == 4 or self.selecter_choice_img.currentIndex() == 4):
            return
        style = {self.enter_name.text():
                 {"text": self.enter_text.text(),
                  "little_icon": self.selecter_choice_icon.currentText(),
                  "little_icon_type": "value" if self.selecter_choice_icon.currentIndex() != 5 else "path",
                  "img": self.selecter_choice_img.currentText(),
                  "img_type": "value" if self.selecter_choice_img.currentIndex() != 5 else "path"}}

        if self.name != self.enter_name.text():
            self.styles.pop(self.name)
        self.styles.update(style)
        self.my_parent.my_parent.my_parent.config_file.edit_config(["general", "styles"], self.styles)
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.my_parent.load_styles()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)

    def cancel(self):
        self.my_parent.my_parent.general_button.unlock()
        self.my_parent.my_parent.game_button.unlock()
        self.my_parent.my_parent.streamer_button.unlock()
        self.my_parent.my_parent.change_config_page(page=self.my_parent)


class StreamerConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        self.lock_scroll = False
        self.my_parent: MainConfigPage | None = my_parent
        self.config_file = self.my_parent.my_parent.config_file
        self.my_parent.streamer_button.lock()
        self.file = []
        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea(None)
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.top_frame = QFrame(None)
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
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() + 207 * sens)

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
    finish = pyqtSignal(name="")

    def __init__(self, img_data, streamer_id, config_file, my_parent: StreamerConfigPage | None = None):
        super().__init__(None)
        self.games_imgs = []
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.my_parent = my_parent
        self.config_file: FileConfig = config_file

        self.setStyleSheet("border: 3px solid white; ")

        self.streamer_id = streamer_id

        self.first_frame = QFrame(None)
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

        sound = self.config_file.get_config(["streamer", self.streamer_id, "sound"])
        self.sound_select_label = QLabel(sound if sound else "Pas de son", self.first_frame)
        self.sound_select_label.move(280, 95)
        self.sound_select_label.setStyleSheet("color: grey; font-size: 20px; border: none; ")
        self.sound_select_label.adjustSize()

        self.sound_select_button = CustomButton(self.first_frame, "assets/ui/choice_sound.png", 30)
        self.sound_select_button.move(400, 95)
        self.sound_select_button.clicked.connect(self.choice_sound)

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

        design = self.config_file.get_config(["streamer", self.streamer_id, "design"])
        self.design_select_label = QLabel(design if design else "Pas de style", self.first_frame)
        self.design_select_label.move(280, 135)
        self.design_select_label.setStyleSheet("color: grey; font-size: 20px; border: none; ")
        self.design_select_label.adjustSize()

        self.design_select_button = CustomButton(self.first_frame, "assets/ui/choice_style.png", 30)
        self.design_select_button.move(400, 135)
        self.design_select_button.clicked.connect(self.choice_style)

        self.design_priority = NbrSelecteur(self.first_frame, 30)
        self.design_priority.move(515, 135)
        self.design_priority.set_value(self.config_file.get_config(["streamer", streamer_id, "design_priority"]))
        self.design_priority.clicked.connect(lambda:
                                             self.config_file.edit_config(["streamer", streamer_id, "design_priority"],
                                                                          self.design_priority.value))

        self.frame_add = QFrame(None)
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

        self.scroll_area = QScrollArea(None)
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

    def choice_sound(self, _):
        page = ChoiceSound(self.config_file)
        self.my_parent.my_parent.change_config_page(page=page)
        page.sound_selected.connect(self.set_sound)

    def set_sound(self, sound):
        config = self.config_file.get_config(["streamer", self.streamer_id])
        config["sound"] = sound if sound else 0
        self.config_file.edit_config(["streamer", self.streamer_id], config)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.sound_select_label.setText(sound or "Pas de son")

    def choice_style(self, _):
        page = ChoiceStyle(self.config_file)
        self.my_parent.my_parent.change_config_page(page=page)
        page.style_selected.connect(self.set_style)

    def set_style(self, style):
        config = self.config_file.get_config(["streamer", self.streamer_id])
        config["design"] = style if style else 0
        self.config_file.edit_config(["streamer", self.streamer_id], config)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.design_select_label.setText(style or "Pas de style")

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
        for game, (game_name, img_data) in images.items():
            self.add_img_game(game, game_name, img_data)
        self.vbox.addWidget(QLabel(""), 1)
        self.finish.emit()

    def remove_game(self, widget):
        self.config_file.delete_config(["streamer", widget.streamer_id, "games", widget.game_id])
        self.vbox.removeWidget(widget)
        widget.setParent(None)
        self.games_imgs.remove(widget)
        self.game_page.game_filter.remove(widget.game_id)

    def add_img_game(self, game, game_name, img_data):
        frame = StreamerGameBox(self, img_data, game, game_name, self.config_file, self.streamer_id)
        frame.delete_button.clicked.connect(lambda _, fframe=frame: self.remove_game(fframe))
        frame.setStyleSheet("border-right: 3px solid white; ")
        frame.setFixedHeight(194)
        self.games_imgs.append(frame)
        self.vbox.insertWidget(len(self.games_imgs) - 1, frame, alignment=Qt.AlignLeft)

    def add_new_game(self, data):
        game_id, name, img_data = data
        self.config_file.add_streamer_game(self.streamer_id, game_id, name)
        self.add_img_game(game_id, name, img_data)

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
    images_loaded = pyqtSignal(dict, name="")

    def __init__(self, config_file, notif_programe):
        super().__init__(None)
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
    images_loaded = pyqtSignal(dict, name="")

    def __init__(self, config_file, notif_programe, streamer_id):
        super().__init__(None)
        self.config_file = config_file
        self.profil_img_file = FileImg("assets/game_img")
        self.notif_programe = notif_programe
        self.streamer_id = streamer_id

    def run(self):
        images = {}

        games = self.config_file.get_streamer_game(self.streamer_id)
        for game_id in games:
            game_name = self.config_file.get_config(["streamer", self.streamer_id, game_id, "name"])
            img_data = self.profil_img_file.get_game_img(game_id)
            if not img_data:
                img_data = self.notif_programe.get_game_img(game_id)
                self.profil_img_file.save_profil_img(game_id, img_data)

            images[game_id] = [game_name, img_data]

        self.images_loaded.emit(images)


class GameConfigPage(QWidget):
    def __init__(self, my_parent=None):
        super().__init__()
        self.my_parent: MainConfigPage | None = my_parent
        self.config_file = self.my_parent.my_parent.config_file
        self.my_parent.game_button.lock()

        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea(None)
        self.vbox = GridLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.top_frame = QFrame(None)
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
        for game, (game_name, image_data) in images.items():
            self.add_game(game, game_name, image_data)

        self.my_parent.game_button.unlock()
        all_notif_switch_button.clicked.connect(self.toogle_all)
        add_game.clicked.connect(self.change_add_game_page)

    def add_game(self, game, game_name, img_data):
        try:
            frame = GameGameBox(self, img_data, game, game_name, self.config_file)
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
        game_id, name, game_img = data
        self.config_file.add_game(game_id, name)
        self.add_game(game_id, name, game_img)


class SuperGameBox(QFrame):
    def __init__(self, my_parent, img_data, game_id, game_name, confil_file):
        super().__init__(None)

        self.my_parent = my_parent
        self.setFixedWidth(525)
        self.config_file: FileConfig = confil_file

        self.img_data = img_data
        self.game_id = game_id
        self.game_name = game_name

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
    def __init__(self, my_parent, img_data, game_id, game_name, confil_file):
        super().__init__(my_parent, img_data, game_id, game_name, confil_file)

        self.notif_switch_button.clicked.connect(lambda state:
                                                 self.config_file.edit_config(["games", self.game_id, "notif"],
                                                                              state))
        self.notif_switch_button.toogle_state(self.config_file.get_config(["games", self.game_id, "notif"]))

        self.notif_priority = NbrSelecteur(self, 30)
        self.notif_priority.move(465, 55)
        self.notif_priority.set_value(self.config_file.get_config(["games", self.game_id, "notif_priority"]))
        self.notif_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["games", self.game_id, "notif_priority"],
                                                                         self.notif_priority.value))

        self.sound_priority = NbrSelecteur(self, 30)
        self.sound_priority.move(465, 95)
        self.sound_priority.set_value(self.config_file.get_config(["games", self.game_id, "sound_priority"]))
        self.sound_priority.clicked.connect(lambda:
                                            self.config_file.edit_config(["games", self.game_id, "sound_priority"],
                                                                         self.sound_priority.value))

        self.design_priority = NbrSelecteur(self, 30)
        self.design_priority.move(465, 135)
        self.design_priority.set_value(self.config_file.get_config(["games", self.game_id, "design_priority"]))
        self.design_priority.clicked.connect(lambda:
                                             self.config_file.edit_config(["games", self.game_id, "design_priority"],
                                                                          self.design_priority.value))

        sound = self.config_file.get_config(["games", self.game_id, "sound"])
        self.sound_select_label.setText(sound or "Pas de son")
        self.sound_select_button.clicked.connect(self.choice_sound)
        style = self.config_file.get_config(["games", self.game_id, "design"])
        self.sound_select_label.setText(style or "Pas de style")
        self.design_select_button.clicked.connect(self.choice_style)

    def choice_sound(self, _):
        page = ChoiceSound(self.config_file)
        self.my_parent.my_parent.change_config_page(page=page)
        page.sound_selected.connect(self.set_sound)

    def set_sound(self, sound):
        config = self.config_file.get_config(["games", self.game_id])
        config["sound"] = sound if sound else 0
        self.config_file.edit_config(["games", self.game_id], config)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.sound_select_label.setText(sound or "Pas de son")

    def choice_style(self, _):
        page = ChoiceStyle(self.config_file)
        self.my_parent.my_parent.change_config_page(page=page)
        page.style_selected.connect(self.set_style)

    def set_style(self, style):
        config = self.config_file.get_config(["games", self.game_id])
        config["design"] = style if style else 0
        self.config_file.edit_config(["games", self.game_id], config)
        self.my_parent.my_parent.change_config_page(page=self.my_parent)
        self.design_select_label.setText(style or "Pas de style")


class StreamerGameBox(SuperGameBox):
    def __init__(self, my_parent, img_data, game_id, game_name, confil_file, streamer_id):
        super().__init__(my_parent, img_data, game_id, game_name, confil_file)

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
                                                                           "games", self.game_id, "notif"]))
        self.notif_switch_button.clicked.connect(lambda state:
                                                 self.config_file.edit_config(["streamer", self.streamer_id,
                                                                               "games", self.game_id, "notif"], state))

        self.notif_priority = CircleButton(self, 30)
        self.notif_priority.move(465, 55)
        self.notif_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                      "games", self.game_name, "notif_active"]))
        self.notif_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                                                          self.config_file.edit_config(
                                                                              ["streamer", self.streamer_id, "games",
                                                                               self.game_id, "notif_active"],
                                                                              self.notif_priority.is_select)))

        self.sound_priority = CircleButton(self, 30)
        self.sound_priority.move(465, 95)
        self.sound_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                      "games", self.game_id, "sound_active"]))
        self.sound_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                                                          self.config_file.edit_config(
                                                                              ["streamer", self.streamer_id, "games",
                                                                               self.game_id, "sound_active"],
                                                                              self.sound_priority.is_select)))

        self.design_priority = CircleButton(self, 30)
        self.design_priority.move(465, 135)
        self.design_priority.toggle_state(self.config_file.get_config(["streamer", self.streamer_id,
                                                                       "games", self.game_id, "design_active"]))
        self.design_priority.clicked.connect(lambda: self.button_propertie(lambda:
                                                                           self.config_file.edit_config(
                                                                               ["streamer", self.streamer_id, "games",
                                                                                self.game_id, "design_active"],
                                                                               self.design_priority.is_select)))

        if True not in [self.notif_priority.is_select, self.sound_priority.is_select, self.design_priority.is_select]:
            self.label.setPixmap(self.greyscale_pixmap)

        sound = self.config_file.get_config(["streamer", self.streamer_id, "games", self.game_id, "sound"])
        self.sound_select_label.setText(sound or "Pas de son")
        self.sound_select_button.clicked.connect(self.choice_sound)
        style = self.config_file.get_config(["streamer", self.streamer_id, "games", self.game_id, "design"])
        self.sound_select_label.setText(style or "Pas de style")
        self.design_select_button.clicked.connect(self.choice_style)

    def choice_sound(self, _):
        page = ChoiceSound(self.config_file)
        self.my_parent.my_parent.my_parent.change_config_page(page=page)
        page.sound_selected.connect(self.set_sound)

    def set_sound(self, sound):
        config = self.config_file.get_config(["streamer", self.streamer_id, "games", self.game_id])
        config["sound"] = sound if sound else 0
        self.config_file.edit_config(["streamer", self.streamer_id, "games", self.game_id], config)
        self.my_parent.my_parent.my_parent.change_config_page(page=self.my_parent.my_parent)
        self.sound_select_label.setText(sound or "Pas de son")

    def choice_style(self, _):
        page = ChoiceStyle(self.config_file)
        self.my_parent.my_parent.my_parent.change_config_page(page=page)
        page.style_selected.connect(self.set_style)

    def set_style(self, style):
        config = self.config_file.get_config(["streamer", self.streamer_id, "games", self.game_id])
        config["design"] = style if style else 0
        self.config_file.edit_config(["streamer", self.streamer_id, "games", self.game_id], config)
        self.my_parent.my_parent.my_parent.change_config_page(page=self.my_parent.my_parent)
        self.design_select_label.setText(style or "Pas de style")

    def button_propertie(self, func):
        func()
        if self.notif_priority.is_select == self.sound_priority.is_select == self.design_priority.is_select is False:
            self.switch_button(False, self.game_id)
        elif [self.notif_priority.is_select, self.sound_priority.is_select,
              self.design_priority.is_select].count(True) == 1:
            self.switch_button(True, self.game_id)

    def switch_button(self, state, game_id):
        self.config_file.edit_config(["streamer", self.streamer_id, "games",
                                      game_id, "is_active"], state)
        if not state:
            self.label.setPixmap(self.greyscale_pixmap)
        else:
            self.label.setPixmap(self.pixmap)


class LoadImagesGameThread(QThread):
    images_loaded = pyqtSignal(dict, name="")

    def __init__(self, config_file, notif_programe):
        super().__init__(None)
        self.config_file = config_file
        self.profil_img_file = FileImg("assets/game_img")
        self.notif_programe = notif_programe

    def run(self):
        images = {}
        games = self.config_file.get_games()
        for game_id in games:
            game_name = self.config_file.get_config(["games", game_id, "name"])
            img_data = self.profil_img_file.get_game_img(game_id)
            if not img_data:
                img_data = self.notif_programe.get_game_img(game_id)
                self.profil_img_file.save_profil_img(game_id, img_data)

            images[game_id] = (game_name, img_data)

        self.images_loaded.emit(images)


class AddGamePage(QWidget):
    addgame = pyqtSignal(tuple, name="")

    def __init__(self, my_parent=None, config_parent=None, game_filter=None):
        super().__init__()
        self.config_parent: MainConfigPage = config_parent
        self.my_parent = my_parent

        self.game_filter: list = game_filter or []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame(None)
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.main_layout = QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        self.search_game = QLineEdit()
        self.search_game.setFixedSize(300, 50)
        self.search_game.setStyleSheet("font-size: 30px; color: white")
        self.search_game.returnPressed.connect(self.launch_search)
        self.main_layout.addWidget(self.search_game, 1, alignment=Qt.AlignCenter)

        self.scroll_area = QScrollArea(None)
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
        data = list(filter(lambda x: x.get("id") not in self.game_filter, data))
        self.thread = LoadImageGameSearch(self.config_parent.my_parent.notif_programe, data)
        self.thread.image_loaded.connect(self.add_game)
        self.thread.start()
        self.load = QFrame(None)
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
        frame.add_button.clicked.connect(lambda: self.add_new_game(*data))
        self.table[data[0]] = frame
        self.vbox.insertWidget(len(self.table) - 1, frame)
        if end:
            self.vbox.removeWidget(self.load)
            self.load.setParent(None)

    def add_new_game(self, game_id, game_name, img_data):
        self.game_filter.append(game_id)
        self.addgame.emit((game_id, game_name, img_data))
        self.vbox.removeWidget(self.table.get(game_id))
        self.table.get(game_id).setParent(None)


class AddGameBox(QFrame):
    def __init__(self, data):
        super().__init__(None)
        self.setFixedHeight(200)
        self.setStyleSheet("border: 3px solid white")

        self.image = QLabel(self)
        pixmap = QPixmap()
        pixmap.loadFromData(data[2], "")
        pixmap = pixmap.scaled(194, 194, Qt.AspectRatioMode.KeepAspectRatio)
        self.image.setPixmap(pixmap)
        self.image.move(0, 0)

        self.label = QLabel(data[1], self)
        self.label.setStyleSheet("color: white; font-size: 50px; border: none")
        self.label.move(175, 10)
        self.label.adjustSize()

        self.add_button = CustomButton(self, "assets/ui/add_button.png")
        self.add_button.move(175, 125)


class LoadImageGameSearch(QThread):
    images_loaded = pyqtSignal(dict, name="")
    image_loaded = pyqtSignal(tuple, bool, name="")

    def __init__(self, notif_program, data):
        super().__init__(None)
        self.notif_program: NotifProgram = notif_program
        self.data = data

    def run(self):
        images = {}
        for k, game in enumerate(self.data):
            game_id = game.get("id")
            game_name = game.get("name")
            img_data = self.notif_program.get_game_img(game_id=game_id)
            self.image_loaded.emit((game_id, game_name, img_data), k == len(self.data) - 1)
            images[game_id] = img_data
        self.images_loaded.emit(images)


class ChoiceSound(QWidget):
    sound_selected = pyqtSignal(str, name="")

    def __init__(self, confil_file):
        super().__init__()
        self.config_file: FileConfig = confil_file

        self.setStyleSheet("border: None")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scrollarea = QScrollArea()
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setFixedHeight(400)
        self.scrollarea.setStyleSheet("border: 2px solid black")
        self.widget = QWidget()
        self.vbox = HGridLayout()

        self.sounds = self.config_file.get_config(["general", "sounds"])

        frame = QFrame()
        frame.setFixedSize(300, 150)
        frame.setStyleSheet("border: 2px solid grey")
        frame.enterEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: white")
        frame.leaveEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: grey")
        frame.mousePressEvent = lambda _: self.select("")
        label = QLabel("Auncun Son", frame)
        label.setStyleSheet("font-size: 30px; color: grey; border: None")
        label.adjustSize()
        label.move(frame.width()//2-label.width()//2, frame.height()//2-label.height()//2)
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.vbox.add_element(frame)

        for sound in self.sounds.keys():
            frame = QFrame()
            frame.setFixedSize(300, 150)
            frame.setStyleSheet("border: 2px solid grey")
            frame.enterEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: white")
            frame.leaveEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: grey")
            frame.mousePressEvent = lambda _, fsound=sound: self.select(fsound)
            label = QLabel(sound, frame)
            label.setStyleSheet("font-size: 30px; color: grey; border: None")
            label.adjustSize()
            label.move(frame.width() // 2 - label.width() // 2, frame.height() // 2 - label.height() // 2)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.vbox.add_element(frame)

        self.widget.setLayout(self.vbox)
        self.scrollarea.setWidget(self.widget)

        self.layout.addWidget(self.scrollarea)

        self.setLayout(self.layout)

    def select(self, sound: str):
        self.sound_selected.emit(sound)


class ChoiceStyle(QWidget):
    style_selected = pyqtSignal(str, name="")

    def __init__(self, confil_file):
        super().__init__()
        self.config_file: FileConfig = confil_file

        self.setStyleSheet("border: None")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scrollarea = QScrollArea()
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setFixedHeight(400)
        self.scrollarea.setStyleSheet("border: 2px solid black")
        self.widget = QWidget()
        self.vbox = HGridLayout()

        self.styles = self.config_file.get_config(["general", "styles"])

        frame = QFrame()
        frame.setFixedSize(300, 150)
        frame.setStyleSheet("border: 2px solid grey")
        frame.enterEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: white")
        frame.leaveEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: grey")
        frame.mousePressEvent = lambda _: self.select("")
        label = QLabel("Default", frame)
        label.setStyleSheet("font-size: 30px; color: grey; border: None")
        label.adjustSize()
        label.move(frame.width()//2-label.width()//2, frame.height()//2-label.height()//2)
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.vbox.add_element(frame)

        for style in self.styles.keys():
            frame = QFrame()
            frame.setFixedSize(300, 150)
            frame.setStyleSheet("border: 2px solid grey")
            frame.enterEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: white")
            frame.leaveEvent = lambda _, fframe=frame: fframe.setStyleSheet("border-color: grey")
            frame.mousePressEvent = lambda _, fstyle=style: self.select(fstyle)
            label = QLabel(style, frame)
            label.setStyleSheet("font-size: 30px; color: grey; border: None")
            label.adjustSize()
            label.move(frame.width() // 2 - label.width() // 2, frame.height() // 2 - label.height() // 2)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.vbox.add_element(frame)

        self.widget.setLayout(self.vbox)
        self.scrollarea.setWidget(self.widget)

        self.layout.addWidget(self.scrollarea)

        self.setLayout(self.layout)

    def select(self, style: str):
        self.style_selected.emit(style)


class MainWindows(QMainWindow):
    notif_signal = pyqtSignal(dict, name="")

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

        self.staked_widget = QStackedWidget(None)
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
