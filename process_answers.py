import json
from sentence_transformers import SentenceTransformer

'''преобразования ответов в векторный вид'''

input_json = json.loads(open(r'data/answers.json',
                             'r', encoding='utf8').read())
output_path = r'data/formatted.json'

'''Загрузка уже заранее обученной модели - https://www.sbert.net/docs/pretrained_models.html'''

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
output_json = {}

for item in input_json:
    embedding = model.encode(item).tolist()  # Векторизация текста
    output_json[item] = {}
    output_json[item]['value'] = input_json[item]  # Сохранение размеченного значения
    output_json[item]['embedding'] = embedding  # Векторное представление

open(output_path, 'w', encoding='utf8').write(json.dumps(output_json, indent=4, ensure_ascii=False))