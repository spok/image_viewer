import os  # операции с файлами
import sys  # аргументы командной строки
import shutil  # для удаления файлов
from PyQt5.QtCore import QFileInfo


class Files:
    """
    Этот класс создаёт и обновляет список файлов
    """

    def __init__(self):
        self.files_list = []
        self.current_folder = ''
        self.current_image = ''
        self.last_image = ''
        self.trash_path = ''
        self.select_path = ''
        self.current_index = 0
        self.count_files = 0
        self.available_extensions = ('.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                                     '.xpm', '.jpg', '.jpeg', '.png', '.gif'
                                     )
        self.folder_list = dict()

    def scan_folder(self, path):
        """
        создаёт список изобр. папки -> self.files
        """
        self.current_folder = os.path.abspath(path)
        self.current_image = ''
        self.trash_path = os.path.join(self.current_folder, '___Deleted')
        self.select_path = os.path.join(self.current_folder, '___Selected')
        self.files_list = []  # очистка списка изображений
        self.folder_list = dict()
        try:
            for dirpath, dirnames, files in os.walk(path):
                subfolder = dirnames[:]
                if len(files) > 0:
                    if ('___Selected' not in dirpath) and ('___Deleted' not in dirpath):
                        count = 0
                        for name in files:
                            if os.path.splitext(name)[1].lower() in self.available_extensions:
                                self.files_list.append(os.path.join(os.path.abspath(dirpath), name))
                                count += 1
                        if count > 0:
                            level = dirpath.replace(path, '').count(os.sep)
                            self.folder_list[dirpath] = [os.path.basename(dirpath), level, count]
            self.current_image = self.files_list[0]
            self.current_index = 0
            self.count_files = len(self.files_list)
        except FileNotFoundError:
            print('Ошибка с открытием файлов')
            sys.exit(0)

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

    def next_image(self):
        """
        Установка следующего в списке изображения
        """
        # если списко с изображениями пуст -> выход
        if self.count_files == 0:
            print('Изображений в указанном каталоге нет')
            sys.exit(0)
        else:
            if self.current_index <= self.count_files - 2:
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
            self.current_index < self.count_files:
            self.current_index += 1
            if self.current_index == self.count_files:
                self.current_index = self.count_files - 1
                break
        self.current_image = self.files_list[self.current_index]

    def previous_image(self):
        """
        Установка предыдующего в списке изображения
        """
        # если список с изображениями пуст -> выход
        if self.count_files == 0:
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
        if os.path.isdir(self.trash_path) is False:
            try:
                os.mkdir(self.trash_path)
            except (FileExistsError, PermissionError):
                print('Не удалось сооздать каталог для удаляемых изображений')

        # проверка на существование файла с таким же имененем
        destination = os.path.join(self.trash_path, os.path.split(self.current_image)[1])
        i = 0
        path, ext = os.path.splitext(destination)
        while os.path.isfile(destination):
            i += 1
            new_path = path + f'_{i}'
            destination = new_path + ext
        try:
            shutil.move(self.current_image, destination)
        except (FileExistsError, PermissionError):
            shutil.copy(self.current_image, destination)
            print(f'не удалось переместить файл - {self.current_image}')
        self.files_list.remove(self.current_image)

        if self.count_files == 0:
            print('изображений в папке больше нет')
            sys.exit(0)
        else:
            if self.current_index == self.count_files - 1:
                self.current_index -= 1
            self.count_files = len(self.files_list)
            self.current_image = self.files_list[self.current_index]

    def delete_dir(self):
        """
        Удаление каталога текущего изображения
        :return:
        """
        # возврат к первому изображению в текущем каталоге
        current_dir = os.path.dirname(self.current_image)
        while os.path.dirname(self.files_list[self.current_index]) == current_dir:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = 0
                break
        if self.current_index > 0:
            self.current_index += 1

        # Создание каталога в папке Deleted
        destination_path = os.path.basename(os.path.dirname(self.current_image))
        destination_path = os.path.join(self.trash_path, destination_path)
        if os.path.isdir(destination_path) is False:
            try:
                os.mkdir(destination_path)
            except (FileExistsError, PermissionError):
                print(f'Не удалось сооздать каталог {destination_path} для удаляемых изображений')
        # удаление всех изображений текущей папки из списка
        file_path = self.files_list[self.current_index]
        while os.path.dirname(file_path) == current_dir:
            self.files_list.remove(file_path)
            if self.current_index == self.count_files - 1:
                self.current_index -= 1
            file_path = self.files_list[self.current_index]
        # Удаление текущего каталога
        try:
            shutil.move(current_dir, destination_path)
        except (FileExistsError, PermissionError) as e:
            print("Error: %s : %s" % (current_dir, e.strerror))
        self.count_files = len(self.files_list)

        if self.count_files == 0:
            print('изображений в папке больше нет')
            sys.exit(0)

        self.current_image = self.files_list[self.current_index]

    def move_image(self):
        """
        Отправляет указанную картинку в папку Selected
        """
        if os.path.isdir(self.select_path) is False:
            try:
                os.mkdir(self.select_path)
            except (FileExistsError, PermissionError):
                print('Не удалось сооздать каталог для выделяемых изображений')
        if os.path.isdir(self.select_path):
            # Генерация пути для перемещаемого файла
            destination = os.path.join(self.select_path, os.path.split(self.current_image)[1])
            i = 0
            path, ext = os.path.splitext(destination)
            while os.path.isfile(destination):
                i += 1
                new_path = path + f'_{i}'
                destination = new_path + ext
            # Перемещение файла в каталог
            try:
                shutil.move(self.current_image, destination)
                self.files_list.remove(self.current_image)
            except (FileExistsError, PermissionError):
                shutil.copy(self.current_image, destination)
                self.files_list.remove(self.current_image)
            self.count_files = len(self.files_list)

            if self.current_index > self.count_files - 1:
                self.current_index = self.count_files - 1

            if self.count_files == 0:
                print('изображений в папке больше нет')
                sys.exit(0)

            self.current_image = self.files_list[self.current_index]

    def move_dir(self):
        """
        Перемещение каталога текущего изображения в избранное
        :return:
        """
        if os.path.isdir(self.select_path) is False:
            try:
                os.mkdir(self.select_path)
            except (FileExistsError, PermissionError):
                print('Не удалось сооздать каталог для выделяемых изображений')
        if os.path.isdir(self.select_path):
            # Создание каталога в папке Selected
            destination_path = os.path.basename(os.path.dirname(self.current_image))
            destination_path = os.path.join(self.select_path, destination_path)
            if os.path.isdir(destination_path) is False:
                try:
                    os.mkdir(destination_path)
                except (FileExistsError, PermissionError):
                    print(f'Не удалось сооздать каталог {destination_path} для перемещаемых изображений')

            # возврат к первому изображению в текущем каталоге
            current_dir = os.path.dirname(self.current_image)
            while os.path.dirname(self.files_list[self.current_index]) == current_dir:
                self.current_index -= 1
                if self.current_index < 0:
                    self.current_index = 0
                    break
            if self.current_index > 0:
                self.current_index += 1

            # перемещение всех изображений из текущей папки
            file_path = self.files_list[self.current_index]
            while os.path.dirname(file_path) == current_dir:
                try:
                    shutil.move(file_path, destination_path)
                except (FileExistsError, PermissionError):
                    shutil.copy(file_path, destination_path)
                self.files_list.remove(file_path)
                if self.current_index == len(self.files_list):
                    self.current_index -= 1
                file_path = self.files_list[self.current_index]
            self.count_files = len(self.files_list)

            # удаление текущей папки
            try:
                shutil.rmtree(current_dir)
            except (FileExistsError, PermissionError):
                print(f'Невозможно удалить каталог - {current_dir}')

            if self.count_files == 0:
                print('изображений в папке больше нет')
                sys.exit(0)

            self.current_image = self.files_list[self.current_index]
