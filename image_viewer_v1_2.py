# -*- coding: utf-8 -*-

import os  # операции с файлами
import sys  # аргументы командной строки
from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, QMenuBar, QMenu, QFileDialog)
from PyQt5.QtCore import Qt
from my_class import *


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
        self.view = images.ImageViewer(self)
        self.files = files.Files()
        self.info_label = label.InfoLabel(self)
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
        elif self.structure.isVisible():
            self.structure.setVisible(False)

    def update_image(self):
        self.setWindowTitle(os.path.basename(self.files.current_image))
        self.show_image()

    def resizeEvent(self, event):
        # Перерисовка изображения при изменении размера
        self.view.scale_image_view()
        self.info_label.update()

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
            # перемещение к предыдущему каталогу
            elif event.key() == Qt.Key_PageUp:
                self.files.previous_dir()
                self.update_image()
            # перемещение к следующему каталогу
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
            # перемещение просматриваемого каталога в избранное
            elif event.key() == Qt.Key_Insert:
                key = os.path.dirname(self.files.current_image)
                del self.files.folder_list[key]
                self.files.move_dir()
                self.update_image()
            # перемещение просматриваемого каталога в корзину
            elif event.key() == Qt.Key_Delete:
                key = os.path.dirname(self.files.current_image)
                del self.files.folder_list[key]
                self.files.delete_dir()
                self.update_image()

        # С зажатой клавишей Shift
        if int(event.modifiers()) == Qt.ShiftModifier:
            # перемещение просматриваемого каталога в избранное
            if event.key() == Qt.Key_Up:
                key = os.path.dirname(self.files.current_image)
                del self.files.folder_list[key]
                self.files.move_dir()
                self.update_image()
            # перемещение просматриваемого каталога в корзину
            elif event.key() == Qt.Key_Down:
                key = os.path.dirname(self.files.current_image)
                del self.files.folder_list[key]
                self.files.delete_dir()
                self.update_image()
            # перемещение к предыдущему каталогу
            elif event.key() == Qt.Key_Left:
                self.files.previous_dir()
                self.update_image()
            # перемещение к следующему каталогу
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
