from flask import Flask, request
from threading import Thread
import telebot
import json
import random
import time
from datetime import datetime

# === FLASK SETUP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route(f"/8043781739:AAEls8RRLsHiqHTr6EWU6ZYR_5_eogLTtuA", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# === BOT SETUP ===
BOT_TOKEN = "8043781739:AAEls8RRLsHiqHTr6EWU6ZYR_5_eogLTtuA"
CHANNEL_ID = "-1002840644974"
ADMIN_ID = 1427409581

bot = telebot.TeleBot(BOT_TOKEN)
print("✅ Bot created successfully")

# === Set webhook (HARDCODED)
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://stylehub-bot-final.onrender.com/8043781739:AAEls8RRLsHiqHTr6EWU6ZYR_5_eogLTtuA")

# === LOGIC ===
is_paused = False
last_post_time = None
posted_indexes = set()

def load_deals():
    with open("deals.json", "r", encoding="utf-8") as f:
        return json.load(f)

def post_deal():
    global last_post_time
    deals = load_deals()
    if len(posted_indexes) == len(deals):
        posted_indexes.clear()
    index = random.choice([i for i in range(len(deals)) if i not in posted_indexes])
    posted_indexes.add(index)
    deal = deals[index]

    caption = f"{deal['title']}\n\n🛍️ Tap here: {deal['ek_link']}\n\n#StyleHubIND #FlipkartFashion"
    try:
        if 'image' in deal:
            bot.send_photo(CHANNEL_ID, photo=deal['image'], caption=caption)
        else:
            bot.send_message(CHANNEL_ID, caption)
        last_post_time = datetime.now().strftime("%d %b %Y %I:%M %p")
        print(f"✅ Posted: {deal['title']}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👋 Bot is live! Use /pause /resume /status /nextdeal")

@bot.message_handler(commands=['pause'])
def pause(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = True
        bot.reply_to(message, "⏸️ Posting paused.")

@bot.message_handler(commands=['resume'])
def resume(message):
    global is_paused
    if message.from_user.id == ADMIN_ID:
        is_paused = False
        bot.reply_to(message, "▶️ Posting resumed.")

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id == ADMIN_ID:
        msg = f"📊 Last Post: {last_post_time or 'None yet'}\n🕒 Next post in 1 hour"
        bot.reply_to(message, msg)

@bot.message_handler(commands=['nextdeal'])
def nextdeal(message):
    if message.from_user.id == ADMIN_ID:
        post_deal()
        bot.reply_to(message, "✅ Deal posted to channel.")

print("🚀 Bot started with webhook")
