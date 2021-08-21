import psycopg2
from psycopg2 import OperationalError
import telebot
import datetime

bot = telebot.TeleBot('1933002165:AAE3vKyCUo9Bf_7ltqfpY1x3WFQX70NGXKI')

cancel = telebot.types.InlineKeyboardMarkup()
cancelBtn = telebot.types.InlineKeyboardButton(text='Отмена', callback_data = 'cancel')
cancel.add(cancelBtn)

menu = telebot.types.InlineKeyboardMarkup()
menu.add(telebot.types.InlineKeyboardButton(text='Новая запись', callback_data = 'newExp'), telebot.types.InlineKeyboardButton(text='Статистика', callback_data = 'statistic'))

tempKb2 = telebot.types.InlineKeyboardMarkup()
tempKb2.add(telebot.types.InlineKeyboardButton(text='Да', callback_data = 'addComm'), telebot.types.InlineKeyboardButton(text='Нет', callback_data = 'dontAddComm'))
tempKb2.add(cancelBtn)

global state
global record
state = 'newRecord'
record = {
	'sum':-10,
	'dateTime':'01/01/1980',
	'comment':'None',
	'id_user':-10
}

@bot.message_handler(commands=['start'])
def handle_text_messages(message):
	begin = telebot.types.InlineKeyboardMarkup()
	begin.add(telebot.types.InlineKeyboardButton(text='Начнем?', callback_data = 'start'))
	bot.send_message(message.chat.id, "Привет, я бот, который поможет тебе контролировать твои финанасы!", reply_markup = begin)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	global state
	global record
	bot.answer_callback_query(call.id)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = call.message.text, reply_markup = None)
	if call.data == 'start':		
		bot.send_message(call.message.chat.id, "Я умею:\n- Делать записи твоих расходов\n- Показывать статистику", reply_markup = menu)
	elif call.data == "newExp":
		bot.send_message(call.message.chat.id, 'Введите сумму, которую вы потратили.', reply_markup = cancel)
		state = 'inputSum'
	elif call.data == "now":
		now = datetime.datetime.now()
		record['dateTime'] = f'{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}'
		bot.send_message(call.message.chat.id, f'Будет записано текущее время: {now.year}/{now.month}/{now.day}  {now.hour}:{now.minute}\nЖелаете добавить коментарий?', reply_markup = tempKb2)
	elif call.data == "notNow":
		bot.send_message(call.message.chat.id, 'Введите дату, в которую была совершена трата в формате [День/Месяц/Год].', reply_markup = cancel)
		state = 'inputDate'
	elif call.data == "addComm":
		bot.send_message(call.message.chat.id, 'Введите ваш комментарий.')
		state = "inputComment"
	elif call.data == "dontAddComm":
		record['id_user'] = call.message.from_user.id
		bot.send_message(call.message.chat.id, f'Сумма - {record["sum"]}\nДата - {record["dateTime"]}\nКомментарий - {record["comment"]}\nПользователь - {record["id_user"]}')
		bot.send_message(call.message.chat.id, "Успешно добавленно в базу данных!", reply_markup = menu)		
		record = {
			'sum':-10,
			'dateTime':'01/01/1980',
			'comment':'None',
			'id_user':-10
		}
	elif call.data == 'statistic':
		bot.send_message(call.message.chat.id, "Эта функция временно недоступна.", reply_markup = menu)
	elif call.data == "cancel":
		record={
			'sum':-10,
			'dateTime':'01/01/0001',
			'comment':'None',
			'id_user':-10
		}
		state ='newRecord'
		bot.send_message(call.message.chat.id, 'Операция отменена!', reply_markup = menu)	
	else:
		print(f'Error! Unexpected callback: {call.data}')

@bot.message_handler(content_types=['text'])
def inputText(message):
	global state
	global record
	if state == 'newRecord':
		bot.send_message(message.chat.id, "Возможно, вы хотите добавить новую запись или посмотреть статистику?", reply_markup = menu)
	elif state == 'inputSum':
		tempKb1 = telebot.types.InlineKeyboardMarkup()
		tempKb1.add(telebot.types.InlineKeyboardButton(text='Да', callback_data = 'now'), telebot.types.InlineKeyboardButton(text='Нет', callback_data = 'notNow'))
		tempKb1.add(cancelBtn)
		try:
			record['sum'] = int(message.text)
			bot.send_message(message.chat.id, "Вы потратили деньги только что?", reply_markup = tempKb1)
			state = 'none'
		except ValueError:
			bot.send_message(message.chat.id, "Некорретно! Введите число.", reply_markup = cancel)			
	elif state == 'inputDate':
		try:
			date = convertToDate(message.text)
			if datetime.datetime.now() <= datetime.datetime.strptime(date, '%d/%m/%y'):
				bot.send_message(message.chat.id, "Некорректно! Дата больше текущей.\nВведите дату в формате [День/Месяц/Год]", reply_markup = cancel)
				return
			record['dateTime'] = datetime.datetime.strptime(date, '%d/%m/%y')
			bot.send_message(message.chat.id, "Желаете добавить комментарий?", reply_markup = tempKb2)
			state = 'none'
		except ValueError:
			bot.send_message(message.chat.id, "Некорретно! Введите дату в формате. [День/Месяц/Год].", reply_markup = cancel)				
	elif state == 'inputComment':
		record['comment'] = message.text
		record['id_user'] = message.from_user.id
		bot.send_message(message.chat.id, f'Сумма - {record["sum"]}\nДата - {record["dateTime"]}\nКомментарий - {record["comment"]}\nПользователь - {record["id_user"]}')
		bot.send_message(message.chat.id, "Успешно добавленно в базу данных!", reply_markup = menu)		
		record = {
			'sum':-10,
			'dateTime':'01/01/1980',
			'comment':'None',
			'id_user':-10
		}
		state = 'newRecord'
	elif state == 'none':
		pass
	else:
		print(f'Произошла ошибка, состояние:{state}')

def convertToDate(str):
	return str[:6]+str[8:]


def create_connection(db_name, db_user, db_password, db_host, db_port):
	connection = None
	try:
		connection = psycopg2.connect(
			database=db_name,
			user=db_user,
			password=db_password,
			host=db_host,
			port=db_port,
			)
		print("Connection to PostgreSQL DB successful")
	except OperationalError as e:
		print(f"The error '{e}' occurred")
	return connection


if __name__ == '__main__':
	connection = create_connection(
		"postgres", "postgres", "root", "#money_bot_PostgreSQL_1", "5432"
		)
	bot.polling(none_stop=True, interval=0)

# def selecet_id(connection, query):
# 	connection.autocommit = True
# 	cursor = connection.cursor()
# 	try:
# 		cursor.execute(query)
# 		print("Query executed successfully")
# 		return 	cursor.fetchall()
# 	except OperationalError as e:
# 		print(f"The error '{e}' occurred")

# selecet_id_query = "select * from test"
# ids = selecet_id(connection, selecet_id_query)
# print(ids)