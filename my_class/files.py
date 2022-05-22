import os  # операции с файлами
import sys  # аргументы командной строки
import shutil  # для удаления файлов
import time
from PyQt5.QtCore import QFileInfo, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt


class ScanThread(QThread):
    mysignal = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.path = ''
        self.files_list = []
        self.folder_list = []
        self.available_extensions = ('.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                                     '.xpm', '.jpg', '.jpeg', '.png', '.gif'
                                     )

    def run(self):
        cur_time = time.time()
        for dirpath, dirnames, files in os.walk(self.path):
            if len(files) > 0:
                if ('___Selected' not in dirpath) and ('___Deleted' not in dirpath):
                    count = 0
                    for name in files:
                        if os.path.splitext(name)[1].lower() in self.available_extensions:
                            self.files_list.append(os.path.join(os.path.abspath(dirpath), name))
                            count += 1
                    if count > 0:
                        level = dirpath.replace(self.path, '').count(os.sep)
                        self.folder_list.append((os.path.abspath(dirpath), os.path.basename(dirpath), level, count))
            if time.time() - cur_time > 1.0:
                cur_time = time.time()
                self.mysignal.emit(self.files_list, self.folder_list)
        self.mysignal.emit(self.files_list, self.folder_list)


class Files:
    """
    Этот класс создаёт и обновляет список файлов
    """

    def __init__(self):
        self.root_path = ''
        self.files_list = []
        self.folder_list = []
        self.current_folder = ''
        self.current_image = ''
        self.last_image = ''
        self.trash_path = ''
        self.select_path = ''
        self.current_index = 0

    @property
    def path(self):
        return self.root_path

    @path.setter
    def path(self, path):
        if isinstance(path, str):
            self.root_path = path
            self.current_folder = os.path.abspath(path)
            self.current_image = ''
            self.trash_path = os.path.join(self.current_folder, '___Deleted')
            self.select_path = os.path.join(self.current_folder, '___Selected')
            self.files_list = []
            self.folder_list = []

    def file_size(self):
        """
        Возвращает удобочитаемый размер файла
        """
        try:
            file = QFileInfo(self.current_image)
            size = file.size()
        except FileNotFoundError:
            size = 0
        if size < 1024:
            return str(size), 'байт'
        elif 1024 <= size < 1048576:
            return str(round(size / 1024, 1)), 'Кб'
        else:
            return str(round(size / 1048576, 1)), 'Мб'

    def move_one_file(self, destination: str):
        """
        Перемещение одного файла в папку назначения
        :param destination: путь к каталогу назначения
        :return: None
        """
        # Если каталог назначения не существует то создаем его
        if os.path.isdir(destination) is False:
            try:
                os.mkdir(destination)
            except (FileExistsError, PermissionError):
                print('Не удалось сооздать каталог для выделяемых изображений')
        # Генерация пути для перемещаемого файла с учетом возможного повторения имени
        i = 0
        destination_new = os.path.join(destination, os.path.basename(self.current_image))
        path, ext = os.path.splitext(destination_new)
        while os.path.isfile(destination_new):
            i += 1
            new_path = path + f'_{i}'
            destination_new = new_path + ext
        # Перемещение файла в каталог назначения
        try:
            shutil.move(self.current_image, destination_new)
        except (FileExistsError, PermissionError):
            shutil.copy(self.current_image, destination_new)
        # Удаление перемещенного файла из списка изображений
        self.files_list.remove(self.current_image)
        # Смещение текущего индекса при удалении последнего в списке файла
        if self.current_index > len(self.files_list) - 1:
            self.current_index -= 1
        # Выход если файлы в списке изображений закончились
        if len(self.files_list) == 0:
            print('изображений в папке больше нет')
            sys.exit(0)

        self.current_image = self.files_list[self.current_index]

    def move_files(self, destination: str):
        """
        Перемещение всех файлов из каталога, за исключением подкаталогов
        :param destination: каталог назначения в который перемещается исходный каталог
        :return: None
        """
        # поиск первого изображения в текущем каталоге
        current_dir = os.path.dirname(self.current_image)
        while os.path.dirname(self.files_list[self.current_index]) == current_dir:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = 0
                break
        if self.current_index > 0:
            self.current_index += 1
        # Создание каталога назначения если он еще не создан
        if os.path.isdir(destination) is False:
            try:
                os.mkdir(destination)
            except (FileExistsError, PermissionError):
                print('Не удалось сооздать каталог для выделяемых изображений')
        # Путь к новому каталогу в каталоге назначения
        name_dir = os.path.basename(current_dir)
        destination_path = os.path.join(destination, name_dir)
        # Изменение названия каталога в случае его существования на диске
        i = 0
        while os.path.isdir(destination_path):
            i += 1
            destination_path = destination_path + f'_{i}'
        # Пытаемся создать каталог
        try:
            os.mkdir(destination_path)
        except (FileExistsError, PermissionError):
            print(f'Не удалось сооздать каталог {destination_path} для перемещаемых изображений')
        # Перемещаем все изображения из текущей папки в новый каталог
        file_path = self.files_list[self.current_index]
        while os.path.dirname(file_path) == current_dir:
            try:
                shutil.move(file_path, destination_path)
            except (FileExistsError, PermissionError):
                shutil.copy(file_path, destination_path)
            self.files_list.remove(file_path)
            if self.current_index == len(self.files_list):
                self.current_index -= 1
            if self.current_index >= 0:
                file_path = self.files_list[self.current_index]
            else:
                file_path = ''
        # Корректируем количество элементов в списке файлов
        # При отсутствии вложенных папок пробуем удалить исходный каталог
        for _, dirs, _ in os.walk(current_dir):
            break
        if len(dirs) == 0:
            try:
                shutil.rmtree(current_dir)
            except (FileExistsError, PermissionError):
                print(f'Невозможно удалить каталог - {current_dir}')
        # Выходим если список с изображениями пуст
        if len(self.files_list) == 0:
            print('изображений в папке больше нет')
            sys.exit(0)
        # Назначаем новое текущее изображение
        self.current_image = self.files_list[self.current_index]

    def next_image(self):
        """
        Установка следующего в списке изображения
        """
        # если списко с изображениями пуст -> выход
        if len(self.files_list) == 0:
            print('Изображений в указанном каталоге нет')
            sys.exit(0)
        else:
            if self.current_index <= len(self.files_list) - 2:
                self.current_index += 1
                self.current_image = self.files_list[self.current_index]
            else:
                return

    def next_dir(self):
        """
        Перескакивает на начало следующего подкаталога с изображениями, или же в конец текущей папки
        :return:
        """
        current_dir = os.path.split(self.current_image)[0]
        while current_dir == os.path.split(self.files_list[self.current_index])[0] and \
            self.current_index < len(self.files_list):
            self.current_index += 1
            if self.current_index == len(self.files_list):
                self.current_index = len(self.files_list) - 1
                break
        self.current_image = self.files_list[self.current_index]

    def previous_image(self):
        """
        Установка предыдующего в списке изображения
        """
        # если список с изображениями пуст -> выход
        if len(self.files_list) == 0:
            print('Изображений в указанном каталоге нет')
            sys.exit(0)
        else:
            if self.current_index > 0:
                self.current_index -= 1
                self.current_image = self.files_list[self.current_index]
            else:
                return

    def previous_dir(self):
        """
        Перескакивает на предыдущий каталог с изображениями, или же в начало текущей папки
        :return:
        """
        current_dir = os.path.dirname(self.current_image)
        # поиск конца предыдущего каталога
        while current_dir == os.path.dirname(self.files_list[self.current_index]):
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = 0
                break

        # перемещение на начало предыдущего каталога
        if self.current_index > 0:
            current_dir = os.path.dirname(self.files_list[self.current_index])
            while current_dir == os.path.dirname(self.files_list[self.current_index]):
                self.current_index -= 1
                if self.current_index < 0:
                    self.current_index = 0
                    break
        self.current_image = self.files_list[self.current_index]

    def delete_image(self):
        """
        Отправляет изображение в папку Deleted
        """
        self.move_one_file(self.trash_path)

    def delete_dir(self):
        """
        Удаление каталога текущего изображения
        :return:
        """
        self.move_files(destination=self.trash_path)

    def move_image(self):
        """
        Отправляет указанную картинку в папку Selected
        """
        self.move_one_file(self.select_path)

    def move_dir(self):
        """
        Перемещение каталога текущего изображения в избранное
        :return:
        """
        self.move_files(destination=self.select_path)
