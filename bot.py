import os
import urllib.request
import requests

from config import TOKEN, IDS
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from datetime import datetime
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re
import csv


STARTER_URL = 'https://g00gle3at5h1t.pro/go/?i='
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
toCsvArr = []

# инициализация машины состояний
class FSMGetUrls(StatesGroup):
    urls = State()

# клавиатуры и кнопки
btn_geturl = KeyboardButton('Добавить урлы в очередь на индексацию')
btn_log = KeyboardButton('Лог за сегодня')
btn_check = KeyboardButton('Проверить наличие урлов')

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
# kb.add(btn_geturl).add(btn_log)
kb.add(btn_geturl)
kb.row(btn_log, btn_check)

# кнопки для подтверждения отправки урлов
confirmKbrd = InlineKeyboardMarkup(row_width=2)
confirmBtn = InlineKeyboardButton(text='Подтвердить', callback_data='confirmUrl')
cancelBtn = InlineKeyboardButton(text='Отмена', callback_data='cancelUrl')
confirmKbrd.row(confirmBtn, cancelBtn)

# функция для обработки полученных урлов
def count_and_prettify(urls):
    urls = list(filter(None, re.split('\n|,| ', urls)))  # удаление символов пробела и переноса строки, а
    nums = 0                                                    # также пустых строк
    for i in urls:
        # добавляем стартовый домен + проверяем на наличие протоколов
        if 'https://' not in i:
            toCsvArr.append(STARTER_URL + 'https://' + i.replace('http://', ''))
        else:
            toCsvArr.append(STARTER_URL + i)
        nums += 1
    return nums


async def csvHandler(state, message : types.Message):
    async with state.proxy() as data:
        global toCsvArr
        nums = 0
        urls = data['urls']
        match urls:
            case 'Добавить урлы в очередь на индексацию':
                await message.reply('Необходимо отправить урлы!')
                await csvHandler(state)
            case 'Проверить наличие урлов':
                await message.reply('Необходимо отправить урлы!')
                await csvHandler(state)
            case 'Лог за сегодня':
                await message.reply('Необходимо отправить урлы!')
                await csvHandler(state)
            case _:
               nums = count_and_prettify(urls)
               # выводит ответ с колличеством обработанных урлов
               await message.reply(f'Хотите добавить {nums} урлов?', reply_markup=confirmKbrd)

