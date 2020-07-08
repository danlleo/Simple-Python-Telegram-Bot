import config
import telebot
import pyowm

from telebot import types

bot = telebot.TeleBot(config.telegram_token)
owm = pyowm.OWM(config.pyowm_token)

located = False
started = False
keys_on = False


observation = ''
place = ''


@bot.message_handler(commands=['start'])
def start(message):
    global started

    if located is False:
        bot.send_message(message.chat.id, "Привет✌ Я бот который будет отправлять тебе погоду \U0001f609")
        bot.send_message(message.chat.id, "Чтобы продолжить, напиши город в котором ты живёшь 🌍")
        print(message.text)
    else:
        bot.send_message(message.chat.id, "Похоже что бот уже запущен, если хочешь изменить локацию, просто напиши "
                                          "/setlocation")
        print(message.text)


@bot.message_handler(commands=['setlocation'])
def set_location(message):
    global started
    global located

    if started:
        located = False

        bot.send_message(message.chat.id, "Я сбросил локацию, напиши новый город для которого ты хочешь получать "
                                          "погоду.")
        print(message.text)

    else:
        bot.send_message(message.chat.id, "Похоже вы не запускали бота, пожалуйста, напишите команду /start и "
                                          "следуйте инструкциям.")
        print(message.text)


@bot.message_handler(content_types=['text'])
def respond(message):
    global place
    global located
    global observation

    print(message.text)

    if located is False:
        try:
            place = message.text
            observation = owm.weather_at_place(place)
            bot.send_message(message.chat.id, "Ура 😎 Я нашёл город - " + place + "!")

            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton("Да", callback_data="Agreed")
            item2 = types.InlineKeyboardButton("Другой город", callback_data="Disagreed")

            markup.add(item1, item2)

            bot.send_message(message.chat.id, "Хотите получать погоду для этого города ?🤔", reply_markup=markup)
            print(message.text)
            print(type(observation))

        except Exception as inst:
            bot.send_message(message.chat.id, "Мне не удалось найти этот город, попробуй ещё раз...")
            print(inst)
    else:
        global keys_on

        markup = types.ReplyKeyboardMarkup()
        item1 = types.KeyboardButton("Погода сейчас")

        markup.add(item1)

        if not keys_on:
            if message.text == "/keyboard":
                bot.send_message(message.chat.id, 'Клавиатура успешно запущена!', reply_markup=markup)
                keys_on = True
                print(message.text)

        if keys_on:
            if message.text == "Погода сейчас":
                w = observation.get_weather()
                bot.send_message(message.chat.id, 'Погода в городе ' + place + ': ' + str(round(w.get_temperature('celsius')['temp'])) + '°', reply_markup=markup)
                print(message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            global located

            if located is False:
                if call.data == "Agreed":
                    bot.send_message(call.message.chat.id, "Локация успешно установлена!")

                    if not keys_on:
                        bot.send_message(call.message.chat.id, "Чтобы запустить клавиатуру, напиши /keyboard")

                    global started

                    located = True
                    started = True

                elif call.data == "Disagreed":
                    bot.send_message(call.message.chat.id, "Напишите другой город.")

    except Exception as e:
        bot.send_message(call.message.chat.id, "Упс, что-то пошло не так ...")
        print(e)


if __name__ == '__main__':
    bot.polling(none_stop=True)
    
