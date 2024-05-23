import aiohttp
import asyncio
import sys
import msvcrt

# Асинхронная функция для получения контента по URL
async def fetch_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            buffer = ''
            output_lines = 0

            while True:
                # Чтение данных порциями по 1024 байта
                chunk = await response.content.read(1024)
                if not chunk:
                    break

                buffer += chunk.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    print(line)
                    output_lines += 1
                    if output_lines >= 25:
                        print("Press space to scroll down.")
                        output_lines = 0
                        while True:
                            if msvcrt.kbhit() and msvcrt.getch() == b' ':
                                break

# Основная функция
def main():
    # Проверка наличия аргумента (URL)
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(1)

    url = sys.argv[1]
    # Запуск асинхронной функции
    asyncio.run(fetch_content(url))

# Проверка, что скрипт выполняется напрямую, а не импортируется
if __name__ == "__main__":
    main()

# Запуск: python 29.py http://example.com
