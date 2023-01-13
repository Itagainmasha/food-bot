import json
from sentence_transformers import SentenceTransformer, util

'''
Модуль для преобразования (интерпретации) текста (ответов пользователя) в нормализованные значения
'''

model = None
'''Загрузка векторизованных данных см. process_answers.py'''
obj = json.loads(
    open(r'data/formatted.json', 'r', encoding='utf8').read())


def text_to_rating(input_text):  # На входе принимаем строку, на выходе получаем значение от -1 до +1
    global model
    if model is None:  # Загружаем модель, если не загружена
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    input_embedding = model.encode(input_text)  # Векторизация входного текста
    max_sim = 0  # Максимальное сходство
    word = ''  # Максимально схожий ответ
    for item in obj:  # Поиск самого семантически близкого ответа
        embedding = obj[item]['embedding']  # Уже вычисленный вектор ответа
        '''Вычисление косинусного сходства между двумя векторами'''
        cosine_scores = util.cos_sim(input_embedding, embedding).numpy()[0][0]
        if max_sim < cosine_scores:  # Если текущий ответ подходит по смыслу чем предыдущий обновляем данные
            max_sim = cosine_scores
            word = item
    #print(word, max_sim, obj[word]['value'])
    # После нахождения самого близкого по семантическому смыслу ответа возвращаем нормализованное значение
    return obj[word]['value']
