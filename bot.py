from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler, CallbackContext, JobQueue
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
GROUP_CHAT_ID = '-1002405955713'  # ID do grupo atualizado

def translate_message(text, dest_language='en'):
    supported_languages = ['pt', 'en', 'es']
    if dest_language not in supported_languages:
        dest_language = 'en'
    return GoogleTranslator(source='auto', target=dest_language).translate(text)

async def welcome(update: Update, context: CallbackContext):
    try:
        if update.message.new_chat_members:
            lang = update.message.from_user.language_code[:2].lower() if update.message.from_user.language_code else 'en'
            
            # Mensagem de boas-vindas
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\n\n".join([
                    translate_message("Welcome to our official VKINHA community!", lang),
                    translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", lang),
                    translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", lang)
                ])
            )

            # Teclado interativo
            keyboard = [
                [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                [InlineKeyboardButton("Pre-Sale", callback_data="pre_sale")],
                [InlineKeyboardButton("Site", url="https://www.vkinha.com.br")],
                [InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")],
                [InlineKeyboardButton("X", url="https://x.com/vkinhacoin")]
            ]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=translate_message("Escolha uma opção:", lang),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
    except Exception as e:
        logger.error(f"Erro no welcome: {e}")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'pre_sale':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pre-sale prevista para começar na dxsale no dia 30/03/2025"
        )

async def send_periodic_message(context: CallbackContext):
    try:
        message = translate_message("🌟 Atualização VKINHA: Fique por dentro do nosso projeto! Visite nosso site oficial: https://www.vkinha.com.br 🌟", 'pt')
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message
        )
        logger.info("Mensagem periódica enviada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem periódica: {e}")

async def get_chat_id(update: Update, context: CallbackContext):
    await update.message.reply_text(f"ID deste chat: {update.effective_chat.id}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Configuração do JobQueue
    job_queue = application.job_queue
    job_queue.run_repeating(
        send_periodic_message,
        interval=900,
        first=10
    )

    # Handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("chatid", get_chat_id))

    # ✅ Modo Webhook (obrigatório no Render)
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"https://meu-bot-t.onrender.com/{TOKEN}"
    )


if __name__ == '__main__':
    main()