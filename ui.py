from PyQt5.QtWidgets import (QAbstractButton, QLabel, QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
                             QGraphicsPixmapItem)
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QBitmap
from PyQt5.Qt import (Qt, QResizeEvent, QRect, pyqtSignal, QObject, QRegion, QMouseEvent, QKeyEvent, pyqtProperty,
                      QPropertyAnimation)
import keyboard


class CircleButton(QAbstractButton):
    def __init__(self, parent=None, size=50):
        super().__init__(parent)
        self.original_image_select = QPixmap("assets/ui/circle_selected.png")
        self.original_image_unselect = QPixmap("assets/ui/circle_unselected.png")
        self.is_select = False
        self.setFixedSize(int(self.img.width() / self.img.height() * size), size)
        self.__is_in_menu__ = False
        self.scaled_image = self.img
        self.update_mask()
        self._lock = False

    @property
    def img(self):
        if self.is_select:
            return self.original_image_select
        else:
            return self.original_image_unselect

    def resizeEvent(self, event: QResizeEvent):
        size = min(event.size().height(), event.size().width())
        super().resizeEvent(event)
        self.setGeometry(self.x(), self.y(), size, size)
        self.update_scaled_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.scaled_image)

    def update_scaled_image(self):
        self.scaled_image = self.img.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        self.update_mask()

    def update_mask(self):
        mask = self.scaled_image.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def mousePressEvent(self, e):
        if not self.__is_in_menu__ or not self.is_select and not self._lock:
            self.toggle_state(True if not self.is_select else False)
            self.clicked.emit()

    def toggle_state(self, state):
        self.is_select = state
        self.update_scaled_image()

    def lock(self):
        self._lock = True
        self.setCursor(Qt.ForbiddenCursor)

    def unlock(self):
        self._lock = False
        self.setCursor(Qt.ArrowCursor)

    def is_lock(self):
        return self._lock


class MutlipleChoice(QObject):
    choising = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.active_button: CircleButton | None = None
        self.choices = {}
        self.toogleEvent = None

    def add(self, button: CircleButton, name):
        self.choices.update({button: name})
        button.__is_in_menu__ = True
        if not self.active_button:
            self.active_button = button
            self.active_button.is_select = True
            self.active_button.update_scaled_image()
            self.active_button.update()
        button.clicked.connect(lambda: self.on_button_clicked(button))

    def on_button_clicked(self, clicked_button: CircleButton):
        if self.active_button != clicked_button and not clicked_button.is_lock():
            self.active_button.toggle_state(False)
            self.active_button.update()
            self.active_button = clicked_button
            self.choising.emit(self.choices[self.active_button])
            if self.toogleEvent:
                self.toogleEvent()


class CustomButton(QAbstractButton):
    def __init__(self, parent=None, path="", size=50):
        super().__init__(parent)
        self.img = QPixmap(path)
        self.setFixedSize(int(self.img.width()/self.img.height()*size), size)
        self.img = self.img.scaled(self.size(), transformMode=Qt.SmoothTransformation)
        self.update_mask()
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.img.isNull():
            # Centrer l'image dans le bouton
            painter.drawPixmap(self.rect(), self.img)
        else:
            painter.fillRect(self.rect(), Qt.black)  # Fond par défaut

    def update_mask(self):
        mask = self.img.mask()
        self.setMask(QRegion(mask))


class SwitchButton(QAbstractButton):
    clicked = pyqtSignal(bool)

    def __init__(self, parent=None, size=50):
        super().__init__(parent)
        self.img_on = QPixmap("assets/ui/toggle_on.png")
        self.img_off = QPixmap("assets/ui/toggle_off.png")
        self.setStyleSheet("background: red")
        self.state = True
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(int(self.img.width()/self.img.height()*size), size)
        self.scaled_image = self.img
        self.update_mask()

    @property
    def img(self):
        if self.state:
            return self.img_on
        else:
            return self.img_off

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.scaled_image)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.update_scaled_image()

    def update_scaled_image(self):
        self.scaled_image = self.img.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        self.update_mask()

    def update_mask(self):
        mask = self.scaled_image.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def toogle_state(self, state):
        self.state = state
        self.update_scaled_image()
        self.update()
        self.clicked.emit(self.state)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if self.state:
            self.toogle_state(False)
        else:
            self.toogle_state(True)


