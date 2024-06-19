import io

if input('Нейропряны или Гта? (Циферку выбери)\n'
         '1) Нейропряны\n'
         '2) Гта\n') == '1':
    with io.open('myConfig.py','w+',encoding='utf-8') as file, io.open('configs/NeuroPryaniky.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
else:
    with io.open('myConfig.py','w',encoding='utf-8') as file, io.open('configs/NeuroGTA.txt','r',encoding='utf-8') as cfg_file:
        config = cfg_file.read()
        file.write(config)
print('Конфиг успешно изменен')
