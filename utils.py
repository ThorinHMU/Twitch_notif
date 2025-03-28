from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re


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

    def clear(self):
        for i in self.elements:
            i.setParent(None)
        for i in self.layouts:
            self.removeItem(i)
            i.setParent(None)
        self.elements: list[QWidget] = []
        self.layouts: list[QVBoxLayout] = []
        self._space: list[QLabel] = []


class CustomEdit(QLineEdit):
    def __init__(self, parent, regex=None):
        super().__init__(parent)
        self.regex = regex

    def keyPressEvent(self, a0: QKeyEvent, event=None):
        text = self.text()
        super().keyPressEvent(a0)
        if not re.match(self.regex, self.text()):
            self.setText(text)
