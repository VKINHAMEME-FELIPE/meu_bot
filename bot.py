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
    return GoogleTranslator(source='auto', target=dest_language).translate(text)

async def welcome(update: Update, context):
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            try:
                language = update.message.from_user.language_code[:2].lower() if update.message.from_user.language_code else 'en'
                
                # Mensagem de boas-vindas
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="\n\n".join([
                        translate_message("Welcome to our official VKINHA community!", language),
                        translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", language),
                        translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", language)
                    ])
                )

                # Teclado
                keyboard = [
                    [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                    [InlineKeyboardButton("Site", url="https://www.vkinha.com.br")],
                    [InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")],
                    [InlineKeyboardButton("X", url="https://x.com/vkinhacoin")]
                ]
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=translate_message("Escolha uma opção:", language),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except Exception as e:
                logger.error(f"Erro: {e}")

async def send_periodic_messages(context):
    messages = [
        "Visite nosso site: www.vkinha.com",
        "O Projeto é novo visualize melhor nosso RoadMap",
        "Vocês já seguem nosso Twitter(X) ou Instagram?",
        "Já está programado a pré-venda DxSale",
        "Parcerias com Azbit, CryptoPix, Bifinance, Byconomy, CertiK e Gate.io"
    ]

    if "message_ids" not in context.bot_data:
        context.bot_data["message_ids"] = []

    for text in messages:
        sent_message = await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=text
        )
        context.bot_data["message_ids"].append(sent_message.message_id)

        # Apaga a mensagem mais antiga após 3 mensagens
        if len(context.bot_data["message_ids"]) > 3:
            try:
                await context.bot.delete_message(
                    chat_id=context.job.chat_id,
                    message_id=context.bot_data["message_ids"].pop(0)
                )
            except Exception as e:
                logger.error(f"Erro ao deletar mensagem: {e}")

        await asyncio.sleep(900)  # 15 minutos

def main():
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Agenda mensagens periódicas
    application.job_queue.run_once(
        callback=lambda ctx: send_periodic_messages(ctx),
        when=5,
        chat_id=-1001234567890  # Substitua pelo ID real do seu grupo
    )

    # Inicia o bot em modo polling
    application.run_polling()

if __name__ == '__main__':
    main()
from telegram.ext import CommandHandler

async def get_chat_id(update: Update, context):
    await update.message.reply_text(f"ID do Grupo: {update.effective_chat.id}")

def main():
    # ... (código existente)
    application.add_handler(CommandHandler("chatid", get_chat_id))