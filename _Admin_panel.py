import customtkinter as ctk
import os
import subprocess
button_width = 400  # Ширина кнопок
button_height = 50  # высота кнопок

#basedir = 'C:\\Users\Honor\Downloads\\'
basedir = 'N:\AI-Stream-Kit\Stream-Kit\\'


def tgbot():
    subprocess.Popen(['start', 'python', 'Bots/TelegramBot.py'], shell=True)
    subprocess.Popen(['start', 'python', 'Bots/TelegramSubscribeBot.py'], shell=True)
    print('Бот Телеграмм запущен')


def dsbot():
    subprocess.Popen(['start', 'python', 'Bots/DiscordBot.py'], shell=True)
    print('Бот Дискорд запущен')


def donbot():
    subprocess.Popen(['start', 'python', 'Bots/DonationBot.py'], shell=True)
    print('Бот для крутых(Донат) запущен')


def controller():
    os.system(f'cd / && cd {basedir} && start 4.Controller.bat')
    print('Контроллер запущен')


def RvcStart():
    os.system(f'cd / && cd {basedir} && start 1.RVC.bat')
    print('RVC запущен')


def RvcTTSStart():
    os.system(f'cd / && cd {basedir}  && start 2.RVCTTS.bat')
    print('RVC TTS запущен')


def RvcGateway():
    os.system(f'cd / && cd {basedir} && start 3.RVCGateway.bat')
    print('RVC GATE запущен')


def startBuild():
    os.startfile(r"N:\AI-Stream-Kit\AI_Gta\BUILDS\Vertical 5\AI_Gta.exe")
    print('Билд запущен')


def qcounter():
    os.system(f'cd / && cd {basedir} && start 8.StartQueueView.bat')
    #subprocess.Popen(['start', 'python', 'Bots/QueueDisplayBot.py'], shell=True)
    print('Бот счетчик тем запущен')


def cfgControl():
    subprocess.run(['python', 'CFG_control.py'])


class BotFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.TGbot = ctk.CTkButton(self, text='Включить телеграмм бота', command=tgbot, width=button_width,
                                   height=button_height)
        self.DSbot = ctk.CTkButton(self, text='Включить дискорд бота', command=dsbot, width=button_width,
                                   height=button_height)
        self.Dbot = ctk.CTkButton(self, text='Включить донат бота', command=donbot, width=button_width,
                                  height=button_height)

        self.TGbot.grid(row=0, column=0, padx=(10, 10), pady=(20, 10))
        self.DSbot.grid(row=1, column=0, padx=(10, 10), pady=(20, 10))
        self.Dbot.grid(row=2, column=0, padx=(10, 10), pady=(20, 10))


class RvcFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.RvcTTS = ctk.CTkButton(self, text='Запустить RvcTTS', command=RvcTTSStart, width=button_width,
                                    height=button_height)
        self.Rvcstart = ctk.CTkButton(self, text='Запустить Rvc', command=RvcStart, width=button_width,
                                      height=button_height)
        self.RvcGate = ctk.CTkButton(self, text='Запустить RvcGate', command=RvcGateway, width=button_width,
                                     height=button_height)
        self.Rvcstart.grid(row=0, column=0, padx=(10, 10), pady=(20, 10))
        self.RvcTTS.grid(row=1, column=0, padx=(10, 10), pady=(20, 10))
        self.RvcGate.grid(row=2, column=0, padx=(10, 10), pady=(20, 10))


class OtherFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        self.button_width = 200  # Ширина кнопок
        self.button_height = 40
        super().__init__(master, **kwargs)
        self.Controlbut = ctk.CTkButton(self, text='Запустить Контроллер', command=controller, width=self.button_width,
                                        height=self.button_height)
        self.CFG = ctk.CTkButton(self, text='Изменить конфиг', command=cfgControl, width=self.button_width,
                                 height=self.button_height)
        self.QCounter = ctk.CTkButton(self, text='Запустить QueueCounter.py', command=qcounter, width=self.button_width,
                                      height=self.button_height)
        self.Buildbut = ctk.CTkButton(self, text='Запустить билд', command=startBuild, width=self.button_width,
                                      height=self.button_height)
        self.CFG.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))
        self.QCounter.grid(row=0, column=1, padx=(10, 10), pady=(10, 10))
        self.Buildbut.grid(row=0, column=2, padx=(10, 10), pady=(10, 10))
        self.Controlbut.grid(row=0, column=3, padx=(10, 10), pady=(10, 10))


class AdminPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('940x400')
        self.title('Админ панелька by Meyson')
        self._set_appearance_mode('System')
        self.frame_bot = BotFrame(self)
        self.frame_rvc = RvcFrame(self)
        self.frame_other = OtherFrame(self)
        self.create_widgets()

    def create_widgets(self):
        self.frame_bot.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        self.frame_rvc.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.frame_other.grid(row=1, column=0, columnspan=2, padx=20, pady=20)
        # button_width = 200  # Ширина кнопок
        # button_height = 40  # высота кнопок
        #
        # # Фреймы
        #
        # # Виджеты
        # TGbot = ctk.CTkButton(self, text='Включить телеграмм бота', command=tgbot, width=button_width,
        #                       height=button_height)
        # DSbot = ctk.CTkButton(self, text='Включить дискорд бота', command=dsbot, width=button_width,
        #                       height=button_height)
        # CFG = ctk.CTkButton(self, text='Изменить конфиг', command=cfgControl, width=button_width,
        #                     height=button_height)
        # QCounter = ctk.CTkButton(self, text='Запустить QueueCounter.py', command=qcounter, width=button_width,
        #                          height=button_height)
        # Dbot = ctk.CTkButton(self, text='Включить Донат бота', command=donbot, width=button_width,
        #                      height=button_height)
        # Buildbut = ctk.CTkButton(self, text='Запустить билд', command=startBuild, width=button_width,
        #                          height=button_height)
        # RvcTTS = ctk.CTkButton(self, text='Запустить RvcTTS', command=RvcTTSStart, width=button_width,
        #                        height=button_height)
        # Rvcstart = ctk.CTkButton(self, text='Запустить Rvc', command=RvcStart, width=button_width,
        #                          height=button_height)
        # RvcGate = ctk.CTkButton(self, text='Запустить RvcGate', command=RvcGateway, width=button_width,
        #                         height=button_height)
        # Controlbut = ctk.CTkButton(self, text='Запустить Контроллер', command=controller, width=button_width,
        #                            height=button_height)
        #
        # # Отрисовка виджетов
        # TGbot.grid(row=0, column=0, padx=(20, 0), pady=(20, 10))
        # DSbot.grid(row=0, column=1, padx=(10, 0), pady=(20, 10))
        # Dbot.grid(row=0, column=2, padx=(10, 0), pady=(20, 10))
        # CFG.grid(row=1, column=0, padx=(20, 0), pady=(0, 10))
        # QCounter.grid(row=1, column=1, padx=(10, 0), pady=(0, 10))
        # Buildbut.grid(row=1, column=2, padx=(10, 0), pady=(0, 10))
        # RvcTTS.grid(row=2, column=1, padx=(10, 0), pady=(0, 10))
        # Rvcstart.grid(row=2, column=0, padx=(20, 0), pady=(0, 10))
        # RvcGate.grid(row=2, column=2, padx=(10, 0), pady=(0, 10))
        # Controlbut.grid(row=3, column=1, padx=(10, 0), pady=(0, 10))


if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
