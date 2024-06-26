import customtkinter as ctk
import subprocess
import os

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")
app = ctk.CTk()
app.geometry('600x400')
app.title('Админ панелька by Meyson')
tg, ds = None, None


def tgbut():
    global tg  # Указываем, что будем использовать глобальную переменную tg
    tg = toggle_script(tg, "Bots/TelegramBot.py")  # Возвращаем новое значение tg из функции


def toggle_script(bot, file_name):
    if bot is None:
        if os.path.exists("stop_bot.flag"):
            os.remove("stop_bot.flag")
        bot = subprocess.Popen(['start', 'python', file_name], shell=True)
        print(f'Скрипт {file_name} успешно выполнен')
        switch_mode(file_name, 'on')
    else:
        with open("stop_bot.flag", "w") as flag_file:
            flag_file.write("stop")
        bot.terminate()
        bot = None
        switch_mode(file_name, 'off')
    return bot  # Возвращаем измененное значение bot (либо новый процесс, либо None)


def switch_mode(bot, status):
    if bot == 'TelegramBot.py':
        if status == 'on':
            TGbot.configure(text='Выключить телеграмм бота', fg_color='red')
        else:
            TGbot.configure(text='Включить телеграмм бота', fg_color='green')


TGbot = ctk.CTkButton(app, text='Включить телеграмм бота', command=tgbut)

TGbot.grid(row=0, column=0)

app.mainloop()
