# -*- coding: utf-8 -*-

import os  # операции с файлами
import sys  # аргументы командной строки
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QGraphicsPixmapItem, QGraphicsScene,
                             QGraphicsView, QVBoxLayout, QMenuBar, QMenu, QFileDialog
                             )
from PyQt5.QtCore import Qt
from my_class import *


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.img_item = QGraphicsPixmapItem()
        self.scene = QGraphicsScene()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)
        self.scene.addItem(self.img_item)
        self.setScene(self.scene)
        self.setRenderHint(4)
        self.current_pixmap = None
        self.current_img_width = 0
        self.current_img_height = 0
        self.ratio = 1

    def scale_image_view(self, default_scale=1):
        # Масштабирование в представлении вида
        if self.current_pixmap:
            self.resetTransform()
            h = self.height()
            w = self.width()
            ratio_view = w / h
            self.current_img_width = self.current_pixmap.width()
            self.current_img_height = self.current_pixmap.height()
            if self.current_img_width / self.current_img_height > ratio_view:
                self.ratio = w / self.current_img_width
            else:
                self.ratio = h / self.current_img_height
            self.scene.setSceneRect(0, 0, self.current_img_height * ratio_view, self.current_img_height)
            # Смещение изображения к центру
            x = round((self.current_img_height * ratio_view - self.current_img_width) / 2)
            self.img_item.setPos(x, 0)
            if default_scale == 1:
                self.scale(self.ratio, self.ratio)
            else:
                self.scale(default_scale, default_scale)

    def show_image(self, scale=1):
        try:
            self.current_pixmap = QPixmap(self.main.files.current_image)
        except FileNotFoundError:
            print('Ошибка открытия графического файлв')
            return
        self.img_item.setPixmap(self.current_pixmap)
        self.scale_image_view(default_scale=scale)

    def mousePressEvent(self, event):
        # Обработка нажатия левой кнопки мыши
        if event.button() == Qt.LeftButton:
            self.show_image(scale=2)

    def mouseReleaseEvent(self, event):
        # Обработка снятия нажатия левой кнопки мыши
        if event.button() == Qt.LeftButton:
            self.show_image(scale=1)


class MainWindow(QWidget):
    """
    Виджет главного окна
    Связующий класс
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Просмотр изображений')
        self.open_dialog = QFileDialog()
        # Настройка меню
        self.menu = QMenuBar(self)
        self.file_menu = QMenu('Файл')
        self.open_dir = self.file_menu.addAction('Открыть каталог')
        self.open_dir.triggered.connect(self.open_dir_dialog)
        self.to_exit = self.file_menu.addAction('Выход')
        self.to_exit.triggered.connect(self.exit_programm)
        self.view_menu = QMenu('Вид')
        self.full = self.view_menu.addAction('Полноэкранный режим')
        self.full.triggered.connect(self.fullscreen_mode)
        self.view_subdir = self.view_menu.addAction('Структура каталога')
        self.view_subdir.setCheckable(True)
        self.view_subdir.setChecked(True)
        self.view_subdir.triggered.connect(self.show_info_subfolder)
        self.view_info = self.view_menu.addAction('Информация')
        self.view_info.setCheckable(True)
        self.view_info.setChecked(True)
        self.view_info.triggered.connect(self.show_info_label)
        self.menu.addMenu(self.file_menu)
        self.menu.addMenu(self.view_menu)
        # Настройка графического представления
        self.label = label.MyLabel(self)
        self.view = ImageViewer(self)
        self.files = files.Files()
        self.info_label = label.InfoLabel(self)
        self.structure = label.StructureFolder(self)
        self.structure.setVisible(False)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.view)
        self.view.setVisible(False)
        self.vbox.addWidget(self.label)
        self.setLayout(self.vbox)
        self.label.setAcceptDrops(True)
        self.vbox.setContentsMargins(4, 24, 4, 4)
        self.current_dir = None
        self.current_fullscreen = False
        app.focusChanged.connect(self.onFocusChanged)

    def onFocusChanged(self):
        self.setFocus()

    def show_image(self):
        if self.label.isVisible():
            self.label.setVisible(False)
        if not self.view.isVisible():
            self.view.setVisible(True)
        self.view.show_image()
        self.info_label.update()
        self.structure.update()

    def exit_programm(self):
        """Выход из программы"""
        QApplication.quit()

    def open_dir_dialog(self):
        """Выбор каталога для просмотра изображений"""
        self.current_dir = self.open_dialog.getExistingDirectory()
        self.files.scan_folder(self.current_dir)

    def fullscreen_mode(self):
        # Переключение полноэкранного режима
        self.current_fullscreen = not self.current_fullscreen
        if self.current_fullscreen:
            self.menu.setVisible(False)
            self.vbox.setContentsMargins(0, 0, 0, 0)
            self.showFullScreen()
        else:
            self.menu.setVisible(True)
            self.vbox.setContentsMargins(4, 24, 4, 4)
            self.showNormal()

    def show_info_label(self):
        if self.view_info.isChecked():
            self.info_label.setVisible(True)
            self.info_label.update()
        elif self.info_label.isVisible():
            self.info_label.setVisible(False)

    def show_info_subfolder(self):
        if self.view_subdir.isChecked():
            self.structure.setVisible(True)
            self.structure.update()
        elif self.structure.isVisible():
            self.structure.setVisible(False)

    def update_image(self):
        self.setWindowTitle(os.path.basename(self.files.current_image))
        self.show_image()

    def resizeEvent(self, event):
        # Перерисовка изображения при изменении размера
        self.view.scale_image_view()
        self.info_label.update()
        self.structure.update()

    def keyPressEvent(self, event):
        """
        Обработка нажатий клавиш клавиатуры
        """
        # свободные нажатия
        if event.modifiers() == Qt.NoModifier:
            # Выход из полноэкранного режима
            if event.key() == Qt.Key_Escape or event.key() == Qt.Key_F:
                self.fullscreen_mode()
            # Выход из программы
            elif event.key() == Qt.Key_Q:
                self.exit_programm()
            # изменения просматриваемого каталога
            elif event.key() == Qt.Key_PageUp:
                self.files.previous_dir()
                self.update_image()
            elif event.key() == Qt.Key_PageDown:
                self.files.next_dir()
                self.update_image()
            # перенос текущей картинки
            elif event.key() == Qt.Key_Up:
                self.files.move_image()
                self.update_image()
            # удаление текущей картинки
            elif event.key() == Qt.Key_Down:
                self.files.delete_image()
                self.update_image()
            # Следующее изображение
            elif event.key() == Qt.Key_Right:
                self.files.next_image()
                self.update_image()
            # Предыдущее изображение
            elif event.key() == Qt.Key_Left:
                self.files.previous_image()
                self.update_image()

        # С зажатой клавишей Shift
        if int(event.modifiers()) == Qt.ShiftModifier:
            # перемещение просматриваемого каталога
            if event.key() == Qt.Key_Up:
                self.files.move_dir()
                self.update_image()
            elif event.key() == Qt.Key_Down:
                self.files.delete_dir()
                self.update_image()
            # изменения просматриваемого каталога
            elif event.key() == Qt.Key_Left:
                self.files.previous_dir()
                self.update_image()
            elif event.key() == Qt.Key_Right:
                self.files.next_dir()
                self.update_image()

    def closeEvent(self, event):
        del self.files


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
