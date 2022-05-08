import os  # операции с файлами
from PyQt5.QtWidgets import (QLabel, QGraphicsDropShadowEffect, QTextEdit)
from PyQt5.QtGui import (QColor, QFont, QTextCursor)
from PyQt5.QtCore import Qt


class MyLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.available_extensions = ('.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                                     '.xpm', '.jpg', '.jpeg', '.png', '.gif'
                                     )
        text = '<h1 align="center">Кидать папку сюда!!!</h1>'
        text += '<div>Управление:</div>'
        text += '<div>кнопки ВЛЕВО/ВПРАВО - просмотр предыдущего/следующего изображения</div>'
        text += '<div>кнопки Shift+ВЛЕВО/Shift+ВПРАВО - перемещение на начало предыдущего/следующего каталога</div>'
        text += '<div>кнопки ВВЕРХ/Shift+ВВЕРХ - переместить изображение/каталог в специальную папку</div>'
        text += '<div>кнопки ВНИЗ/Shift+ВНИЗ - переместить изображение/каталог в каталог для удаленных файлов</div>'
        self.setText(text)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        drop_path = [u.toLocalFile() for u in e.mimeData().urls()]
        path = drop_path[0]
        self.parent.files.scan_folder(path)
        self.parent.resize(800, 600)
        self.parent.structure.setVisible(True)
        self.parent.show_image()


class InfoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files = self.parent.files

        self.setMargin(5)
        self.resize(50, 30)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint |
                            Qt.X11BypassWindowManagerHint)
        self.font = QFont()
        self.font.setItalic(True)
        self.font.setPointSize(11)
        self.font.setFamily('Liberation Serif')
        self.setFont(self.font)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor("#001100"))
        self.shadow.setOffset(1, 1)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGraphicsEffect(self.shadow)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.show()

    def update(self):
        count = self.files.count_files
        if count > 0:
            index = self.files.current_index + 1
            file_name = os.path.basename(os.path.dirname(self.files.current_image)) + ' -> '\
                        + os.path.split(self.files.current_image)[1]
            size = self.files.file_size()
            width = self.parent.view.current_img_width
            height = self.parent.view.current_img_height
            self.setText(
                    '<font color="#00ff00">'
                    '{0}  {1}x{2}  {3} {4}   {5}/{6}</font>'.format(
                            file_name, width, height, size[0], size[1], index, count
                    )
            )
            self.move(10, self.parent.height() - 30)
            self.adjustSize()
            self.raise_()


class StructureFolder(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.previos_dir = None
        self.move(2, 30)
        self.resize(400, self.main.view.height() - 60)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background:transparent;')
        self.setFrameShape(0)
        self.setTextColor(QColor("#001100"))
        self.font = QFont()
        self.font.setPointSize(10)
        self.font.setFamily('Liberation Serif')
        self.setFont(self.font)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setLineWrapMode(0)
        self.show()

    def update(self):
        self.move(2, 30)
        self.resize(400, self.main.view.height() - 60)
        folders = self.main.files.folder_list
        current_pos = None
        current_dir = os.path.dirname(self.main.files.current_image)
        if len(folders) > 0 and self.previos_dir != current_dir:
            rows = 0
            text = '<font color="#00ff00">'
            for key in folders:
                rows += 1
                if os.path.abspath(key) == current_dir:
                    bold = 'style="font-weight:bold; font-size: 13pt"'
                    current_pos = rows
                else:
                    bold = ''
                if folders[key][1] == 0:
                    text += f'<div {bold}>{folders[key][0]} - {folders[key][2]}</div>'
                else:
                    margin = 15 * folders[key][1]
                    text += f'<div style="margin-left: {margin}px" {bold}>└ {folders[key][0]} -' \
                            f' {folders[key][2]}</div>'
            self.setText(text)
            self.previos_dir = current_dir
            if current_pos:
                newCursor = self.textCursor()
                newCursor.setPosition(0)
                newCursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, current_pos)
                self.setTextCursor(newCursor)
                self.ensureCursorVisible()
        self.raise_()
