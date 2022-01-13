"""
Задание 2.

Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя!!! методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

Подсказки:
--- b'class' - используйте маркировку b''
--- используйте списки и циклы, не дублируйте функции
"""

bytes_s_1 = b'class'
bytes_s_2 = b'function'
bytes_s_3 = b'method'

new_list = [bytes_s_1, bytes_s_2, bytes_s_3]
for item in new_list:
    print(item)
    print(type(item))
    print(len(item))
