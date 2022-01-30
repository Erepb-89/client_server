"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""
word_1 = 'attribute'
word_2 = 'класс'
word_3 = 'функция'
word_4 = 'type'

word_list = [word_1, word_2, word_3, word_4]
new_list = []

# вариант 1
for item in word_list:
    try:
        word_bytes = bytes(item, "ascii")
        print(word_bytes)
    except ValueError as e:
        print(f'Error: {e}')

# вариант 2
for item in word_list:
    try:
        word_bytes = eval(f"b'{item}'")
        print(word_bytes)
    except SyntaxError as e:
        print(f'Error: {e}')