import random
import time
import pickle
import os
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

TOKEN = "7612547079:AAEzbQEcHRD4dprHogr5JLY5ScOEoCCjT8o"
DATA_FILE = "user_data.pkl"
SELECT_ITEM, ENTER_TRADE_LINK, ENTER_DEPOSIT_AMOUNT, SELL_ITEMS, SELL_SELECTED, WAITING_DEPOSIT_AMOUNT, WAITING_SUPPORT_MESSAGE = range(7)
ADMIN_ID = 1473801995

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            pass
    return {'users_db': {}, 'trade_links': {}, 'last_daily_bonus': {}}

def save_data(data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(data, f)

data = load_data()
users_db = data['users_db']
TRADE_LINK = data['trade_links']
LAST_DAILY_BONUS = data['last_daily_bonus']

RARITY_COMMON = "🔹 Промышленное качество"
RARITY_MILSPEC = "🔹 Армейское качество"
RARITY_RESTRICTED = "🟪 Запрещенное"
RARITY_CLASSIFIED = "🟪 Засекреченное"
RARITY_COVERT = "♦️ Тайное"
RARITY_RARE = "🔶 Крайне редкий предмет или контрабандное"

RARITIES = {
    RARITY_COMMON: {"chance": 50.0, "multiplier": 1},
    RARITY_MILSPEC: {"chance": 30.0, "multiplier": 1},
    RARITY_RESTRICTED: {"chance": 10.0, "multiplier": 1},
    RARITY_CLASSIFIED: {"chance": 5.0, "multiplier": 1},
    RARITY_COVERT: {"chance": 1.0, "multiplier": 1},
    RARITY_RARE: {"chance": 0.89, "value_mult": 1}
}

CASES = {
    "Грезы и кошмары (300₽)": {
        "price": 300,
        "items": [
            ("AK-47 | Пожелание на ночь", RARITY_COVERT, 3000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09K_k4ifgP7nO4Tdn2xZ_Pp9i_vG8MKliwDh80I-Nmn6INOXIFI5YlqCrwK_ybu90cfovsvOyCBiuiEqtCnfgVXp1iNhGu0F"),
            ("MP9 | Звёздный защитник", RARITY_COVERT, 3000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou6r8FABz7P7YKAJR-N2kmImMn-PLP7LWnn9u5MRjjeyPotXx2g3h_UM_ZGigINTEdw88aVrUqVDvwLvs1J69u5famnVhvClwsGGdwUKxD8sm0Q"),
            ("Dual Berettas | Плод воображения", RARITY_CLASSIFIED, 1000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpos7asPwJf0Ob3dDFL-Nmlq4KOgPbmNoTdn2xZ_Pp9i_vG8MKmiQDh-kRsYmmmJoWScwU4N1GDqQC7kuvmhsTp6cmdwHYyuHEitH7YgVXp1r6aPbAJ"),
            ("MP7 | Дух бездны", RARITY_CLASSIFIED, 1000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou6ryFAR17P7YJgJE6d2kq4yCkP_gDLfQhGxUppQmjL-RrY_w3wSy_0c9NWn6d4fEewRtZFzR_lK-ye7rgZS17cjLnXR9-n51k7vdI74"),
            ("FAMAS | Быстрые движения глаз", RARITY_CLASSIFIED, 1000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposLuoKhRf1OD3dzxP7c-JhoGbnvPLNqLUhVRd4cJ5ntbN9J7yjRrsqkJqZTz1cIWTcwQ_M1nWrgXqku_u15_t78zAzSZm6SUm5C3dzRCxn1gSObQrE_CU"),
            ("USP-S | Билет в ад", RARITY_RESTRICTED, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpoo6m1FBRp3_bGcjhQ09-jq5WYh8jgPITZk2dd18l4jeHVyoD0mlOx5UJvamjxcteUcQ9oY1jV_we5lO3vgZLtvp7NmCZiuyFwty2OyhCziU5SLrs4xNicnZY"),
            ("M4A1-S | Ночной ужас", RARITY_RESTRICTED, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou-6kejhz2v_Nfz5H_uOxh7-Gw_alIITYmHhe5ct4i9bN_Iv9nGu4qgE7NnfxIoPAdFNsaV7Wrla7wL2-05Lu7sjOn3owsnIk5yrZnxXkhE5Mb-Jqm7XAHrs5PyMk"),
            ("G3SG1 | Поляна грёз", RARITY_RESTRICTED, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposem2LFZf0Ob3dm5R642Jk4yKk_LLP7LWnn9u5MRjjeyPrN_w2QPi80ZrYmHwJYWTJAI5YwvY-wO5xO3shJ--tcnOm3di7iNzsWGdwUKZjxvmOg"),
            ("ПП-19 «Бизон» | Космокот", RARITY_RESTRICTED, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpotLO_JAlf0Ob3czRY49KJh5CKlPL3Mq_ummJW4NFOhujT8om7iwa38hE-NWD3LdWRIFJoYwuF-VC5wr27h5K4u5jMwHNkvScj4yuJnAv330-6Hkec3g"),
            ("XM1014 | Зомби-страйк", RARITY_RESTRICTED, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgporrf0e1Y07PLFTiVP08a5mYKCksj7Nb3UmHhY_sBOhuDG_ZjKhFWmrBZyYzzyIdKTe1BsN1GC-QW3wrzugcC5uMvBzCQysiRwti3Zmka_1xxFO_sv26IMuXvssQ"),
            ("MAC-10 | Заточение", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou7umeldf0Ob3fDxBvYyJhImTnvLLP7LWnn9u5MRjjeyPp9qs3QSx-EM5NW6mI4LAdA83Y1iE_Fa3x-u8gZa17pWbwXpquiJx7WGdwULwMeB_qg"),
            ("Five-SeveN | Каракули", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposLOzLhRlxfbGTj5X09q_goWYkuHxPYTQmntZ6fp-h-zG9LP5gVO8vywwMiukcZiTew5qYViE_1K4w--8hMS-v5jBz3dm63F0s3uLmBe-00tMO7FphvWeVxzAUFFwYKtp"),
            ("Sawed-Off | Спиритическая доска", RARITY_MILSPEC, 75, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpopbuyLgNv1fX3cih9_92hkYSEkfHLPK7YnGpu5Mx2gv3--Y3nj1H6_Eo5NmjwLIGTcQE6NwnRrAW8l-7r18PttJnIy3YwuCYnsy3YmhG3hgYMMLKc7wSu3A"),
            ("MP5-SD | Юный некромант", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou6rwOANf1OD3fC0X09e_kL-FkvTmPLXem2JS58tOhuDG_ZjKhFWmrBZya273IIWddQdrY1HZ_lntley80Me-uM7JyCA3uCQjt3zbnRbiiBkYOvsv26JVcvImbA"),
            ("P2000 | Поднятие духов", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovrG1eVcwg8zLZAJSvteJkoySnvnzDL_Dk2pc18l4jeHVyoD0mlOx5Rc-YmqnIdKTcQNrZlqB_wK4leu-15G4vszPnyNg6yF3tnvcnRyzgR1SLrs4oNFBqs8"),
            ("MAG-7 | Предсказание", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgporrf0e1Y07PLFTiVP08a5mYKCksj7Nb3UmHhY_sBOhuDG_ZjKhFWmrBZyYzzyIdKTe1BsN1GC-QW3wrzugcC5uMvBzCQysiRwti3Zmka_1xxFO_sv26IMuXvssQ"),
            ("SCAR-20 | Экзорцыпа", RARITY_MILSPEC, 75, "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpopbmkOVUw7ODYTi5B7c6Jl4iClPzxPb3YkWNF18l4jeHVyoD0mlOx5RFvYT-ncYSSJAZoZV3U_1fsxb3u0JPqvJnAmydl7CQmtyzVmRG-0x9SLrs4w6klS8s"),
            ("Нож-бабочка | Гамма-волны", RARITY_RARE, 300000, "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf0ebcZThQ6tCvq4GGqPD1PrbQqW9e-NV9j_v-5YT0m1HmlB81NDG3OtOcdlM5MF3Srla4wO-8h5PuucyawHo37HZxsXePnEe20xseaLBnhPSACQLJc-o5FQc"),
            ("Нож-бабочка | Легенды", RARITY_RARE, 200000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf0ebcZThQ6tCvq4OeqPXhJ6_UhG1d8fp9hfvEyoHwjF2hpiwwMiukcZjBdVNsZgnYr1i-kOm5gZC5tZqYwHdrs3R05XfYlkGz1R8ZP7Rv0_yeVxzAUFm-H04o"),
            ("Нож-бабочка | Черный глянец", RARITY_RARE, 150000, "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf0ebcZThQ6tCvq4eYqPXhJ6_UhG1d8fpzhujC_rP5iVm9pRIoNgavfdHNNmliMBqHr0-5wufmjZa_6JXPn3RhvCIm5Xnfn0fh1xwaOrBvjaGfHVyfUvMYTafQGDOO51zVYmLG"),
            ("Сергей | Пенкин", RARITY_RARE, 100000, "https://ibb.co/DDZR13fS" ),
            ("Арсений | Морозов", RARITY_RARE, 100000, "https://ibb.co/23SBKfV3" ),
            ("Пестернаков | Илья", RARITY_RARE, 100000, "https://ibb.co/k6wNngJF" )
        ]
    }
}

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if 'last_drop_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['last_drop_id']
            )
        except:
            pass

    await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 1000, "inventory": []}
        save_data(data)

    keyboard = [
        [InlineKeyboardButton("🎁 Открыть кейс", callback_data='select_case')],
        [InlineKeyboardButton("💰 Баланс", callback_data='balance'),
         InlineKeyboardButton("📦 Инвентарь", callback_data='inventory')],
        [InlineKeyboardButton("📤 Вывод предметов", callback_data='withdraw_items')],
        [InlineKeyboardButton("🎰 Ежедневный бонус", callback_data='daily_bonus')],
        [InlineKeyboardButton("🆘 О боте", callback_data='help')],
    ]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🔫 CS2 SKIN-HUNTER BOT\n\n"
            f"💰 Баланс: {users_db[user_id]['balance']}₽\n"
            f"📦 Предметов: {len(users_db[user_id]['inventory'])}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "🔫 CS2 SKIN-HUNTER BOT\n\n"
            f"💰 Баланс: {users_db[user_id]['balance']}₽\n"
            f"📦 Предметов: {len(users_db[user_id]['inventory'])}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def select_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Грезы и кошмары (300₽)", callback_data='open_case_Грезы и кошмары (300₽)')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
    ]

    await query.edit_message_text(
        "🎁 Выберите кейс для открытия:",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('current_handler', None)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("❌ Операция отменена.")
    elif update.message:
        await update.message.reply_text("❌ Операция отменена.")

    return ConversationHandler.END

async def process_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        user_id = update.effective_user.id

        if amount < 10:
            await update.message.reply_text("❌ Минимальная сумма - 10₽")
            return ENTER_DEPOSIT_AMOUNT
        if amount > 100000:
            await update.message.reply_text("❌ Максимальная сумма - 100000₽")
            return ENTER_DEPOSIT_AMOUNT

        users_db[user_id]["balance"] += amount
        save_data(data)

        await update.message.reply_text(
            f"✅ Баланс пополнен на {amount}₽\n"
            f"💰 Текущий баланс: {users_db[user_id]['balance']}₽",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')]
            ])
        )
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "❌ Введите число (например: 1000)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='balance')]
            ])
        )
        return ENTER_DEPOSIT_AMOUNT

def create_deposit_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(deposit_start, pattern='^deposit$')],
        states={
            WAITING_DEPOSIT_AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    process_deposit
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_operation),
            CallbackQueryHandler(cancel_operation, pattern='^cancel_operation$')
        ],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END
        },
        per_message=True
    )

def create_support_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler('support', support_command),
            CallbackQueryHandler(support_command, pattern='^ask_support$')
        ],
        states={
            WAITING_SUPPORT_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_support_message
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_operation),
            CallbackQueryHandler(cancel_operation, pattern='^cancel_operation$')
        ],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END
        },
        per_message=True
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_handler'] = 'support'

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "✍️ Напишите ваше сообщение в техподдержку:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data='cancel_operation')]
            ])
        )
    else:
        await update.message.reply_text(
            "✍️ Напишите ваше сообщение в техподдержку:",
            reply_markup=ReplyKeyboardRemove()
        )

    return WAITING_SUPPORT_MESSAGE

