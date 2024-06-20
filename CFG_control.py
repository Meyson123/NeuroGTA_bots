import io
import subprocess
ai = int(input( 'Выбери конфиг (Циферку выбери)\n'
                '1) Нейропряны\n'
                '2) Гта\n'
                '3) Колаб\n'
                '4) Ролик\n' ))
if  ai == 1:
    with io.open('myConfig.py','w+',encoding='utf-8') as file, io.open('configs/NeuroPryaniky.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptPryaniky.py'
elif ai == 2:
    with io.open('myConfig.py','w',encoding='utf-8') as file, io.open('configs/NeuroGTA.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptGTA.py'
elif ai == 3:
    with io.open('myConfig.py','w',encoding='utf-8') as file, io.open('configs/NeuroGTA.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptColab.py'
elif ai == 4:
    with io.open('myConfig.py','w',encoding='utf-8') as file, io.open('configs/NeuroGTA.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = 'configs/PromptVideo.py'
else: print('Ps. Нужно отправить необходимую цифорку')
print('Конфиг успешно изменен')

try:
    subprocess.run(['python', propmt_to_run], check=True)
    print(f'Скрипт {propmt_to_run} успешно выполнен')
except subprocess.CalledProcessError as e:
    print(f'Ошибка при выполнении скрипта {propmt_to_run}: {e}')
