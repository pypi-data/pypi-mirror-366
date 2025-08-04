from smb.SMBConnection import SMBConnection
import os

class DFSClient:
    def __init__(self, user, password, dfs_remote_name, dfs_domain):
        """
        Конструктор клиента для подключения к удалённой файловой системе через протокол SMB.
        
        Параметры:
        - user (str): Имя пользователя для аутентификации.
        - password (str): Пароль пользователя.
        - dfs_remote_name (str): Название удаленного сервера.
        - dfs_domain (str): Доменное имя или рабочая группа.
        """
        
        self.conn = SMBConnection(
            username=user,
            password=password,
            my_name='gpnconnect', # Наименование подключения
            remote_name=dfs_remote_name,
            domain=dfs_domain,
            use_ntlm_v2=True,      # Использовать NTLMv2 для авторизации
            is_direct_tcp=True     # Прямой TCP-подход для подключения
        )
        self.dfs_remote_name = dfs_remote_name
    
    def connect(self):
        """Подключение к удалённому серверу по порту 445"""
        self.conn.connect(self.dfs_remote_name, port=445)

    def write(self, dfs_folder_share, remote_file_path, local_file_path):
        """
        Запись локального файла на удаленный ресурс.
        
        Параметры:
        - dfs_folder_share (str): Удаленный ресурс, куда загружаем файлы.
        - remote_file_path (str): Путь к файлу на удалённом ресурсе.
        - local_file_path (str): Полный путь к локальному файлу.
        """
        with open(local_file_path, 'rb') as localfile:
            self.conn.storeFile(dfs_folder_share, remote_file_path, localfile)

    def read(self, dfs_folder_share, remote_file_path, local_file_path):
        """
        Чтение содержимого файла из удалённого ресурса.
        
        Параметры:
        - dfs_folder_share (str): Удаленный ресурс, откуда читаем файл.
        - remote_file_path (str): Путь к файлу на удалённом ресурсе.
        - local_file_path (str): Локальное расположение для сохранения прочитанного файла.
        """
        with open(local_file_path, 'wb') as localfile:
            self.conn.retrieveFile(dfs_folder_share, remote_file_path, localfile)

    def create_directory(self, dfs_folder_share, directory_path):
        """
        Создает директорию на удалённом сервере.
        
        Параметры:
        - dfs_folder_share (str): Удаленный ресурс, где создаётся директория.
        - directory_path (str): Путь к создаваемой директории.
        """
        try:
            self.conn.createDirectory(dfs_folder_share, directory_path)
        except Exception as e:
            print(f'Ошибка при создании директории {directory_path}: {e}')

    def list_files(self, dfs_folder_share, directory_path=''):
        """
        Возвращает список файлов и директорий в указанной папке на удалённом сервере.
        
        Параметры:
        - dfs_folder_share (str): Удаленный ресурс, где выполняется операция.
        - directory_path (str): Папка внутри ресурса (опционально).
        """
        
        base_path = f"/{dfs_folder_share}/{directory_path}".rstrip('/')
        result = []

        for entry in self.conn.listPath(dfs_folder_share, directory_path):
            if entry.filename not in ('.','..'):
                full_path = os.path.join(base_path, entry.filename)
                result.append(full_path)
        return result

    def list_smb_files(self, dfs_folder_share, directory_path=''):
        """
        Возвращает список файлов и директорий в указанной папке на удалённом сервере.
        
        Параметры:
        - dfs_folder_share (str): Общий ресурс (шина), где выполняется операция.
        - directory_path (str): Папка внутри шары (опционально).
        """
        return self.conn.listPath(dfs_folder_share, directory_path)

  

    def _recursive_read_folder(self, dfs_folder_share, remote_path, local_output_dir):
        """
        Рекурсивно читает и сохраняет все файлы и папки из удалённой папки.

        Параметры:
        - dfs_folder_share (str): Общий ресурс (шина), откуда считываются файлы.
        - remote_path (str): Текущая удалённая папка, включая вложенные.
        - local_output_dir (str): Локальная директория для сохранения файлов.
        """
        entries = self.list_smb_files(dfs_folder_share, remote_path)

        for entry in entries:
            # Игнорируем служебные записи '.' и '..'
            if entry.filename in ('.', '..'):
                continue

            # Формирование полного удалённого и локального путей
            full_remote_path = os.path.join(remote_path, entry.filename)
            local_path = os.path.join(local_output_dir, entry.filename)

            if entry.isDirectory:
                # Создание локальной папки и рекурсия для обработки вложенных элементов
                os.makedirs(local_path, exist_ok=True)
                self._recursive_read_folder(dfs_folder_share, full_remote_path, local_path)
            else:
                # Сохранение файла локально
                self.read(dfs_folder_share, full_remote_path, local_path)

    def read_folder(self, dfs_folder_share, remote_root_folder, local_output_dir):
        """
        Рекурсивно читает и сохраняет все файлы и папки из удалённой папки и её подпапок.
        """
        self._recursive_read_folder(dfs_folder_share, remote_root_folder, local_output_dir)