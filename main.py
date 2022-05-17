from youtube_transcript_api import YouTubeTranscriptApi
import random
import telebot
from telebot import types
import re
import io

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttest = types.KeyboardButton('Тесты')
butteop = types.KeyboardButton('Теория')
butsvaz = types.KeyboardButton('Связь')
markup.add(buttest, butteop, butsvaz)

butback = types.KeyboardButton('Назад в меню')

markuptests = types.ReplyKeyboardMarkup(resize_keyboard=True)
butsin = types.KeyboardButton('Тест на синонимы')
butfrazeolog = types.KeyboardButton('Тест на фразеологизмы')
butyoutube = types.KeyboardButton('Тест на видосы')
markuptests.add(butsin, butfrazeolog, butyoutube)
markuptests.add(butback)

markupback = types.ReplyKeyboardMarkup(resize_keyboard=True)
butbacktotest = types.KeyboardButton('Назад к тестам')
markupback.add(butbacktotest)

markupclear = types.ReplyKeyboardRemove()

bot_token = '5316685010:AAHx-Chtt6z3opo7Q_Mcru_3nwCrAoMVzU0'
bot = telebot.TeleBot(bot_token, parse_mode=None)

## -----------------------------
## TEXTS


help_text = "Помощь в использовании бота"


# TEXTS
# ------------------------------
# SUBS

end_symbols = ['!', '?', '.']
start_of_link = "https://www.youtube.com/watch?v="
hided_words = []


def get_subs_text(video_id):
    video_id = video_id[len(start_of_link):]
    try:
        subs_unformatted = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        subs_text = ""
        for i in subs_unformatted:
            subs_text += i.get('text')
        return subs_text

    except ValueError:
        return "Неверный формат ссылки"


def get_words_of_text(text):
    try:
        text = remove_symbols(text)
        words = text.split()
        return words
    except ValueError:
        return "Не удалось преобразовать текст в слова"


def is_letter(symbol):
    result = (ord('Z') >= ord(symbol) >= ord('A') or ord('a') <= ord(symbol) <= ord('z'))
    return result


def remove_symbols(text):
    for i in text:
        if not is_letter(i):
            text = text.replace(i, ' ')

    return text


def hide_random_word(text):
    text = remove_symbols(text)
    words = get_words_of_text(text)
    random_word = words[random.randint(0, len(words))]
    random_word = ' ' + random_word + ' '
    hided_words.append(random_word[1:-1])
    text = text.replace(random_word, ' {Пропуск} ')
    text = re.sub(r'\s+', ' ', text)
    return text


def reduce_manual_text(text):
    sents = []
    sent = ""
    for i in text:
        if i in end_symbols:
            sent += i
            sents.append(sent)
            sent = ""
        else:
            sent += i

    if len(sents) > 7:
        text = ""
        diap = random.randint(1, len(sents) - 6)
        for i in range(diap, diap + 6):
            text += sents[i]
        return text

    else:
        return text


def check_answer():
    return hided_words[-1]


def reduce_auto_text(text):
    words = get_words_of_text(text)
    reduced_text = ""
    diap = random.randint(1, len(words) - 170)
    for i in range(diap, diap + 170 - 1):
        reduced_text = reduced_text + words[i] + " "
    return reduced_text


def bot_send_texts(message):
    if message.text == "Назад к тестам":
        bot.send_message(message.chat.id, 'Вы в перешли к тестам', reply_markup=markuptests)
        return

    try:
        video_id = message.text
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id[len(start_of_link):])
        transcript = transcript_list.find_transcript(['en'])
        if transcript.is_generated:
            text = get_subs_text(video_id)
            if len(text) >= 1000:
                text = reduce_auto_text(text)
                print(text)
                holey_text = hide_random_word(text)
                bot.send_message(message.chat.id, "Внимание! Субтитры созданы автоматически!\nВозможны ошибки!\n\n" + holey_text)
                ms = bot.send_message(message.chat.id, "Пришли ответ")
                bot.register_next_step_handler(ms, bot_check_answer)
            else:
                print(text)
                holey_text = hide_random_word(text)
                bot.send_message(message.chat.id, "Внимание! Субтитры созданы автоматически!\nВозможны ошибки!\n\n" + holey_text)
                ms = bot.send_message(message.chat.id, "Пришли ответ")
                bot.register_next_step_handler(ms, bot_check_answer)

        else:
            text = reduce_manual_text(get_subs_text(video_id))
            print(text)
            holey_text = hide_random_word(text)
            bot.send_message(message.chat.id, holey_text)
            ms = bot.send_message(message.chat.id, "Пришли ответ")
            bot.register_next_step_handler(ms, bot_check_answer)

    except:
        ms = bot.send_message(message.chat.id, "Невозможно создать субтитры, либо неверный формат ссылки! Попробуйте еще раз")
        bot.register_next_step_handler(ms, bot_send_texts)