async def cancel_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('support_started_from_button', None)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("❌ Отправка сообщения отменена.")
    elif update.message:
        await update.message.reply_text("❌ Отправка сообщения отменена.")

    return ConversationHandler.END

async def start_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_support'] = True

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "✍️ Напишите ваше сообщение в техподдержку. Мы ответим в ближайшее время.\n\n"
            "Для отмены нажмите кнопку ниже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отменить", callback_data='cancel_support')]
            ])
        )
    else:
        await update.message.reply_text(
            "✍️ Напишите ваше сообщение в техподдержку. Мы ответим в ближайшее время.\n\n"
            "Для отмены используйте /cancel",
            reply_markup=ReplyKeyboardRemove()
        )

    return WAITING_SUPPORT_MESSAGE

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('support_started_from_button', None)

    user = update.effective_user
    message_text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆘 Поддержка от {user.full_name} (@{user.username}, ID: {user.id}):\n\n{message_text}"
    )

    await update.message.reply_text(
        "✅ Ваше сообщение отправлено в техподдержку!",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def withdraw_items_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if not users_db[user_id]["inventory"]:
        await query.edit_message_text(
            "❌ Ваш инвентарь пуст!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
            ]))
        return

    if user_id in TRADE_LINK:
        await withdraw_items_start(update, context)
        return

    await query.edit_message_text(
        "📤 Для вывода предметов введите вашу трейд-ссылку Steam:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
        ]))
    return ENTER_TRADE_LINK