class NbrSelecteur(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None, size=50):
        super().__init__(parent)
        self.img = QPixmap("assets/ui/nbr_selecteur.png")
        self.img_mask = QPixmap("assets/ui/nbr_selecteur_mask.png")

        self.scaled_image = self.img
        self.scaled_mask = self.img_mask

        self.setFixedSize(int(self.img.width() / self.img.height() * size), size)

        self._value = 0

        self.label = QLabel(str(self.value), self)
        self.label.setStyleSheet(f"font-size: {int(size/3)}px; background: transparent; "
                                 f"font-weight: bold; color: white; border: none")
        self.label.move(20, 20)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.adjustSize()

        self.mask_text: QRegion | None = None
        self.mask_up: QRegion | None = None
        self.mask_down: QRegion | None = None
        self.update_scaled_image()

    @property
    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        self.label.setText(str(self.value))
        self.label.adjustSize()
        self.update_label_position()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.img)

    def update_scaled_image(self):
        self.scaled_image = self.img.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)

        self.scaled_mask = self.img_mask.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)

        self.mask_text = self.scaled_mask.createMaskFromColor(Qt.blue, Qt.MaskOutColor)
        self.mask_up = self.scaled_mask.createMaskFromColor(Qt.red, Qt.MaskOutColor)
        self.mask_down = self.scaled_mask.createMaskFromColor(Qt.green, Qt.MaskOutColor)

        self.mask_text = QRegion(self.mask_text)
        self.mask_up = QRegion(self.mask_up)
        self.mask_down = QRegion(self.mask_down)

        self.update_mask()
        self.update_label_position()

    def update_label_position(self):
        if self.mask_text.isEmpty():
            return
        rect = self.mask_text.subtracted(self.mask_up).subtracted(self.mask_down).boundingRect()
        rect.setWidth(int(rect.width()//1.2))
        self.label.setGeometry(rect)  # Positionner le QLabel

    def update_mask(self):
        mask = self.scaled_image.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def mousePressEvent(self, event: QMouseEvent):
        value = self.value
        if self.mask_up.contains(event.pos()):
            value += 10 if keyboard.is_pressed("shift") else 5 if keyboard.is_pressed("ctrl") else 1
            if value > 99:
                value = 99
        elif self.mask_down.contains(event.pos()):
            value -= 10 if keyboard.is_pressed("shift") else 5 if keyboard.is_pressed("ctrl") else 1
            if value < -1:
                value = -1
        else:
            return

        self.set_value(value)
        self.clicked.emit()


class RotatingWidget(QGraphicsView):
    def __init__(self, size=50):
        super().__init__()
        self.stop = False
        self.setStyleSheet("border: none; background: transparent")

        pixmap = QPixmap("assets/ui/loading_spinner.png").scaled(size, size, Qt.KeepAspectRatio,
                                                                              Qt.SmoothTransformation)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)

        self.pixmap_item.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)

        # Ajouter l'image à la scène
        self.scene.addItem(self.pixmap_item)

        # Désactiver les barres de scroll
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Ajuster la taille de la vue
        self.setFixedSize(size, size)
        self.setSceneRect(0, 0, size, size)

        # Initialiser l'angle de rotation
        self._angle = 0

        # Créer l'animation de rotation
        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setStartValue(360)
        self.animation.setEndValue(0)
        self.animation.setDuration(1000)  # 1 seconde pour une rotation complète
        self.animation.setLoopCount(-1)  # -1 pour une boucle infinie

    def setAngle(self, angle):
        """Appliquer la rotation à l'image de manière fluide et stable"""
        if self.stop:
            if angle < 5 or angle > 355:
                self.animation.stop()
                self.stop = False
        self._angle = angle
        self.pixmap_item.setRotation(angle)  # Rotation fluide avec QGraphicsItem

    def getAngle(self):
        return self._angle

    # Définition de la propriété animable avec pyqtProperty
    angle = pyqtProperty(int, getAngle, setAngle)

    def start_animation(self):
        """Démarrer l'animation de rotation"""
        if self.animation.state() == QPropertyAnimation.Stopped:
            self.animation.start()

    def stop_animation(self):
        """Arrêter l'animation et remettre l'image droite"""
        self.stop = True
