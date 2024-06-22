import io
import subprocess
import customtkinter as ctk

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


def Pryanik_mode():
    with io.open('myConfig.py', 'w+', encoding='utf-8') as file, io.open('configs/NeuroPryaniky.txt', 'r',
                                                                         encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptPryaniky.py'
    prompt_to_run(propmt_to_run)


def Gta_mode():
    with io.open('myConfig.py', 'w', encoding='utf-8') as file, io.open('configs/NeuroGTA.txt', 'r',
                                                                        encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptGTA.py'
    prompt_to_run(propmt_to_run)


def Colab_mode():
    with io.open('myConfig.py', 'w', encoding='utf-8') as file, io.open('configs/NeuroColab.txt', 'r',
                                                                        encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptColab.py'
    prompt_to_run(propmt_to_run)


def Video_mode():
    with io.open('myConfig.py', 'w', encoding='utf-8') as file, io.open('configs/NeuroGTA.txt', 'r',
                                                                        encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptVideo.py'
    prompt_to_run(propmt_to_run)


def prompt_to_run(propmt_to_run):
    try:
        subprocess.run(['python', propmt_to_run], check=True)
        print(f'Скрипт {propmt_to_run} успешно выполнен')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при выполнении скрипта {propmt_to_run}: {e}')


app = ctk.CTk()
app.geometry("240x240")

NeuroPry = ctk.CTkButton(master=app, text="ПРЯНИКИ", command=Pryanik_mode)
NeuroGta = ctk.CTkButton(master=app, text="ГТА", command=Gta_mode)
NeuroCol = ctk.CTkButton(master=app, text="КОЛАБ", command=Colab_mode)
NeuroRol = ctk.CTkButton(master=app, text="ВИДЕОРОЛИК", command=Video_mode)
Title = ctk.CTkLabel(master=app,text='Выбери нужный конфиг')

Title.grid(column = 0,row = 0)
NeuroPry.grid(column = 0,row = 1,ipadx=30, ipady=6, padx=27, pady=7)
NeuroGta.grid(column = 0,row = 2,ipadx=30, ipady=6, padx=27, pady=7)
NeuroCol.grid(column = 0,row = 3,ipadx=30, ipady=6, padx=27, pady=7)
NeuroRol.grid(column = 0,row = 4,ipadx=30, ipady=6, padx=27, pady=7)


app.mainloop()