async def withdraw_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    item_index = int(query.data.split('_')[1])
    item, rarity, value, *_ = users_db[user_id]["inventory"].pop(item_index)
    save_data(data)

async def enter_trade_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    trade_link = update.message.text

    if "steamcommunity.com/tradeoffer" not in trade_link:
        await update.message.reply_text(
            "❌ Неверная трейд-ссылка! Пример: https://steamcommunity.com/tradeoffer/...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
            ]))
        return ENTER_TRADE_LINK

    TRADE_LINK[user_id] = trade_link
    data['trade_links'] = TRADE_LINK
    save_data(data)

    await update.message.reply_text(
        "✅ Трейд-ссылка сохранена!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Вывод предметов", callback_data='withdraw_items')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
        ]))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🎁 Открыть кейс", callback_data='select_case')],
        [InlineKeyboardButton("💰 Баланс", callback_data='balance'),
         InlineKeyboardButton("📦 Инвентарь", callback_data='inventory')],
        [InlineKeyboardButton("📤 Вывод предметов", callback_data='withdraw_items')],
        [InlineKeyboardButton("🎰 Ежедневный бонус", callback_data='daily_bonus')],
        [InlineKeyboardButton("🆘 Помощь", callback_data='help')],
    ]

    await safe_edit_or_send_text(
        query,
        context,
        "🔫 CS2 Case Bot\n\n"
        f"💰 Баланс: {users_db[user_id]['balance']}₽\n"
        f"📦 Предметов: {len(users_db[user_id]['inventory'])}",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if user_id not in users_db:
        users_db[user_id] = {"balance": 0, "inventory": []}
        save_data(data)

    keyboard = [
        [InlineKeyboardButton("💳 Пополнить баланс", callback_data='deposit')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
    ]

    await query.edit_message_text(
        f"💰 Ваш баланс: {users_db[user_id]['balance']}₽\n"
        f"📦 Предметов: {len(users_db[user_id]['inventory'])}",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['current_handler'] = 'deposit'

    await query.edit_message_text(
        "💳 Введите сумму для пополнения (от 10 до 100000₽):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data='cancel_operation')]
        ])
    )
    return WAITING_DEPOSIT_AMOUNT

async def open_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    case_name = query.data.split('_', 2)[2]

    if case_name not in CASES:
        await safe_edit_or_send_text(
            query,
            context,
            f"❌ Кейс '{case_name}' не найден.",
            reply_markup=None
        )
        return

    case_data = CASES[case_name]

    if users_db[user_id]["balance"] < case_data["price"]:
        await safe_edit_or_send_text(
            query,
            context,
            f"❌ Недостаточно средств! Нужно {case_data['price']}₽",
            reply_markup=None
        )
        return

    users_db[user_id]["balance"] -= case_data["price"]

    items = case_data["items"]
    weights = [RARITIES[item[1]]["chance"] for item in items]

    selected_item = random.choices(items, weights=weights, k=1)[0]
    name, rarity, value, image_url = selected_item

    users_db[user_id]["inventory"].append((name, rarity, value, image_url))
    save_data(data)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_url,
        caption=(
            f"🎉 Вы получили из {case_name}:\n"
            f"{rarity} {name}\n"
            f"💵 Стоимость: {value}₽\n\n"
            f"💰 Баланс: {users_db[user_id]['balance']}₽\n"
            f"📦 Инвентарь: {len(users_db[user_id]['inventory'])} предметов"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Открыть еще раз", callback_data=f'open_case_{case_name}')],
            [InlineKeyboardButton("📦 Инвентарь", callback_data='new_inventory')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
        ])
    )
