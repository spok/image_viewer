import os  # операции с файлами
from PyQt5.QtWidgets import (QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QColor, QFont)
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
        text += '<div>кнопки ВВЕРХ/Insert(Shift+ВВЕРХ) - переместить изображение/каталог в специальную папку</div>'
        text += '<div>кнопки ВНИЗ/Delete(Shift+ВНИЗ) - переместить изображение/каталог в каталог для удаленных файлов</div>'
        text += '<div>кнопки F/Esc - включение/отключение полноэкранного режима</div>'
        self.setText(text)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        drop_path = [u.toLocalFile() for u in e.mimeData().urls()]
        path = drop_path[0]
        self.parent.scan_thread.path = path
        self.parent.scan_thread.start()
        self.parent.files.path = path
        self.parent.resize(800, 600)


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
        count = len(self.files.files_list)
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
            self.move(10, self.parent.view.height() - 30)
            self.adjustSize()
            self.raise_()
