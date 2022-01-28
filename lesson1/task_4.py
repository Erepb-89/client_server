"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
word_1 = 'разработка'
word_2 = 'администрирование'
word_3 = 'protocol'
word_4 = 'standard'

word_list = [word_1, word_2, word_3, word_4]
new_list = []

for item in word_list:
    byte_s = item.encode("utf-8")
    print(byte_s)
    new_list.append(byte_s)

print("-"*30)

for item in new_list:
    print(item.decode("utf-8"))