async def show_inventory_from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await send_inventory_message(update.effective_chat.id, context)


async def send_inventory_message(chat_id, context):
    user_id = context._user_id
    inventory = users_db[user_id]["inventory"]

    if not inventory:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📦 Ваш инвентарь пуст!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
            ])
        )
        return


    chunk_size = 15
    chunks = [inventory[i:i + chunk_size] for i in range(0, len(inventory), chunk_size)]

    await send_inventory_page(chat_id, context, chunks, 0)


async def send_inventory_page(chat_id, context, chunks, page):

    text = f"📦 Ваш инвентарь (страница {page + 1}/{len(chunks)}):\n\n"
    for idx, item in enumerate(chunks[page], 1):
        name, rarity, value, *_ = item
        text += f"{idx}. {name} ({rarity}) — {value}₽\n"


    buttons = []
    if len(chunks) > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f'inv_page_{page - 1}'))
        nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{len(chunks)}", callback_data='page_info'))
        if page < len(chunks) - 1:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f'inv_page_{page + 1}'))
        buttons.append(nav_buttons)

    buttons.extend([
        [InlineKeyboardButton("💵 Продать все", callback_data='sell_all')],
        [InlineKeyboardButton("🔎 Выбрать предметы", callback_data='select_items')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
    ])


    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def safe_edit_or_send_text(query, context, text, reply_markup=None):
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if "message to edit" in str(e):
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=reply_markup)
        else:
            raise


