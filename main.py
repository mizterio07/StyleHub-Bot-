from flask import Flask, request
from threading import Thread
import telebot
import json
import random
import time
from datetime import datetime
import logging

# === CONFIG ===
BOT_TOKEN = "8043781739:AAE5itRQD1Jh24pN0QDfD4lbyMU5095LeBM"
CHANNEL_ID = "-1002840644974"
ADMIN_ID = 1427409581
WEBHOOK_URL = f"https://stylehub-bot-final.onrender.com/{BOT_TOKEN}"

# === LOGGING ===
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# === BOT INIT ===
bot = telebot.TeleBot(BOT_TOKEN)

# === REMOVE POLLING ===
# 🔥 DO NOT USE polling() anywhere in this file

# === WEBHOOK SETUP ===
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)
print(f"✅ Webhook set to: {WEBHOOK_URL}")

# === FLASK APP SETUP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive with webhook!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# === STATE ===
is_paused = False
last_post_time = None
is_flipkart = True
posted_indexes_flipkart = set()
posted_indexes_ajio = set()

# === DEALS ===
def load_deals(source):
    file = "deals.json" if source == "flipkart" else "ajio_deals.json"
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def post_deal(source_toggle=None):
    global last_post_time, is_flipkart, posted_indexes_flipkart, posted_indexes_ajio

    source = source_toggle if source_toggle else ("flipkart" if is_flipkart else "ajio")
    deals = load_deals(source)
    posted = posted_indexes_flipkart if source == "flipkart" else posted_indexes_ajio

    if len(posted) >= len(deals):
        posted.clear()
        print(f"🔁 Resetting {source} cycle.")

    available = [i for i in range(len(deals)) if i not in posted]
    if not available:
        print(f"⚠️ No {source} deals left.")
        return

    index = random.choice(available)
    posted.add(index)
    if source == "flipkart":
        posted_indexes_flipkart = posted
    else:
        posted_indexes_ajio = posted

    deal = deals[index]
    caption = f"{deal['title']}\n\n🛍️ Tap here: {deal['ek_link']}\n\n#StyleHubIND #{source.capitalize()}Fashion"

    try:
        if 'image' in deal:
            bot.send_photo(CHANNEL_ID, deal['image'], caption=caption)
        else:
            bot.send_message(CHANNEL_ID, caption)
        last_post_time = datetime.now().strftime("%d %b %Y %I:%M %p")
        print(f"✅ Posted: {deal['title']}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

    if not source_toggle:
        is_flipkart = not is_flipkart

# === TELEGRAM COMMANDS ===
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👋 Bot live via webhook.\nUse /pause /resume /status /nextdeal /postflipkart /postajio")

@bot.message_handler(commands=['pause'])
def pause(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = True
        bot.reply_to(message, "⏸️ Auto-posting paused.")

@bot.message_handler(commands=['resume'])
def resume(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = False
        bot.reply_to(message, "▶️ Auto-posting resumed.")

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 Last post: {last_post_time or 'None'}")

@bot.message_handler(commands=['nextdeal'])
def nextdeal(message):
    if message.from_user.id == ADMIN_ID:
        post_deal()
        bot.reply_to(message, "✅ Deal posted.")

@bot.message_handler(commands=['postflipkart'])
def postflipkart(message):
    if message.from_user.id == ADMIN_ID:
        post_deal("flipkart")
        bot.reply_to(message, "✅ Flipkart deal posted.")

@bot.message_handler(commands=['postajio'])
def postajio(message):
    if message.from_user.id == ADMIN_ID:
        post_deal("ajio")
        bot.reply_to(message, "✅ Ajio deal posted.")

# === BACKGROUND AUTO POSTING ===
def auto_post():
    while True:
        try:
            if not is_paused:
                post_deal()
            time.sleep(3600)
        except Exception as e:
            print(f"⚠️ Auto-post error: {e}")
            time.sleep(30)

Thread(target=auto_post).start()

# === START FLASK ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
