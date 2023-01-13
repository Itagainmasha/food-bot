import json
from sentence_transformers import util
import numpy as np

'''Загрузка всех описанных блюд'''
dishes_path = r'data/dishes.json'
dishes = json.loads(open(dishes_path, 'r', encoding='utf8').read())


def get_compilation(interpreted_values):  # Метод получения подборки блюд по нормализованному вектору
    '''
    interpreted_values = {'spiciness': 0.5, 'fried': -0.5,
                          'boiled': -0.5, 'time': 1, 'satiety': 1,
                          'saturation': 0.5, 'salinity': 1,
                          'sweetness': 1, 'dryness': 0.6}
    '''
    print(interpreted_values)
    '''Убираем ключи из словаря, оставляем значения'''
    input_vector = [interpreted_values[item] for item in interpreted_values]
    '''Преобразуем в массив с типом элементов float32 (нужно для случая с единицами в векторе)'''
    input_vector = np.array(input_vector, dtype=np.float32)
    '''Оставляем только ключи'''
    characteristics = [item for item in interpreted_values]
    print(input_vector)
    print(characteristics)
    out = []  # Результирующий массив подборки
    for item in dishes:  # Цикл по блюдам
        item_characteristics = item['characteristics']  # Размеченный массив характеристик блюда
        dish_vector = [item_characteristics[item] for item in characteristics]  # Преобразование в вектор
        print(input_vector, dish_vector)
        '''Вычисление косинусного сходства между вектором предпочтений пользователя и характеристиками блюда'''
        cosine_score = util.cos_sim(input_vector, dish_vector).numpy()[0][0]
        out.append([cosine_score, item])  # Добавляем в результат пару: сходство - блюдо
    out = sorted(out, key=lambda x: x[0], reverse=True)  # Сортируем по первому элементу - сходству
    return out