async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    inventory = users_db[user_id]["inventory"]
    if not inventory:
        await query.edit_message_text(
            "📦 Ваш инвентарь пуст!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
            ])
        )
        return

    chunk_size = 20
    inventory_chunks = [inventory[i:i + chunk_size] for i in range(0, len(inventory), chunk_size)]


    await send_inventory_chunk(query, context, inventory_chunks, 0)


async def handle_inventory_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    page_index = int(query.data.split('_')[2])
    inventory = users_db[user_id]["inventory"]
    chunk_size = 20
    chunks = [inventory[i:i + chunk_size] for i in range(0, len(inventory), chunk_size)]

    await send_inventory_chunk(query, context, chunks, page_index)


async def send_inventory_chunk(query, context, chunks, chunk_index):
    current_chunk = chunks[chunk_index]
    text = "📦 Ваш инвентарь:\n\n"

    for idx, (item, rarity, value, *_) in enumerate(current_chunk, 1):
        text += f"{idx}. {item} ({rarity}) — {value}₽\n"

    keyboard = []
    if len(chunks) > 1:
        if chunk_index > 0:
            keyboard.append(
                [InlineKeyboardButton("⬅️ Предыдущая страница", callback_data=f'inv_page_{chunk_index - 1}')])
        if chunk_index < len(chunks) - 1:
            keyboard.append(
                [InlineKeyboardButton("➡️ Следующая страница", callback_data=f'inv_page_{chunk_index + 1}')])

    keyboard.extend([
        [InlineKeyboardButton("💵 Продать все", callback_data='sell_all')],
        [InlineKeyboardButton("🔎 Выбрать предметы", callback_data='select_items_to_sell')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def toggle_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    item_index = int(query.data.split('_')[1])


    selected_items = context.user_data.setdefault('selected_items', [])

    if item_index in selected_items:
        selected_items.remove(item_index)
    else:
        selected_items.append(item_index)


    inventory = users_db[user_id]["inventory"]
    keyboard = []
    for idx, (item, rarity, value, *_) in enumerate(inventory, 1):
        is_selected = (idx - 1) in selected_items
        emoji = "✅" if is_selected else "❌"
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {idx}. {item} ({value}₽)",
            callback_data=f'toggle_{idx - 1}'
        )])

    keyboard.append([InlineKeyboardButton("💰 Продать выбранное", callback_data='confirm_sell')])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data='inventory')])

    await query.edit_message_text(
        "🔎 Выберите предметы для продажи (нажмите на предмет, чтобы отметить):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELL_SELECTED

async def confirm_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if 'selected_items' not in context.user_data or not context.user_data['selected_items']:
        await query.edit_message_text(
            "❌ Вы не выбрали ни одного предмета!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='select_items_to_sell')]
            ])
        )
        return SELL_SELECTED

    total = 0

    for index in sorted(context.user_data['selected_items'], reverse=True):
        if 0 <= index < len(users_db[user_id]["inventory"]):
            total += users_db[user_id]["inventory"][index][2]
            del users_db[user_id]["inventory"][index]

    users_db[user_id]["balance"] += total
    save_data(data)
    context.user_data['selected_items'] = []

    await query.edit_message_text(
        f"✅ Продано предметов на сумму: {total}₽\n"
        f"💰 Новый баланс: {users_db[user_id]['balance']}₽",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В инвентарь", callback_data='inventory')]
        ])
    )
    return ConversationHandler.END


