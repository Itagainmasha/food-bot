from enum import auto, Enum

import telebot
from telebot import types
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

import core
import text_processor

API_TOKEN = '5935028082:AAGDuCCAbYjS1WcT9jp-YeJlEJ8ZZSt8vtc'  #токен бота

'''
Описание решения
Суть заключается в сборе ответов на типизированные вопросы, которые касаются характеристик того
или иного блюда. После сбора ответов пользователя они преобразуются в семантически-значимые
вектора с помощью фреймворка sbert, далее для интерпретации векторов в значения оценки используется
вычисление косинусного сходства между размеченными ответами и пользовательскими. Оценки можно
интерпретировать как шкалу от -1 до 1, от 0 до 1 или от 1 до 10 - без разницы. Для интерпретации
ответов пользователя можно использовать оценку тональности, но это даёт меньшую точность без 
использования специально обученных моделей. После того, как мы узнали насколько пользователь 
отдаёт предпочтения блюдам с теми или иными характеристиками выполняем поиск среди известного списка
блюд. Поиск выполняется так же за счёт вычисления косинусного сходства между двумя векторами: 
характеристики блюда и предпочтения пользователя. Таким образом мы можем понять с какой вероятностью
блюдо может понравиться пользователю. После вычисления этой оценки отправляем пользователю эти данные.  
'''

state_storage = StateMemoryStorage()  # хранилище, чтобы сохранять состояния машины состояний
bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)

user_dict = {}  # множество отношений пользователь -> предпочтения

'''
Класс, с использованием которого обрабатываются предпочтения
Острота spiciness
Жаренное fried
Варёное boiled
Время приготовления time
Сытность satiety
Насыщенность saturation
Солёность salinity
Суховатость dryness
'''


class User:
    def __init__(self):
        self.spiciness = None
        self.fried = None
        self.boiled = None
        self.time = None
        self.satiety = None
        self.saturation = None
        self.salinity = None
        self.sweetness = None
        self.dryness = None

    def get_interpreted_values(self):  # метод, возвращающий интерпретированные значения ответов пользователя
        out = {}
        for attribute, value in self.__dict__.items():  # выполняем для каждого поля класса
            out[attribute] = text_processor.text_to_rating(value)  # преобразуем текст в значения от -1 до +1
        return out

    def __str__(self):  # аналог toString
        out = ''
        for attribute, value in self.__dict__.items():
            out += f"{attribute, '=', value} "
        return out


class States(StatesGroup):  # Машина состояний
    spiciness = auto()
    fried = auto()
    boiled = auto()
    time = auto()
    satiety = auto()
    saturation = auto()
    salinity = auto()
    sweetness = auto()
    dryness = auto()

# Отношение состояние -> вопрос
questions = {
    States.spiciness: 'Любишь острую пищу?',
    States.fried: 'Любишь жареную пищу?',
    States.boiled: 'Любишь варёную пищу?',
    States.time: 'Любишь пищу быстрого приготовления?',
    States.satiety: 'Любишь сытную пищу?',
    States.saturation: 'Любишь насыщенную пищу?',
    States.salinity: 'Любишь солёную пищу?',
    States.sweetness: 'Любишь сладкую пищу?',
    States.dryness: 'Любишь сухую пищу?',
}


def get_state_message(state: States):  # получение вопроса по состоянию
    return questions[state]


@bot.message_handler(commands=['start'])  # обработка команды /start
def send_welcome(message):
    print(message.chat.id)
    bot.reply_to(message, """\
Привет!
Я по твоим предпочтениям могу подсказать блюда, которые тебе будут по вкусу!
""")
    bot.set_state(message.chat.id, States.spiciness)  # Задаём состояние
    bot.send_message(message.chat.id, get_state_message(bot.get_state(message.chat.id)))  # Задаём вопрос
    user_dict[message.chat.id] = User()  # Присваиваем каждому пользователю класс


@bot.message_handler(state="*")  # Хендлер, обрабатывающий любые состояния
def cancel(message):
    #bot.send_message(message.chat.id, text_processor.text_to_rating(message.text))
    if bot.get_state(message.chat.id) == States.spiciness:  # Если состояние текущего пользователя - ожидание ответа
        # на вопрос "Любишь острую пищу?"
        user_dict[message.chat.id].spiciness = message.text  # Записываем ответ
        bot.set_state(message.chat.id, States.fried)  # Переход в следующие состояние
        bot.send_message(message.chat.id,
                         get_state_message(bot.get_state(message.from_user.id)))  # Отправляем следующий вопрос
        return
    '''Дальше проходимся по состояниям, попутно запоминая ответы пользователя'''
    if bot.get_state(message.chat.id) == States.fried:
        user_dict[message.chat.id].fried = message.text
        bot.set_state(message.chat.id, States.boiled)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.boiled:
        user_dict[message.chat.id].boiled = message.text
        bot.set_state(message.chat.id, States.time)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.time:
        user_dict[message.chat.id].time = message.text
        bot.set_state(message.chat.id, States.satiety)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.satiety:
        user_dict[message.chat.id].satiety = message.text
        bot.set_state(message.chat.id, States.saturation)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.saturation:
        user_dict[message.chat.id].saturation = message.text
        bot.set_state(message.chat.id, States.salinity)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.salinity:
        user_dict[message.chat.id].salinity = message.text
        bot.set_state(message.chat.id, States.sweetness)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.sweetness:
        user_dict[message.chat.id].sweetness = message.text
        bot.set_state(message.chat.id, States.dryness)
        bot.send_message(message.chat.id, get_state_message(bot.get_state(message.from_user.id)))
        return
    if bot.get_state(message.chat.id) == States.dryness:
        user_dict[message.chat.id].dryness = message.text
        bot.set_state(message.chat.id, None)  # На последнем вопросе выходим из машины состояний
        bot.send_message(message.chat.id, 'Сейчас сделаю тебе несколько предложений...')
        interpreted_values = user_dict[message.chat.id].get_interpreted_values()  # Преобразуем текст в оценку
        # bot.send_message(message.chat.id, str(interpreted_values))
        compilation = core.get_compilation(interpreted_values)  # Передаём вектор предпочтений пользователя в генератор
        compilation = compilation[:2]  # Оставляем первые два полученных блюда
        score, _ = compilation[0]
        if score < 0.2:
            bot.send_message(message.chat.id, 'Для таких вкусов у меня нет предложений')
            compilation = []
        else:
            bot.send_message(message.chat.id, 'Думаю тебе понравятся эти блюда')
        print(compilation)
        for item in compilation:  # Цикл по отправляемым блюдам
            score, dish = item
            caption = f"Даю {round(score*100,1)}%, что тебе понравится {dish['title']}"
            bot.send_photo(message.chat.id,
                           photo=dish['image'],
                           caption=caption)
        bot.send_message(message.chat.id, 'Ещё разок? /start')
        return


bot.enable_save_next_step_handlers(delay=2)
bot.add_custom_filter(custom_filters.StateFilter(bot))  # Регистрация обработчиков машины состояний
bot.load_next_step_handlers()
print(bot.get_me())  # Вывод текущего бота
bot.infinity_polling()  # Запуск бота
