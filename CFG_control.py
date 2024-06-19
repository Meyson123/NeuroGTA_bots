import io
import os
import subprocess

base_dir = os.path.dirname(__file__)

if input('Нейропряны или Гта? (Циферку выбери)\n'
         '1) Нейропряны\n'
         '2) Гта\n') == '1':
    with io.open('myConfig.py','w+',encoding='utf-8') as file, io.open('configs/NeuroPryaniky.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = os.path.join(base_dir, 'configs', 'PromptPryaniky.py')
else:
    with io.open('myConfig.py','w',encoding='utf-8') as file, io.open('configs/NeuroGTA.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
    propmt_to_run = os.path.join(base_dir, 'configs', 'PromptGTA.py')
print('Конфиг успешно изменен')

try:
    subprocess.run(['python', propmt_to_run], check=True)
    print(f'Скрипт {propmt_to_run} успешно выполнен')
except subprocess.CalledProcessError as e:
    print(f'Ошибка при выполнении скрипта {propmt_to_run}: {e}')
