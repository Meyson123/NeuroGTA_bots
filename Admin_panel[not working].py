import tkinter as tk
import subprocess
import asyncio

# Функция для запуска скрипта TelegramBot.py
async def start_bot():
    process = await asyncio.create_subprocess_exec('python', 'TelegramBot.py')
    await process.communicate()

# Функция для остановки скрипта TelegramBot.py
async def stop_bot():
    process.terminate()

# Функция, которая будет вызываться при нажатии кнопки
def toggle_bot():
    global bot_process
    if bot_process is None:
        bot_process = asyncio.ensure_future(start_bot(), loop=loop)
        start_stop_button.config(text="Stop Bot")
    else:
        asyncio.ensure_future(stop_bot(), loop=loop)
        bot_process = None
        start_stop_button.config(text="Start Bot")

# Создание графического интерфейса с кнопкой
root = tk.Tk()
start_stop_button = tk.Button(root, text="Start Bot", command=toggle_bot)
start_stop_button.pack()

bot_process = None

# Создание нового цикла событий asyncio
loop = asyncio.new_event_loop()

# Функция для запуска цикла событий tkinter и asyncio
def start_event_loop():
    loop.run_forever()

# Запуск циклов событий
root.after(0, start_event_loop)
root.mainloop()
