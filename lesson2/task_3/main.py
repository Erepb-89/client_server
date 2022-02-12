"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""
import yaml

items = ['computer',
         'printer',
         'keyboard',
         'mouse']

items_price = {'computer': u'200€-1000€',
               'printer': u'100€-300€',
               'keyboard': u'5€-50€',
               'mouse': u'4€-7€'}

data_to_yaml = {'items': items, 'items_price': items_price, 'items_quantity': 4}

with open('file.yaml', 'w', encoding='utf-8') as f_write:
    yaml.dump(data_to_yaml, f_write, default_flow_style=False, allow_unicode=True,
              sort_keys=True)  # sort_keys=True, т.к. в образце items_price отсортированы

with open('file.yaml', 'r', encoding='utf-8') as f_read:
    data_from_yaml = yaml.load(f_read, Loader=yaml.SafeLoader)
    print(data_from_yaml)

print('data_from_yaml == data_to_yaml: ', data_from_yaml == data_to_yaml)