async def select_items_to_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    context.user_data.setdefault('selected_items', [])
    inventory = users_db[user_id]["inventory"]

    if not inventory:
        await query.edit_message_text(
            "❌ Ваш инвентарь пуст!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='inventory')]
            ])
        )
        return ConversationHandler.END

    keyboard = []
    for idx, (item, rarity, value, *_) in enumerate(inventory, 1):
        is_selected = (idx - 1) in context.user_data['selected_items']
        emoji = "✅" if is_selected else "❌"
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {idx}. {item} ({value}₽)",
            callback_data=f'toggle_{idx - 1}'
        )])

    keyboard.append([InlineKeyboardButton("💰 Продать выбранное", callback_data='confirm_sell')])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data='inventory')])

    await query.edit_message_text(
        "🔎 Выберите предметы для продажи:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELL_SELECTED

async def sell_all_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    total = sum(item[2] for item in users_db[user_id]["inventory"])
    users_db[user_id]["balance"] += total
    users_db[user_id]["inventory"] = []
    save_data(data)

    await query.edit_message_text(
        f"✅ Все предметы проданы за {total}₽\n"
        f"💰 Новый баланс: {users_db[user_id]['balance']}₽",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')]
        ])
    )
    return ConversationHandler.END


async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    now = time.time()
    last_bonus = LAST_DAILY_BONUS.get(user_id, 0)

    if now - last_bonus < 24 * 60 * 60:
        await query.edit_message_text(
            "❌ Вы уже получали бонус сегодня!\n"
            "Приходите завтра.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
            ])
        )
        return

    bonus = random.randint(50, 300)
    users_db[user_id]["balance"] += bonus
    LAST_DAILY_BONUS[user_id] = now
    data['last_daily_bonus'] = LAST_DAILY_BONUS
    save_data(data)

    await query.edit_message_text(
        f"🎉 Вы получили ежедневный бонус: {bonus}₽\n"
        f"💰 Новый баланс: {users_db[user_id]['balance']}₽",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')]
        ])
    )


async def handle_unexpected_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_handler = context.user_data.get('current_handler')

    if current_handler == 'deposit':
        return await process_deposit(update, context)
    elif current_handler == 'support':
        return await handle_support_message(update, context)

    await update.message.reply_text(
        "Я не понимаю эту команду. Используйте /start для основного меню.",
        reply_markup=ReplyKeyboardRemove()
    )


