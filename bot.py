from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler
import logging
from deep_translator import GoogleTranslator
import asyncio

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7852634722:AAFPO4V3-6w4NMmUxNatzz4EedyMrE8Mv6w'

def translate_message(text, dest_language):
    supported_languages = ['pt', 'en', 'es']
    if dest_language not in supported_languages:
        dest_language = 'en'
    translator = GoogleTranslator(source='auto', target=dest_language)
    return translator.translate(text)

async def welcome(update: Update, context):
    logger.info(f"Novo membro detectado: {update.message.new_chat_members}")
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            try:
                language = update.message.from_user.language_code or 'en'
                language = language[:2].lower()
                logger.info(f"Processando membro: {member.username} - Idioma: {language}")

                welcome_message = translate_message("Welcome to our official VKINHA community!", language)
                warning_message = translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", language)
                admin_message = translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", language)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{welcome_message}\n\n{warning_message}\n\n{admin_message}"
                )

                keyboard = [
                    [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                    [InlineKeyboardButton("Pre-Sale", callback_data="pre_sale")],
                    [InlineKeyboardButton("Site", url="https://www.vkinha.com.br")],
                    [InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")],
                    [InlineKeyboardButton("X", url="https://x.com/vkinhacoin")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Escolha uma opção:",
                    reply_markup=reply_markup
                )

                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except Exception as e:
                logger.error(f"Erro ao processar novo membro: {e}")

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'pre_sale':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pre-sale prevista para começar na dxsale no dia 30/03/2025"
        )

async def start(update: Update, context):
    await update.message.reply_text("Bot está funcionando!")
    logger.info("Comando /start recebido")

async def set_webhook(application):
    webhook_url = f"https://meu-bot-t.onrender.com/{TOKEN}"
    await application.bot.setWebhook(webhook_url)
    logger.info(f"Webhook configurado para: {webhook_url}")

async def main():
    logger.info("Iniciando o bot...")
    application = Application.builder().token(TOKEN).build()

    # Adiciona os handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Configura o webhook
    await set_webhook(application)

    # Inicia o bot em modo webhook
    await application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"https://meu-bot-t.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    asyncio.run(main())