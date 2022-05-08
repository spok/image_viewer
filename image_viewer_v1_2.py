# -*- coding: utf-8 -*-

import os  # операции с файлами
import sys  # аргументы командной строки
from PyQt5.QtGui import QPixmap, QPainter, QMouseEvent
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
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing |QPainter.SmoothPixmapTransform)
        self.current_pixmap = None
        self.current_img_width = 0
        self.current_img_height = 0
        self.ratio = 1
        self.img_x = 0
        self.img_y = 0
        self.zoom_scale = False

    def scale_image_view(self):
        """Масштабирвоание изображение под размер экрана"""
        if self.current_pixmap:
            w = self.width()
            h = self.height()
            ratio_view = w / h
            self.current_img_width = self.current_pixmap.width()
            self.current_img_height = self.current_pixmap.height()
            try:
                if self.current_img_width / self.current_img_height > ratio_view:
                    self.ratio = w / self.current_img_width
                else:
                    self.ratio = h / self.current_img_height
            except ZeroDivisionError:
                self.ratio = ratio_view
            self.image_w = round(self.current_img_width * self.ratio)
            self.image_h = round(self.current_img_height * self.ratio)
            # Корректировка размеров сцены под пропорции экрана
            self.scene.setSceneRect(0, 0, w, h)
            # Перегрузка изображения в графический компонент
            self.img_item.setPixmap(self.current_pixmap.scaled(self.image_w, self.image_h,
                                                               aspectRatioMode=1, transformMode=1))
            # Смещение изображения к центру
            self.img_x = round((w - self.image_w) / 2)
            self.img_y = round((h - self.image_h) / 2)
            self.img_item.setPos(self.img_x, self.img_y)

    def show_image(self):
        try:
            self.current_pixmap = QPixmap(self.main.files.current_image)
        except FileNotFoundError:
            print('Ошибка открытия графического файлв')
            return
        self.img_item.setPixmap(self.current_pixmap)
        self.scale_image_view()

    def mousePressEvent(self, event):
        # Обработка нажатия левой кнопки мыши
        if event.button() == Qt.LeftButton and self.current_pixmap:
            self.setCursor(Qt.ClosedHandCursor)
            w = self.width()
            h = self.height()
            x = event.pos().x()
            y = event.pos().y()
            proc_x = (x - (w - self.image_w) / 2) / self.image_w
            proc_y = (y - (h - self.image_h) / 2) / self.image_h
            self.img_x = round((w - self.current_pixmap.width()) * proc_x)
            self.img_y = round((h - self.current_pixmap.height()) * proc_y)
            self.img_item.setPixmap(self.current_pixmap)
            self.img_item.setPos(self.img_x, self.img_y)
            self.zoom_scale = True

    def mouseReleaseEvent(self, event):
        # Обработка снятия нажатия левой кнопки мыши
        if event.button() == Qt.LeftButton and self.current_pixmap:
            self.zoom_scale = False
            self.show_image()
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Обработка перемещения мыши при увеличении изображения"""
        if self.current_pixmap:
            w = self.width()
            h = self.height()
            x = event.pos().x()
            y = event.pos().y()
            proc_x = x / w
            proc_y = y / h
            self.img_x = (w - self.current_pixmap.width()) * proc_x
            self.img_y = (h - self.current_pixmap.height()) * proc_y
            self.img_item.setPos(self.img_x, self.img_y)


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