async def cancel_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("❌ Пополнение баланса отменено.")
    elif update.message:
        await update.message.reply_text("❌ Пополнение баланса отменено.")

    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        "ℹ️ Помощь по боту:\n\n"
        "🎁 Открыть кейс - покупайте кейсы и получайте случайные предметы\n"
        "💰 Баланс - просмотр текущего баланса и пополнение\n"
        "📦 Инвентарь - просмотр ваших предметов\n"
        "💵 Продать предметы - продажа предметов из инвентаря\n"
        "📤 Вывод предметов - вывод предметов в Steam\n"
        "🎰 Ежедневный бонус - получайте бонус раз в 24 часа\n\n"
        "По всем вопросам обращайтесь к @jkss_onion"
    )

    await query.edit_message_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]
        ])
    )


async def support_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


    context.user_data['support_started_from_button'] = True

    await query.edit_message_text(
        "✍️ Напишите ваше сообщение в техподдержку. Мы ответим в ближайшее время.\n\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отменить", callback_data='cancel_support')]
        ])
    )
    return WAITING_SUPPORT_MESSAGE

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if 'awaiting_support' in context.user_data:
        return await cancel_support(update, context)

    await update.message.reply_text(
        "❌ Нет активных операций для отмены.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /reply <user_id> <сообщение>")
        return

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📨 Ответ от поддержки:\n\n{message}"
        )
        await update.message.reply_text("✅ Ответ отправлен пользователю")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", start_support))
    application.add_handler(CommandHandler("reply", admin_reply))


    application.add_handler(CallbackQueryHandler(select_case, pattern='^select_case$'))
    application.add_handler(CallbackQueryHandler(open_case, pattern='^open_case_'))
    application.add_handler(CallbackQueryHandler(show_inventory, pattern='^inventory$'))
    application.add_handler(CallbackQueryHandler(show_balance, pattern='^balance$'))
    application.add_handler(CallbackQueryHandler(daily_bonus, pattern='^daily_bonus$'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    application.add_handler(CallbackQueryHandler(sell_all_items, pattern='^sell_all$'))
    application.add_handler(CallbackQueryHandler(handle_inventory_page, pattern='^inv_page_'))
    application.add_handler(CallbackQueryHandler(show_inventory_from_photo, pattern='^new_inventory$'))
    application.add_handler(CallbackQueryHandler(support_button, pattern='^ask_support$'))
    application.add_handler(CallbackQueryHandler(cancel_support, pattern='^cancel_support$'))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(select_case, pattern='^select_case$'))

    deposit_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(deposit_start, pattern='^deposit$')],
        states={
            ENTER_DEPOSIT_AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    process_deposit
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_deposit),
            CallbackQueryHandler(cancel_deposit, pattern='^cancel_deposit$')
        ],
        per_message=True,
        allow_reentry=True
    )


    support_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('support', start_support),
            CallbackQueryHandler(start_support, pattern='^ask_support$')
        ],
        states={
            WAITING_SUPPORT_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_support_message
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_support),
            CallbackQueryHandler(cancel_support, pattern='^cancel_support$'),
            MessageHandler(filters.REPLY, handle_support_message)
        ],
        per_message=True,
        allow_reentry=True
    )
    application.add_handler(support_conv_handler)

    withdraw_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(withdraw_items_start, pattern='^withdraw_items$')],
        states={
            ENTER_TRADE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_trade_link)],
            SELECT_ITEM: [CallbackQueryHandler(withdraw_item, pattern='^withdraw_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True
    )

    support_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('support', start_support),
            CallbackQueryHandler(support_button, pattern='^ask_support$')
        ],
        states={
            WAITING_SUPPORT_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_support_message
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_support),
            CallbackQueryHandler(cancel_support, pattern='^cancel_support$')
        ],
        per_message=True,
        allow_reentry=True
    )

    application.add_handler(deposit_conv_handler)
    application.add_handler(withdraw_conv_handler)
    application.add_handler(support_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unexpected_text))

    print("WW")
    application.run_polling()

if __name__ == '__main__':
    main()