def bot_check_answer(message):
    if message.text == check_answer():
        ms = bot.send_message(message.chat.id,
                              'Все верно!\n\nОтправьте следующую ссылку, или введите: "Назад к тестам" ')
        bot.register_next_step_handler(ms, bot_send_texts)
    else:
        ms = bot.send_message(message.chat.id, "Неверно!\nПравильный ответ: " + check_answer() +
                         '\n\nОтправьте следующую ссылку, или введите: "Назад к тестам"')
        bot.register_next_step_handler(ms, bot_send_texts)


# SUBS
# ------------------------------------
# IDIOMS

lang = 0
f = io.open("Idioms.txt", mode="r", encoding="utf-8")
idioms_data = f.readlines()
f.close()
for i in range(len(idioms_data)):
    idioms_data[i] = idioms_data[i].replace('\n', '')

idioms = [] # eng 0, rus 1
for i in idioms_data:
    line = i.split(' - ')
    idioms.append(line)

idioms_amount = len(idioms)
idioms_memory = []

choose_lang_idioms = types.ReplyKeyboardMarkup(resize_keyboard=True)
eng_rus = types.KeyboardButton('Английский --> Русский')
rus_eng = types.KeyboardButton('Русский --> Английский')
choose_lang_idioms.add(eng_rus, rus_eng)
choose_lang_idioms.add(butbacktotest)


def idioms_test(message):
    global lang
    if message.text == "Назад к тестам":
        bot.send_message(message.chat.id, 'Вы перешли к тестам', reply_markup=markuptests)
        return

    if message.text == "Английский --> Русский":
        lang = 1
        ms = bot.send_message(message.chat.id, get_idiom(lang)[0], reply_markup=markupback)
        bot.register_next_step_handler(ms, check_idiom)

    elif message.text == "Русский --> Английский":
        lang = 0
        ms = bot.send_message(message.chat.id, get_idiom(lang)[0], reply_markup=markupback)
        bot.register_next_step_handler(ms, check_idiom)

    else:
        ms = bot.send_message(message.chat.id, "Бот вас не понял :(\nВведите направление перевода фразеологизма")
        bot.register_next_step_handler(ms, idioms_test)


def check_idiom(message):
    if message.text.lower() == idioms_memory[-1]:
        ms = bot.send_message(message.chat.id, "Все верно!\n\nСледующий вопрос:\n\n" + get_idiom(lang)[0])
        bot.register_next_step_handler(ms, check_idiom)
    elif message.text == "Назад к тестам":
        bot.send_message(message.chat.id, "Вы вернулись к тестам", reply_markup=markuptests)

    else:
        ms = bot.send_message(message.chat.id, "Неправда! Правильный ответ:\n\n" + idioms_memory[-1] + "\n\n" + "Следующий вопрос:\n\n" + get_idiom(lang)[0])
        bot.register_next_step_handler(ms, check_idiom)


def get_idiom(lang):
    rand_ind = random.randint(0, idioms_amount - 1)

    if lang == 0:
        question = idioms[rand_ind][0].lower()
        answer = idioms[rand_ind][1].lower()

        print(question)
        print(answer)

    elif lang == 1:
        question = idioms[rand_ind][1].lower()
        answer = idioms[rand_ind][0].lower()

        print(question)
        print(answer)

    idioms_memory.append(answer)

    return [question, answer]


# IDIOMS
# ------------------------------------
# SYNONIMS