#   Обработчик кнопки "Подтвердить"
@dp.callback_query_handler(text=['confirmUrl'])
async def confirmUrl(callback : types.CallbackQuery):
    user_name = callback.from_user.first_name
    await callback.answer('Действие подтверждено')
    # передаем урлы в csv файл
    for url in toCsvArr:
        url = url.strip('\r')
        with open('urls.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([url])
        file.close()

    now = datetime.now()
    if not os.path.exists('logs'):
        os.makedirs('logs')
    with open(f"logs/log_{now.day}-{now.month}-{now.year}.txt", "a") as file:
        file.write(f"****{now.hour}:{now.minute}:{now.second}****\n")
        file.write(f"Пользователь {user_name} добавил следующие урлы:\n")
        # file.write(str(toCsvArr) + '\n')
    toCsvArr.clear()
    await callback.message.answer('Урлы в обработке, дождитесь ответа...')
    await callback.message.edit_reply_markup(reply_markup=None)
    os.system("python3 main.py")
    with open('log.txt') as f:
        indexerLog = f.readlines()
        for l in indexerLog:
            await callback.message.answer(l)
    now = datetime.now()
    with open(f"logs/log_{now.day}-{now.month}-{now.year}.txt", "a") as file:
        file.write(f"****{now.hour}:{now.minute}:{now.second}****\n")
        file.write("Ответ от апи:\n")
        file.write(str(indexerLog) + '\n')
    f.close()


#   Обработчик кнопки "Отмена"
@dp.callback_query_handler(text=['cancelUrl'])
async def cancelUrl(callback : types.CallbackQuery):
    await callback.answer('Действие отменено', show_alert=True)
    toCsvArr.clear()
    await callback.message.delete()


# обработка входной точки (первое обращение)
@dp.message_handler(commands=['start'])
async def getStart(message : types.Message):
    if (message.from_user.id in IDS):
        try:
            await bot.send_message(message.from_user.id,
            'Добро пожаловать в бот индексатор! Выбирите ваше действие: ', reply_markup=kb)
        except:
            await message.reply('Вы не добавили бота в лс, \n Перейдите по ссылке: https://t.me/googleindexbot')
    else:
        await message.answer('Ошибка! Вы не являетесь зарагестрированным пользователем!')

# метод, получающий список урлов
@dp.message_handler(Text(equals='Добавить урлы в очередь на индексацию'))
async def getUrls(message : types.Message):
    if (message.from_user.id in IDS):
        try:
            await bot.send_message(message.from_user.id, 'Отправьте список урлов или файл в формате txt')
            await FSMGetUrls.urls.set()
        except:
            await message.reply('Вы не добавили бота в лс, \n Перейдите по ссылке: https://t.me/googleindexbot')
    else:
        await message.answer('Ошибка! Вы не являетесь зарагестрированным пользователем!')



# загрузка списка урлов в хранилище
@dp.message_handler(content_types=['text'], state=FSMGetUrls.urls)
async def setUrls(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['urls'] = message.text
    await csvHandler(state, message)
    await state.finish()


# Метод, читающий урлы с txt файла

async def convertTxtCsv(message):
    file_id = message.document['file_id']
    file_link = 'https://api.telegram.org/bot' + TOKEN + '/getFile?file_id=' + file_id
    file_request = requests.post(file_link)
    if file_request.status_code == 200:
        file_request = requests.post(file_link).json()
        file_path = file_request['result']['file_path']
        file_path = 'https://api.telegram.org/file/bot' + TOKEN + '/' + file_path
        data = urllib.request.urlopen(file_path)
        data_str = ""
        for line in data:
           data_str += line.decode("utf-8")
    else:
        await message.answer('Не удается соединиться с сервером')
    return data_str


@dp.message_handler(content_types=['document'], state=FSMGetUrls.urls)
async def setUrlsFromFile(message : types.Document, state: FSMContext):
    async with state.proxy() as data:
        data['urls'] = await convertTxtCsv(message)
    await csvHandler(state, message)
    await state.finish()


# метод, выводящий логи
async def get_log(message):
    now = datetime.now()
    try:
        await bot.send_document(chat_id=message.chat.id, document=open(f"logs/log_{now.day}-{now.month}-{now.year}.txt", 'rb'))
    except:
        await message.reply('Сегодня ничего еще не было добавлено в лог')

@dp.message_handler(Text(equals='Лог за сегодня'))
async def getLog(message : types.Message):
    if (message.from_user.id in IDS):
        try:
            await get_log(message)
        except:
            await message.reply('Вы не добавили бота в лс, \n Перейдите по ссылке: https://t.me/googleindexbot')
    else:
        await message.answer('Ошибка! Вы не являетесь зарагестрированным пользователем!')


# Кнопка для проверки наличия неиндексирцуемых урлов
@dp.message_handler(Text(equals='Проверить наличие урлов'))
async def checkUrlsInScope(message : types.Message):
    if (message.from_user.id in IDS):
        try:
            try:
                with open('urls.csv') as f:
                    urls = f.readlines()
                    if str(urls) == '[]':
                        await message.answer('У вас нет незаиндексированных урлов')
                    else:
                        await message.answer('Эти урлы не были отправлены в индекс')
                        await bot.send_document(chat_id=message.chat.id, document=open("urls.csv", 'rb'))
            except:
                await message.reply('Файл csv еще не создан! Попробуйте добавить урлы на индексацию')

        except:
            await message.reply('Вы не добавили бота в лс, \n Перейдите по ссылке: https://t.me/googleindexbot')
    else:
        await message.answer('Ошибка! Вы не являетесь зарагестрированным пользователем!')


# дефолтный метод для всех прочих запросов
@dp.message_handler()
async def defaultHander(message : types.Message):
    await message.answer("Это не является командой бота, выбирите действие из списка", reply_markup=kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


