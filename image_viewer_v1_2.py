# -*- coding: utf-8 -*-

import os  # операции с файлами
import sys  # аргументы командной строки
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QVBoxLayout, QMenuBar, QMenu,
                             QFileDialog, QLabel, QStatusBar, QToolBar, QAction, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from my_class import *


class MainWindow(QMainWindow):
    """
    Виджет главного окна
    Связующий класс
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Просмотр изображений')
        self.resize(800, 600)
        self.central_widget = QWidget()
        # Настройка меню
        self.menu = QMenuBar()
        self.file_menu = QMenu('Файл')
        self.open_dialog = QFileDialog()
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
        self.setMenuBar(self.menu)
        # Настройка графического представления
        self.label = label.MyLabel(self)
        self.view = images.ImageViewer(self)
        self.files = files.Files()
        self.info_label = label.InfoLabel(self)
        self.info_label.setVisible(False)
        self.scan_thread = files.ScanThread(self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.view)
        self.view.setVisible(False)
        self.vbox.addWidget(self.label)
        self.setLayout(self.vbox)
        self.label.setAcceptDrops(True)
        self.vbox.setContentsMargins(4, 24, 4, 4)
        self.current_dir = None
        self.current_fullscreen = False
        # Добавление нижней информационной панели
        self.status_bar = QStatusBar(self)
        self.label2 = QLabel('Имя файла: ')
        self.status_bar.addWidget(self.label2)
        self.label3 = QLabel('Размер изображения: 0х0')
        self.status_bar.addWidget(self.label3)
        self.label4 = QLabel('Объем: 0 кБ')
        self.status_bar.addWidget(self.label4)
        self.label5 = QLabel("0/0")
        self.status_bar.addPermanentWidget(self.label5)
        self.set_visible_statusbar(False)
        self.setStatusBar(self.status_bar)
        # Добавление нижней панели управления
        self.toolbar = QToolBar("Управление")
        self.toolbar.setMovable(False)
        self.spacer_left = QWidget()
        self.spacer_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(self.spacer_left)
        del_image = QAction(QIcon("icon/delete.png"), "Перемещение изображения в корзину", self)
        del_image.triggered.connect(self.del_image)
        self.toolbar.addAction(del_image)
        del_dir = QAction(QIcon("icon/delete-sweep.png"), "Перемещение каталога в корзину", self)
        del_dir.triggered.connect(self.del_dir)
        self.toolbar.addAction(del_dir)
        self.toolbar.addSeparator()
        prev_dir = QAction(QIcon("icon/skip-backward.png"), "Предыдущий каталог", self)
        prev_dir.triggered.connect(self.to_prev_dir)
        self.toolbar.addAction(prev_dir)
        prev_image = QAction(QIcon("icon/skip-previous.png"), "Предыдущее изображение", self)
        prev_image.triggered.connect(self.to_prev_image)
        self.toolbar.addAction(prev_image)
        next_image = QAction(QIcon("icon/skip-next.png"), "Следующее изображение", self)
        next_image.triggered.connect(self.to_next_image)
        self.toolbar.addAction(next_image)
        next_dir = QAction(QIcon("icon/skip-forward.png"), "Следующий каталог", self)
        next_dir.triggered.connect(self.to_next_dir)
        self.toolbar.addAction(next_dir)
        self.toolbar.addSeparator()
        fav_image = QAction(QIcon("icon/folder-star.png"), "Переместить изображение в избранное", self)
        fav_image.triggered.connect(self.to_favorites_image)
        self.toolbar.addAction(fav_image)
        fav_dir = QAction(QIcon("icon/folder-star-multiple.png"), "Переместить каталог в избранное", self)
        fav_dir.triggered.connect(self.to_favorites_dir)
        self.toolbar.addAction(fav_dir)
        self.spacer_right = QLabel()
        self.update_spacer_toolbar()
        self.toolbar.addWidget(self.spacer_right)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        self.toolbar.setEnabled(False)
        # Компановка главных компонентов
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        # Обработка событий
        app.focusChanged.connect(self.onFocusChanged)
        self.scan_thread.mysignal.connect(self.show_progress, Qt.QueuedConnection)
        self.scan_thread.finished.connect(self.end_scan)

    def onFocusChanged(self):
        self.setFocus()

    def update_spacer_toolbar(self):
        """Расчет выравнивателя элементов тоолбара по центру"""
        spacer = round((self.toolbar.width() - 8 * self.toolbar.iconSize().width()) / 2)
        self.spacer_right.setMinimumWidth(spacer)

    def to_view_image(self):
        """
        Отображение графических элементов для просмотра изображений
        :return:
        """
        self.label.setVisible(False)
        self.view.setVisible(True)

    def to_drop_down(self):
        """
        Отображение графических элементов для передачи каталога просмотра
        :return:
        """
        self.label.setVisible(True)
        self.view.setVisible(False)

    def show_scan_result(self):
        """
        Отображение количества каталогов и файлов
        :return:
        """
        if self.scan_thread.isRunning():
            self.status_bar.showMessage(f'Сканирование выполняется... Количество каталогов: ' \
                                        f'{len(self.files.folder_list)}, ' \
                                        f'количество файлов: {len(self.files.files_list)}', 1000)

    def update_statusbar(self):
        t = f"{self.files.current_index + 1} / {len(self.files.files_list)}"
        self.label5.setText(t)
        file_name = os.path.basename(os.path.dirname(self.files.current_image)) + ' -> ' \
                    + os.path.split(self.files.current_image)[1]
        size = self.files.file_size()
        width = self.view.current_img_width
        height = self.view.current_img_height
        self.label2.setText(file_name)
        self.label3.setText(f"Размер изображения: {width}x{height}")
        self.label4.setText(f"Объем: {size[0]} {size[1]}")

    def show_image(self):
        self.to_view_image()
        if len(self.files.files_list) > 0:
            self.view.show_image()
            self.info_label.update()
            self.update_statusbar()
        self.show_scan_result()

    def show_progress(self, files: list, folders: list):
        """
        Отображение на label прогресса сканирования структуры каталогов
        :return:
        """
        self.files.files_list = files
        self.files.folder_list = folders
        if self.files.current_image == '':
            self.files.current_image = self.files.files_list[0]
            self.files.current_index = 0
            self.show_image()
        self.show_scan_result()

    def end_scan(self):
        self.files.files_list = self.scan_thread.files_list
        self.files.folder_list = self.scan_thread.folder_list
        self.set_visible_statusbar(True)
        self.toolbar.setEnabled(True)
        self.status_bar.showMessage(f'Количество каталогов: {len(self.files.folder_list)}, '
                            f'количество файлов: {len(self.files.files_list)}', 1000)

    def exit_programm(self):
        """Выход из программы"""
        del files.ScanThread
        del files.Files
        QApplication.quit()

    def open_dir_dialog(self):
        """Выбор каталога для просмотра изображений"""
        self.current_dir = self.open_dialog.getExistingDirectory()
        self.scan_thread.path = self.current_dir
        self.scan_thread.start()

    def set_visible_statusbar(self, status: bool):
        """
        Установка режима видимости текста в статусбаре
        :param status: Значение True или False
        :return:
        """
        if isinstance(status, bool):
            self.label2.setVisible(status)
            self.label3.setVisible(status)
            self.label4.setVisible(status)
            self.label5.setVisible(status)

    def fullscreen_mode(self):
        # Переключение полноэкранного режима
        self.current_fullscreen = not self.current_fullscreen
        if self.current_fullscreen:
            self.menu.setVisible(False)
            self.status_bar.setVisible(False)
            self.info_label.setVisible(True)
            self.vbox.setContentsMargins(0, 0, 0, 0)
            self.showFullScreen()
            self.toolbar.setVisible(False)
        else:
            self.menu.setVisible(True)
            self.status_bar.setVisible(True)
            self.info_label.setVisible(False)
            self.vbox.setContentsMargins(4, 24, 4, 4)
            self.showNormal()
            self.toolbar.setVisible(True)
            self.update_spacer_toolbar()

    def show_info_label(self):
        if self.view_info.isChecked():
            self.info_label.setVisible(True)
            self.info_label.update()
        elif self.info_label.isVisible():
            self.info_label.setVisible(False)

    def show_info_subfolder(self):
        if self.view_subdir.isChecked():
            self.view.structure.is_visible = True
            self.view.structure.update()
        elif self.view.structure.is_visible:
            self.view.structure.is_visible = False
            self.view.structure.update()

    def update_image(self):
        self.setWindowTitle(os.path.basename(self.files.current_image))
        self.show_image()

    def resizeEvent(self, event):
        # Перерисовка изображения при изменении размера
        self.view.scale_image_view()
        self.view.structure.update()
        self.info_label.update()
        self.update_spacer_toolbar()

    def del_dir_in_list(self):
        """
        Удаление текущего каталога из списка каталогов
        :return:
        """
        key = os.path.dirname(self.files.current_image)
        index = [i for i, elem in enumerate(self.files.folder_list) if elem[0] == key]
        if len(index):
            del self.files.folder_list[index[0]]

    def to_next_image(self):
        """Переход к следующему изображению"""
        self.files.next_image()
        self.update_image()

    def to_prev_image(self):
        """Переход к предыдущему изображению"""
        self.files.previous_image()
        self.update_image()

    def to_next_dir(self):
        """Переход к следующему каталогу"""
        self.files.next_dir()
        self.update_image()

    def to_prev_dir(self):
        """переход к предыдущему каталогу"""
        self.files.previous_dir()
        self.update_image()

    def del_image(self):
        """Перенос в удаленные текущее изображение"""
        self.files.delete_image()
        self.update_image()

    def del_dir(self):
        """Перенос текущего каталога в избранное"""
        self.del_dir_in_list()
        self.files.delete_dir()
        self.update_image()

    def to_favorites_image(self):
        """Перенос изображения в избранное"""
        self.files.move_image()
        self.update_image()

    def to_favorites_dir(self):
        """Перенос каталога в избранное"""
        self.del_dir_in_list()
        self.files.move_dir()
        self.update_image()

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
                self.to_prev_dir()
            # перемещение к следующему каталогу
            elif event.key() == Qt.Key_PageDown:
                self.to_next_dir()
            # перенос текущей картинки
            elif event.key() == Qt.Key_Up:
                self.to_favorites_image()
            # удаление текущей картинки
            elif event.key() == Qt.Key_Down:
                self.del_image()
            # Следующее изображение
            elif event.key() == Qt.Key_Right:
                self.to_next_image()
            # Предыдущее изображение
            elif event.key() == Qt.Key_Left:
                self.to_prev_image()
            # перемещение просматриваемого каталога в избранное
            elif event.key() == Qt.Key_Insert:
                self.to_favorites_dir()
            # перемещение просматриваемого каталога в корзину
            elif event.key() == Qt.Key_Delete:
                self.del_dir()

        # С зажатой клавишей Shift
        if int(event.modifiers()) == Qt.ShiftModifier:
            # перемещение просматриваемого каталога в избранное
            if event.key() == Qt.Key_Up:
                self.to_favorites_dir()
            # перемещение просматриваемого каталога в корзину
            elif event.key() == Qt.Key_Down:
                self.del_dir()
            # перемещение к предыдущему каталогу
            elif event.key() == Qt.Key_Left:
                self.to_prev_dir()
            # перемещение к следующему каталогу
            elif event.key() == Qt.Key_Right:
                self.to_next_dir()

    def closeEvent(self, event):
        del self.files


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
