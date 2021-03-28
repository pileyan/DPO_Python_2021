# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
import telebot
import re
from random import randint
import config
import dbworker

bot = telebot.TeleBot(config.token)


def stat(tag=0):
    url = 'https://www.worldometers.info/coronavirus/'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[tag]
    rows = table.find_all('tr')
    d = dict()
    for i in range(9):
        col = []
        key = rows[0].find_all('th')[i + 1].get_text().strip()

        for row in rows[1:230]:
            r = row.find_all('td')
            col.append(r[i + 1].get_text().strip())
        d[key] = col
    df = pd.DataFrame(d)
    df = df.rename(columns={'Country,Other': 'Country', 'Serious,Critical': 'SeriousCritical'})
    return df


pict = [
    'https://avatars.mds.yandex.net/get-pdb/2864819/2091b635-1a05-4a81-9f4f-9cdd46cb9be0/s1200',
    'https://avatars.mds.yandex.net/get-zen_doc/196516/pub_5d65e93efe289100adb4c54e_5d66099378125e00ac052d00/scale_1200',
    'https://avatars.mds.yandex.net/get-pdb/1683100/d71b5f09-b408-42ce-b480-cbcd0d340efe/s1200?webp=false',
    'https://avatars.mds.yandex.net/get-zen_doc/1899089/pub_5d9b5f2f35c8d800ae71fb5a_5d9b60a98f011100b48eb4fb/scale_1200',
    'https://avatars.mds.yandex.net/get-zen_doc/196516/pub_5d65e93efe289100adb4c54e_5d66099378125e00ac052d00/scale_1200',
    'http://ysia.ru/wp-content/uploads/2018/01/1-19.jpg'
    ]

# @bot.message_handler()
# def echo(message):
#     bot.send_photo(message.chat.id, pict[randint(0, 5)])


@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "Info method is used to show you what I am capable of.\n"
                                      "I could provide you with some statistics on the notorious COVID-19 pandemia.\n"
                                      "First you gotta select the day of statistics: \n"
                                      "I only have info for yesterday and today\n"
                                      "Then it's time to specify if you are interested in regions or countries.\n"
                                      "You gotta type either regions or countries.\n"
                                      "Type /reset to start anew.")
    bot.send_message(message.chat.id, "The next step is to specify which countries/regions you are interested in.\n"
                                      "You should enter comma-delimited list of countries or regions or just a single country/region:\n"
                                      "For example  UK, Iran, Uganda, Equatorial Guinea.\n"
                                      "You can also get lists of available regions/countries using /listregions or /listcountries correspondingly.\n"
                                      "Finally It's time to specify what kind of statistics do you want to get: \n"
                                      "You should enter comma-delimited list of fields or just a single field\n"
                                      "For example  TotalCases, SeriousCritical.\n"
                                      "You can get list of available fields using /listfields\n"
                                      "Type /reset to start anew.")
    bot.send_message(message.chat.id, "There's a number of commands you can use here. \n"
                                      "Type /commands to get the list of available functions.\n"
                                      "Type /reset to start anew.")


@bot.message_handler(commands=["listcountries"])
def cmd_listcountries(message):
    x = stat()['Country'][8:]
    bot.send_message(message.chat.id,
                     ', '.join([e+'\n' if i % 6 == 5 else e for i, e in enumerate(x)]).replace('\n,', ',\n'))


@bot.message_handler(commands=["listregions"])
def cmd_listregions(message):
    x = stat()['Country'][:8]
    bot.send_message(message.chat.id,
                     ', '.join(i for i in list(x) if i != ''))


@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id,
                     "/reset - is used to discard previous selections and start anew.\n"
                     "/start - is used to start a new dialogue from the very beginning.\n"
                     "/info - is used to know what i can do for you (there's a tree of commands)\n"
                     "/commands - If you got here, you know what it is used for.\n"
                     "/listregions - is used to list regions covered by statistics.\n"
                     "/listcountries - is used to list countries covered by statistics.\n"
                     "/listfields - is used to list fields available in statistics")


@bot.message_handler(commands=["listfields"])
def cmd_listfields(message):
    x = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths',
         'TotalRecovered', 'ActiveCases', 'SeriousCritical']
    bot.send_message(message.chat.id, ", ".join(x))


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Let's start anew.\n"
                                      "Which day's statistics do you want to get: /today or /yesterday.\n"
                                      "Use /info or /commands to rewind what I am and what can I do.")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DAY.value)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    bot.send_message(message.chat.id, "Greetings again! I'm coronabot :) \n"
                                      "You gotta specify which day's statistics you want to get: /today or /yesterday.\n"
                                      "Type /info to know what I am and what I can do for you.\n"
                                      "Tye /commands to list the available commands.\n"
                                      "Type /reset to discard previous selections and start anew.")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DAY.value)


@bot.message_handler(func=lambda message: (dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DAY.value)
                                          and message.text.strip().lower() not in
                                          ('/reset', '/info', '/start', '/commands',
                                          '/listregions','/listfields'))
def cmd_day(message):
    dbworker.del_state(str(message.chat.id)+'day')
    if message.text.lower().strip() == '/yesterday':
        #day = 1
        bot.send_message(message.chat.id, "Ok, we've specified the date of statistics. It's time to go further. \n"
                                          "Do you want to know things about /regions or /countries?\n"
                                          "You could also type /info to know more about me.\n"
                                          "Type /reset to start anew.")
        dbworker.set_property(str(message.chat.id) + 'day', 'yesterday')  # запишем день в базу
        dbworker.set_state(message.chat.id, config.States.S_COUNTRY_OR_REGION.value)
    elif message.text.lower().strip() == '/today':
        # day = 0
        bot.send_message(message.chat.id, "Ok, we've specified the date for statistics. It's time to go further. \n"
                                          "Do you want to know things about /regions or /countries?\n"
                                          "You could also type /info to know more about me.\n"
                                          "Type /reset to start anew.")

        dbworker.set_property(str(message.chat.id) + 'day', 'today')  # запишем день в базу
        dbworker.set_state(message.chat.id, config.States.S_COUNTRY_OR_REGION.value)
    else:
        bot.send_message(message.chat.id, "Seems like you've already got acquainted with me.\n"
                                          "Now you gotta specify the date for statistics.\n"
                                          "I have information for /yesterday and /today \n"
                                          "To recollect what we are doing now type /info.\n"
                                          "Type /reset to start anew.")



@bot.message_handler(func=lambda message: message.text not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions',
                                                              '/listfields'))
def cmd_sample_message(message):
    bot.send_message(message.chat.id, "Hey there, I'm coronabot!\n"
                                      "I'm not that smart, sorry :(\n"
                                      "But I guess you want some statistics on COVID-19.\n"
                                      "That's what I can help you with!.\n"
                                      "If so, type /start and let's get some. \n"
                                      "Type /info to know what i can do for you.\n"
                                      "Type /commands to list available commands :).")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])



if __name__ == '__main__':
    bot.infinity_polling()
