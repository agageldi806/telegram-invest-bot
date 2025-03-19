from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import re

# Botun tokeni
TOKEN = "7085060766:AAGGaI6eFUnmF0uVGk7fF6pgElSZ-AqsZH8"
# Admin kullanıcı adı
ADMIN_USERNAME = "@Elegante_offical"

# Kullanıcı verilerini saklamak için sözlük
user_data = {}

# Görev başına ödül
TASK_REWARD = 0.05
# Minimum çekim miktarı
MIN_WITHDRAWAL = 0.5
# Çekim ücreti
WITHDRAWAL_FEE = 0.02

# Başlangıç komutu
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "username": update.message.from_user.username,
            "balance": 0.0,
            "total_earned": 0.0,
            "withdrawal_amount": 0.0
        }
    keyboard = [
        [InlineKeyboardButton("Profile", callback_data='profile')],
        [InlineKeyboardButton("Çekim", callback_data='withdraw')],
        [InlineKeyboardButton("Görevler", callback_data='tasks')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hoş geldiniz! Lütfen bir seçenek seçin:", reply_markup=reply_markup)

# Profil butonu
def profile(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = user_data[user_id]
    profile_text = (
        f"Kullanıcı Adı: {user['username']}\n"
        f"ID: {user_id}\n"
        f"Mevcut Bakiye: ${user['balance']:.2f}\n"
        f"Toplam Kazanç: ${user['total_earned']:.2f}\n"
        f"Çekim Miktarı: ${user['withdrawal_amount']:.2f}"
    )
    query.answer()
    query.edit_message_text(text=profile_text)

# Çekim butonu
def withdraw(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = user_data[user_id]
    if user['balance'] < MIN_WITHDRAWAL:
        query.answer()
        query.edit_message_text(text=f"Yetersiz bakiye! Minimum çekim miktarı: ${MIN_WITHDRAWAL:.2f}")
    else:
        query.answer()
        query.edit_message_text(text="Lütfen telefon numaranızı girin (8 haneli, 6 veya 7 ile başlamalı):")
        context.user_data['awaiting_phone'] = True

# Telefon numarası doğrulama
def handle_phone(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    phone = update.message.text
    if re.match(r'^[67]\d{7}$', phone):
        user_data[user_id]['withdrawal_amount'] = user_data[user_id]['balance']
        user_data[user_id]['balance'] = 0.0
        update.message.reply_text(f"Çekim talebiniz alındı. 3 gün içinde ${user_data[user_id]['withdrawal_amount']:.2f} telefon numaranıza gönderilecek.")
        context.user_data['awaiting_phone'] = False
    else:
        update.message.reply_text("Geçersiz telefon numarası! Lütfen 8 haneli ve 6 veya 7 ile başlayan bir numara girin.")

# Görevler butonu
def tasks(update: Update, context: CallbackContext):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Botlara Giriş Yap", callback_data='login_bots')],
        [InlineKeyboardButton("Kanallara Abone Ol", callback_data='subscribe_channels')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.answer()
    query.edit_message_text(text="Görevler:", reply_markup=reply_markup)

# Görev tamamlama
def complete_task(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user_data[user_id]['balance'] += TASK_REWARD
    user_data[user_id]['total_earned'] += TASK_REWARD
    query.answer()
    query.edit_message_text(text=f"Görev tamamlandı! ${TASK_REWARD:.2f} bakiyenize eklendi.")

# Admin paneli
def admin_panel(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if update.message.from_user.username == ADMIN_USERNAME:
        update.message.reply_text("Admin paneline hoş geldiniz!")
        # Burada admin işlemleri eklenebilir
    else:
        update.message.reply_text("Bu komutu kullanma yetkiniz yok.")

# Hata yönetimi
def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")

# Ana fonksiyon
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komutlar
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_panel))

    # Butonlar
    dp.add_handler(CallbackQueryHandler(profile, pattern='^profile$'))
    dp.add_handler(CallbackQueryHandler(withdraw, pattern='^withdraw$'))
    dp.add_handler(CallbackQueryHandler(tasks, pattern='^tasks$'))
    dp.add_handler(CallbackQueryHandler(complete_task, pattern='^login_bots$'))
    dp.add_handler(CallbackQueryHandler(complete_task, pattern='^subscribe_channels$'))

    # Mesaj işleme
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_phone))

    # Hata yönetimi
    dp.add_error_handler(error)

    # Botu başlat
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()