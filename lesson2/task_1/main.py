"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv

files = ["info_1.txt", "info_2.txt", "info_3.txt"]


def get_data():
    main_data = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    result_list = []
    result_list.append(main_data)

    for num_file in range(len(files)):
        with open(files[num_file], 'r', encoding='utf-8') as f_n:
            for line in f_n:
                if (main_data[0] in line) or \
                        (main_data[1] in line) or \
                        (main_data[2] in line) or \
                        (main_data[3] in line):
                    header_line, result_line = line.split(":")[0], line.split(":")[1]
                    result_line = result_line.split("\n")[0]

                    elem = 0
                    while result_line[elem] == " ":
                        elem += 1
                    result = result_line[elem:]

                    if main_data[0] in header_line:
                        os_prod_list.append(result)
                    elif main_data[1] in header_line:
                        os_name_list.append(result)
                    elif main_data[2] in header_line:
                        os_code_list.append(result)
                    elif main_data[3] in header_line:
                        os_type_list.append(result)

        result_list.append([num_file + 1,
                            os_prod_list[num_file],
                            os_name_list[num_file],
                            os_code_list[num_file],
                            os_type_list[num_file]]
                           )
    return result_list


def write_to_csv(file):
    data = get_data()
    with open(file, "w", encoding="utf-8") as f_new:
        F_N_WRITER = csv.writer(f_new)
        for row in data:
            F_N_WRITER.writerow(row)


write_to_csv('data_report.csv')
