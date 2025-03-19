from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# Botun admini
ADMIN_USERNAME = "@Elegante_offical"

# Kullanıcı verileri (test amaçlı RAM'de, veritabanına bağlanabilirsiniz)
users = {}

# Mevcut görevler
tasks = {
    "botlar": {"title": "Botlara giriş yap", "reward": 0.01, "penalty": -0.02},
    "kanallar": {"title": "Kanallara abone ol", "reward": 0.01, "penalty": -0.02},
}

# Kullanıcıyı kaydetme fonksiyonu
def register_user(user_id, username):
    if user_id not in users:
        users[user_id] = {"username": username, "balance": 0.0, "total_earned": 0.0}

# /start komutu
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    register_user(user.id, user.username)
    keyboard = [
        [InlineKeyboardButton("📋 Profil", callback_data="profile")],
        [InlineKeyboardButton("💰 Çekim", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Görevler", callback_data="tasks")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Merhaba! Görev botuna hoş geldiniz.", reply_markup=reply_markup)

# Profil gösterme
def profile(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = users.get(user_id, {"balance": 0, "total_earned": 0})
    
    profile_text = f"""
👤 Kullanıcı: @{query.from_user.username}
🆔 ID: {user_id}
💵 Bakiye: {user['balance']:.2f} USD
💰 Toplam Kazanç: {user['total_earned']:.2f} USD
    """
    query.message.reply_text(profile_text)

# Çekim işlemi
def withdraw(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = users.get(user_id, {"balance": 0})

    if user["balance"] < 0.5:
        query.message.reply_text("❌ Yetersiz bakiye! En az 0.5 USD olmalıdır.")
        return
    
    query.message.reply_text("📞 Paranın gönderileceği telefon numarasını girin (8 haneli, 6 veya 7 ile başlamalı).")
    context.user_data["awaiting_phone"] = True

# Telefon numarası kontrolü
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = users.get(user_id, {"balance": 0})
    
    if context.user_data.get("awaiting_phone"):
        phone_number = update.message.text
        if phone_number.isdigit() and len(phone_number) == 8 and phone_number[0] in "67":
            user["balance"] = 0
            update.message.reply_text(f"✅ Para çekme işlemi başarılı! 3 gün içinde {phone_number} numarasına gönderilecek.")
            context.user_data["awaiting_phone"] = False
        else:
            update.message.reply_text("❌ Hatalı numara! 8 haneli ve 6 veya 7 ile başlamalı.")

# Görevler menüsü
def tasks_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🤖 Botlara giriş yap", callback_data="botlar")],
        [InlineKeyboardButton("📢 Kanallara abone ol", callback_data="kanallar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("🎯 Görevleri seçin:", reply_markup=reply_markup)

# Görev işleme fonksiyonu
def handle_task(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    task_type = query.data  # botlar veya kanallar

    if task_type in tasks:
        user = users.get(user_id, {"balance": 0, "total_earned": 0})
        user["balance"] += tasks[task_type]["reward"]
        user["total_earned"] += tasks[task_type]["reward"]
        query.message.reply_text(f"✅ {tasks[task_type]['title']} tamamlandı! Bakiye: {user['balance']:.2f} USD")

# Admin paneli
def admin_panel(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.username == ADMIN_USERNAME:
        keyboard = [
            [InlineKeyboardButton("➕ Yeni Görev Ekle", callback_data="add_task")],
            [InlineKeyboardButton("📊 Kullanıcıları Görüntüle", callback_data="view_users")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🛠 Admin Paneli", reply_markup=reply_markup)
    else:
        update.message.reply_text("❌ Yetkiniz yok!")

# Yeni görev ekleme (admin)
def add_task(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    if user.username == ADMIN_USERNAME:
        query.message.reply_text("Yeni görev adını ve ödülü girin (örnek: 'Görev Adı,0.02').")
        context.user_data["awaiting_task"] = True
    else:
        query.message.reply_text("❌ Yetkiniz yok!")

# Yeni görev alma
def handle_new_task(update: Update, context: CallbackContext):
    if context.user_data.get("awaiting_task"):
        try:
            task_name, reward = update.message.text.split(",")
            reward = float(reward)
            tasks[task_name] = {"title": task_name, "reward": reward, "penalty": -reward}
            update.message.reply_text(f"✅ Yeni görev eklendi: {task_name} ({reward} USD)")
            context.user_data["awaiting_task"] = False
        except:
            update.message.reply_text("❌ Hatalı format! Örnek: 'Görev Adı,0.02'")

# Bot başlatma
def main():
    updater = Updater("7085060766:AAGGaI6eFUnmF0uVGk7fF6pgElSZ-AqsZH8", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(profile, pattern="profile"))
    dp.add_handler(CallbackQueryHandler(withdraw, pattern="withdraw"))
    dp.add_handler(CallbackQueryHandler(tasks_menu, pattern="tasks"))
    dp.add_handler(CallbackQueryHandler(handle_task, pattern="botlar|kanallar"))
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(CallbackQueryHandler(add_task, pattern="add_task"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()