import os
from PyQt5.QtGui import QPixmap, QPainter, QMouseEvent, QFont, QPalette, QColor
from PyQt5.QtWidgets import (QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsTextItem
                             )
from PyQt5.QtCore import Qt


class FilesStructure:
    def __init__(self, parent=None):
        if parent:
            self.scene = parent.scene
            self.main = parent.main
        self.items = []
        self.width_pixel_name = 150
        self.font_size = 10
        # Настройка шрифтов
        self.normal_font = QFont('Liberation Serif', self.font_size)
        self.bold_font = QFont('Liberation Serif', self.font_size)
        self.bold_font.setBold(True)
        self.text_color = QColor("#00ff00")

    def clear_text_items(self):
        """
        Очистка массива с элементами
        :return:
        """
        if len(self.items) > 0:
            for item in self.items:
                self.scene.removeItem(item[0])
                self.scene.removeItem(item[1])
            self.items.clear()

    def update(self):
        """
        Обновление отображения структуры каталогов
        :return: None
        """
        self.clear_text_items()
        folders = self.main.files.folder_list
        current_dir = os.path.dirname(self.main.files.current_image)
        if len(folders) > 0:
            y = 5
            x = 5
            for key in folders:
                # Элемент с названием каталога
                name_text = QGraphicsTextItem()
                text = folders[key][0]
                name_text.setPlainText(text)
                if os.path.abspath(key) == current_dir:
                    name_text.setFont(self.bold_font)
                else:
                    name_text.setFont(self.normal_font)
                name_text.setDefaultTextColor(self.text_color)
                self.scene.addItem(name_text)
                # Сокращение длинных названий каталогов
                w = name_text.sceneBoundingRect().width()
                h = name_text.sceneBoundingRect().height()
                max_width = self.width_pixel_name - 15 * folders[key][1]
                if w > max_width:
                    count_char = round(max_width / w * len(text)) - 3
                    if count_char > 0:
                        text = text[:count_char] + '...'
                name_text.setPlainText(text)
                # Элемент с количеством файлов в каталоге
                count_text = QGraphicsTextItem()
                count_text.setPlainText(str(folders[key][2]))
                count_text.setFont(self.normal_font)
                count_text.setDefaultTextColor(self.text_color)
                self.scene.addItem(count_text)
                # Определение положения на сцене
                x = 5 + 15 * folders[key][1]
                name_text.setPos(x, y)
                count_text.setPos(x + max_width + 20, y)
                y += h + 4
                self.items.append((name_text, count_text))


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
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.current_pixmap = None
        self.current_img_width = 0
        self.current_img_height = 0
        self.ratio = 1
        self.img_x = 0
        self.img_y = 0
        self.zoom_scale = False
        self.structure = FilesStructure(self)

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
        self.structure.update()

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
        if self.current_pixmap and self.zoom_scale:
            w = self.width()
            h = self.height()
            x = event.pos().x()
            y = event.pos().y()
            proc_x = x / w
            proc_y = y / h
            self.img_x = (w - self.current_pixmap.width()) * proc_x
            self.img_y = (h - self.current_pixmap.height()) * proc_y
            self.img_item.setPos(self.img_x, self.img_y)
