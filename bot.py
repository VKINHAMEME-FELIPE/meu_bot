from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler, CallbackContext, JobQueue
from flask import Flask, request, jsonify
import logging
from deep_translator import GoogleTranslator
import asyncio
import os

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configurações do Telegram
TOKEN = '7852634722:AAFPO4V3-6w4NMmUxNatzz4EedyMrE8Mv6w'
GROUP_CHAT_ID = '-1002405955713'
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://meu-bot1.onrender.com')  # Substitua pelo URL do Render
PORT = int(os.getenv('PORT', 8443))

# Inicializa Flask
app = Flask(__name__)

# Inicializa o bot
application = Application.builder().token(TOKEN).build()

def translate_message(text, dest_language='en'):
    supported_languages = ['pt', 'en', 'es']
    if dest_language not in supported_languages:
        dest_language = 'en'
    return GoogleTranslator(source='auto', target=dest_language).translate(text)

# Função para verificar membresia
async def verify_telegram_membership(user_id: int) -> dict:
    try:
        chat_member = await application.bot.get_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return {"status": True, "message": "Verification successful! The user is in the group."}
        else:
            return {"status": False, "message": f"The user is not in the group. Please join the group with ID {GROUP_CHAT_ID} and try again."}
    except Exception as e:
        logger.error(f"Error verifying membership: {e}")
        return {"status": False, "message": "Error verifying membership. Please try again later."}

# Endpoint para o site verificar membresia
@app.route('/verify', methods=['POST'])
async def verify_membership():
    data = request.json
    username = data.get('username')
    
    if not username or not username.startswith('@'):
        return jsonify({"status": False, "message": "Please provide a valid Telegram username (e.g., @username)."}), 400

    try:
        # Obtém informações do usuário pelo username
        chat_member = await application.bot.get_chat_member(chat_id=GROUP_CHAT_ID, user_id=username[1:])  # Remove '@'
        result = await verify_telegram_membership(chat_member.user.id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching user info for {username}: {e}")
        return jsonify({"status": False, "message": "User not found or error occurred. Please ensure the username is correct."}), 404

# Handlers do Telegram
async def welcome(update: Update, context: CallbackContext):
    try:
        if update.message.new_chat_members:
            lang = update.message.from_user.language_code[:2].lower() if update.message.from_user.language_code else 'en'
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\n\n".join([
                    translate_message("Welcome to our official VKINHA community!", lang),
                    translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", lang),
                    translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", lang)
                ])
            )
            keyboard = [
                [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                [InlineKeyboardButton("Pre-Sale", callback_data="pre_sale")],
                [InlineKeyboardButton("Site", url="https://www.vkinha.com.br")],
                [InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")],
                [InlineKeyboardButton("X", url="https://x.com/vkinhacoin")]
            ]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=translate_message("Choose an option:", lang),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
    except Exception as e:
        logger.error(f"Error in welcome: {e}")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'pre_sale':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pre-sale is scheduled to start on DxSale on 03/30/2025."
        )

async def send_periodic_messages(context: CallbackContext):
    messages = [
        {"text": "🌟 VKINHA Update: Stay informed about our project! Visit our official website: https://www.vkinha.com.br 🌟", "keyboard": None},
        {"text": "🌟 VKINHA Update: Did you know the pre-sale on DxSale is set up?", "keyboard": [[InlineKeyboardButton("Click here!", url="https://www.dx.app/dxsale/view?address=0x0597Ce945ED83C81AdC47c97139B5602ddb03c69&chain=56")]]},
        {"text": "Did you know we are partnering with:", "keyboard": [
            [InlineKeyboardButton("Azbit", url="https://azbit.com"), InlineKeyboardButton("Bifinance", url="https://bifinance.com")],
            [InlineKeyboardButton("CertiK", url="https://www.certik.com"), InlineKeyboardButton("Gate.io", url="https://www.gate.io")],
            [InlineKeyboardButton("Cryptopix", url="https://cryptopix.com")]
        ]},
        {"text": "Follow us on Instagram:", "keyboard": [[InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")]]},
        {"text": "Do you know our X (Twitter) profile?", "keyboard": [[InlineKeyboardButton("Twitter", url="https://x.com/vkinhacoin")]]},
        {"text": "Have you seen our CODE? Check it out, it’s verified and audited:", "keyboard": [[InlineKeyboardButton("BSCScan", url="https://bscscan.com/address/0x7Bd2024cAd405ccA960fE9989334A70153c41682#code")]]},
        {"text": "Support our community! Drop a 🔥 on the DX site to boost our token!", "keyboard": None},
        {"text": "Thank you for supporting VKINHA.", "keyboard": None},
        {"text": "Did you know we will support projects that help lives?", "keyboard": None},
        {"text": "Check out our Roadmap:", "keyboard": [[InlineKeyboardButton("Roadmap Link", url="https://vkinha.com/roadmap.html")]]}
    ]

    if "message_ids" not in context.bot_data:
        context.bot_data["message_ids"] = []
    if "current_message_index" not in context.bot_data:
        context.bot_data["current_message_index"] = 0

    index = context.bot_data["current_message_index"]
    message_data = messages[index]

    try:
        sent_message = await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message_data["text"],
            reply_markup=InlineKeyboardMarkup(message_data["keyboard"]) if message_data["keyboard"] else None
        )
        context.bot_data["message_ids"].append(sent_message.message_id)

        if len(context.bot_data["message_ids"]) > 3:
            old_msg = context.bot_data["message_ids"].pop(0)
            await context.bot.delete_message(
                chat_id=GROUP_CHAT_ID,
                message_id=old_msg
            )

        context.bot_data["current_message_index"] = (index + 1) % len(messages)
    except Exception as e:
        logger.error(f"Error sending periodic message: {e}")

# Webhook handler
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return '', 200

def setup_handlers():
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))

async def main():
    # Configura handlers
    setup_handlers()

    # Configura o webhook
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # Agenda mensagens periódicas
    job_queue = application.job_queue
    job_queue.run_repeating(
        callback=send_periodic_messages,
        interval=900,  # 15 minutos
        first=10       # Inicia após 10 segundos
    )

    # Inicia o Flask
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    # Inicia o loop asyncio
    asyncio.run(main())