currentStep = 0
trueAns = 0
wrongAns = []


def testByContext(number):
    queFile = open("Question.txt", "r")
    ansFile = open("Answer.txt", "r")
    ansArray = []
    queArray = []
    while True:
        line = ansFile.readline()
        if not line:
            break
        ansArray.append(line.strip())
    ansFile.close

    while True:
        line = queFile.readline()
        if not line:
            break
        queArray.append(line.strip())

    queFile.close

    def tempDic(n):
        tempArray = []
        border = 3
        indArr = [0, 1, 2, 3]
        randArr = []
        for i in range(4):
            ind = random.randint(0, border)
            randArr.append(indArr[ind])
            c = indArr[ind]
            indArr[ind] = indArr[border]
            indArr[border] = c
            border -= 1
        A1 = ansArray[n].split("//")[randArr[0]]
        A2 = ansArray[n].split("//")[randArr[1]]
        A3 = ansArray[n].split("//")[randArr[2]]
        A4 = ansArray[n].split("//")[randArr[3]]

        tempArray.append(A1)
        tempArray.append(A2)
        tempArray.append(A3)
        tempArray.append(A4)

        return tempArray

    def merge(x, y):
        z = x.copy()
        z.update(y)
        return z

    finalArray = []
    finalArray.append(queArray[number])
    finalArray = finalArray + tempDic(number)
    finalArray.append(ansArray[number].split("//")[0])
    finalArray.append(len(queArray))
    return finalArray


def keboardCreate(number):
    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    arr = testByContext(number)
    but1 = types.KeyboardButton(arr[1])
    but2 = types.KeyboardButton(arr[2])
    but3 = types.KeyboardButton(arr[3])
    but4 = types.KeyboardButton(arr[4])
    butback = types.KeyboardButton("Назад")
    markup1.add(but1, but2)
    markup1.add(but3, but4)
    markup1.add(butback)
    return markup1


def printWrong(arr):
    str = ""
    for i in range(len(arr)):
        str = str + arr[i] + "\n"
    return str


def contextFunction(message):
    global trueAns
    global currentStep
    answer = message.text.lower()
    if answer == 'тест на синонимы':
        trueAns = 0
        currentStep = 0
        infoMessage = bot.send_message(message.chat.id,str(currentStep + 1) + "/" + str(testByContext(0)[6]) + "  " + testByContext(0)[0], reply_markup=keboardCreate(0))
        bot.register_next_step_handler(infoMessage, nextContentFunction)
    elif answer == 'назад к тестам':
        trueAns = 0
        currentStep = 0
        bot.send_message(message.chat.id, 'Вы перешли к тестам', reply_markup=markuptests)


def nextContentFunction(message):
    global trueAns
    global currentStep
    global wrongAns

    if message.text == 'Назад':
        bot.send_message(message.chat.id, 'Вы перешли к тестам. Правильных ответов было - ' + str(trueAns) + "/" + str(
            testByContext(0)[6]), reply_markup=markuptests)
        trueAns = 0
        currentStep = 0

    elif message.text == testByContext(currentStep)[5]:
        trueAns += 1
        currentStep += 1
        if currentStep == testByContext(0)[6]:
            bot.send_message(message.chat.id, 'Вы прошли тест! Ваш результат - ' + str(trueAns) + "/" + str(testByContext(0)[6]) + "  " + "\n" + "Рекомендуем внимательнее проработать предложения: " + "\n" + printWrong(wrongAns), reply_markup=markup)
            wrongAns.clear()
        else:
            infoMessage = bot.send_message(message.chat.id,str(currentStep + 1) + "/" + str(testByContext(0)[6]) + "  " +testByContext(currentStep)[0], reply_markup=keboardCreate(currentStep))
            bot.register_next_step_handler(infoMessage, nextContentFunction)
    else:
        wrongAns.append(testByContext(currentStep)[0])
        currentStep += 1
        if currentStep == testByContext(0)[6]:
            bot.send_message(message.chat.id, 'Вы прошли тест! Ваш результат - ' + str(trueAns) + "/" + str(testByContext(0)[6]) + "  " + "\n" + "Рекомендуем внимательнее проработать предложения: " + "\n" + printWrong(wrongAns), reply_markup=markup)
            wrongAns.clear()
        else:
            infoMessage = bot.send_message(message.chat.id, str(currentStep + 1) + "/" + str(testByContext(0)[6]) + "  " + testByContext(currentStep)[0], reply_markup=keboardCreate(currentStep))
            bot.register_next_step_handler(infoMessage, nextContentFunction)


