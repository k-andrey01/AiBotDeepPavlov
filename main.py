import multiprocessing

import telebot;
from deeppavlov.core.common.file import read_json
from deeppavlov import build_model, train_model
from multiprocessing import Process

bot = telebot.TeleBot('');

contextFile = open("context.txt", 'r', encoding='UTF-8')
context = contextFile.read()

model_config = read_json('squad_ru_bert_infer.json')
intent_catcher_model_config = read_json('intent_catcher.json')
model = build_model(model_config)

case = 1

def get_answer_message(message):
    bot.reply_to(message, "Ваш вопрос в обработке, ожидайте!")
    messageText = message.text
    answer = model([context], [messageText])
    print(answer)
    if answer[0][0].strip() and answer[2][0] > 1000:
        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "Я не знаю")

def get_start_message(message):
    bot.reply_to(message, "Вы на начальном этапе работы с ботом. Что вы хотите сделать?")


def get_links():
    return open("links.txt", encoding="utf-8").read()

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    global case
    if case == 1:
        print("Main")
        queue.put(message.text)
        intent_result = queue.get()
        print("Сообщение:", message.text)
        print("Интент:", intent_result[0])

        if intent_result[0] == 'start':
            get_start_message(message)
            case = 1
        elif intent_result[0] == 'answering':
            bot.reply_to(message, "Вы в режиме ответов на вопросы! Задавайте Ваш вопрос!")
            # get_answer_message(message)
            case = 2
        elif intent_result[0] == 'links':
            bot.reply_to(message, "Ссылки на ресурсы Зенита:\n" + get_links())
        else:
            bot.reply_to(message, "Я не понимаю")
    else:
        print("Answering")
        queue.put(message.text)
        intent_result = queue.get()
        print("Сообщение:", message.text)
        print("Интент:", intent_result[0])
        if intent_result[0] == 'start' and not "?" in message.text:
            get_start_message(message)
            case = 1
        else:
            get_answer_message(message)

def work_with_intent_catcher_model(q):
    intent_catcher_model = build_model(intent_catcher_model_config)
    #intent_catcher_model = train_model(intent_catcher_model_config)
    q.put(1)
    while True:
        q.put(intent_catcher_model([q.get()]))

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    newProcess = Process(target=work_with_intent_catcher_model, args=(queue,))
    newProcess.start()
    queue.get()
    print('Bot is here!')
    bot.polling(none_stop=True)