# SYNONIMS
# -------------------------------------
# THEORY

markupTheory = types.ReplyKeyboardMarkup(resize_keyboard=True)
butt1 = types.KeyboardButton('О теории')
butt2 = types.KeyboardButton('О фразеологизмах')
butt3 = types.KeyboardButton('IELTS')
markupTheory.add(butt1, butt2, butt3)
markupTheory.add(butback)


def theory_func(message):
    answer = message.text.lower()
    if answer == 'о теории':
        ms = bot.send_message(message.chat.id, 'A set of ideas, based on evidence and careful reasoning, which offers an explanation of how something works or why something happens, but has not been completely proved' + '\n\n' + 'https://www.collinsdictionary.com/dictionary/english-thesaurus/theory')
        bot.register_next_step_handler(ms, theory_func)
    elif answer == 'о фразеологизмах':
        ms = bot.send_message(message.chat.id, "Idiom is a phrase or expression whose total meaning differs from the meaning of the individual words. For example, to blow one's top (get angry) and behind the eight ball (in trouble) are English-language idioms. Idioms come from language and generally cannot be translated literally (word for word). Foreign language students must learn them just as they would learn vocabulary words. Idioms come to be a very numerous part of English. Idioms cover a lot of drawbacks of the English language and it is one-third part of the colloquial speech. While some teaching materials may ignore idioms, or try to demote their importance, it is best for teachers to take the time to explain, discuss, and make their students use them." + '\n\n' + 'https://otherreferats.allbest.ru/languages/00776974_0.html')
        bot.register_next_step_handler(ms, theory_func)
    elif answer == 'ielts':
        ms = bot.send_message(message.chat.id, 'The International English Language Testing System (IELTS) is designed to help you work, study or migrate to a country where English is the native language. This includes countries such as Australia, Canada, New Zealand, the UK and USA.'+"\n\n"+'https://www.ielts.org/')
        bot.register_next_step_handler(ms, theory_func)
    elif answer == 'назад в меню':
        bot.send_message(message.chat.id, 'Вы перешли в меню', reply_markup=markup)


# THEORY
# ---------------------------------------
# BOT


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Привет', reply_markup=markup)

    elif message.text == '/help':
        bot.send_message(message.chat.id, help_text)


@bot.message_handler(content_types=['text'])
def ask_for_link(message):
    if message.text == 'Тесты':
        bot.send_message(message.chat.id, 'Выбирите тест', reply_markup=markuptests)
    elif message.text == 'Назад в меню':
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню', reply_markup=markup)
    elif message.text == 'Тест на видосы':
        msg_temp = bot.send_message(message.chat.id, "Вы выбрали тест на видосы \nПришли ссылку", reply_markup=markupback)
        bot.register_next_step_handler(msg_temp, bot_send_texts)
    elif message.text == 'Назад к тестам':
        bot.send_message(message.chat.id, 'Вы в перешли к тестам', reply_markup=markuptests)
    elif message.text == 'Связь':
        bot.send_message(message.chat.id, 'Для обратной связь писать сюда @ziperlin')
    elif message.text == 'Тест на фразеологизмы':
        ms = bot.send_message(message.chat.id, "Выберите формат тестирования", reply_markup=choose_lang_idioms)
        bot.register_next_step_handler(ms, idioms_test)
    elif message.text == "Тест на синонимы":
        contextFunction(message)

    elif message.text == "Теория":
        infoMessage = bot.send_message(message.chat.id, "О чем вы хотите узнать?", reply_markup=markupTheory)
        bot.register_next_step_handler(infoMessage, theory_func)

    else:
        bot.send_message(message.chat.id, "Бот вас не понял :( \nПопробуйте еще раз")


bot.infinity_polling(True)
