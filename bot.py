from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler, CallbackContext, JobQueue
import logging
from deep_translator import GoogleTranslator
import asyncio
from aiohttp import web
import json

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7852634722:AAFPO4V3-6w4NMmUxNatzz4EedyMrE8Mv6w'
GROUP_CHAT_ID = '-1002405955713'  # ID do seu grupo
PORT = 8080  # Porta que o Render espera
WEBHOOK_URL = 'https://seu-app.render.com/webhook'  # Substitua por sua URL do Render

def translate_message(text, dest_language='en'):
    supported_languages = ['pt', 'en', 'es']
    if dest_language not in supported_languages:
        dest_language = 'en'
    return GoogleTranslator(source='auto', target=dest_language).translate(text)

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
            text="Pre-sale scheduled to start on DxSale on 03/30/2025"
        )

async def send_periodic_messages(context: CallbackContext):
    messages = [
        {"text": "🌟 VKINHA Update: Stay updated on our project! Visit our official website: https://www.vkinha.com.br 🌟", "keyboard": None},
        {"text": "🌟 VKINHA Update: Did you know that the pre-sale on DxSale is set up?", "keyboard": [[InlineKeyboardButton("Click here!", url="https://www.dx.app/dxsale/view?address=0x0597Ce945ED83C81AdC47c97139B5602ddb03c69&chain=56")]]},
        {"text": "Did you know we are partnering with:", "keyboard": [[InlineKeyboardButton("Azbit", url="https://azbit.com"), InlineKeyboardButton("Bifinance", url="https://bifinance.com")], [InlineKeyboardButton("CertiK", url="https://www.certik.com"), InlineKeyboardButton("Gate.io", url="https://www.gate.io")], [InlineKeyboardButton("Cryptopix", url="https://cryptopix.com")]]},
        {"text": "Follow our Instagram profile:", "keyboard": [[InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")]]},
        {"text": "Do you know our X (Twitter) profile?", "keyboard": [[InlineKeyboardButton("Twitter", url="https://x.com/vkinhacoin")]]},
        {"text": "Have you seen our CODE? Check it out, it’s verified and audited:", "keyboard": [[InlineKeyboardButton("BSCScan", url="https://bscscan.com/address/0x7Bd2024cAd405ccA960fE9989334A70153c41682#code")]]},
        {"text": "Support our community! Leave your 🔥 on the DX site to boost our token!", "keyboard": None},
        {"text": "Thank you for supporting VKINHA.", "keyboard": None},
        {"text": "Did you know we will support projects that help lives?", "keyboard": None},
        {"text": "Check out our Roadmap:", "keyboard": [[InlineKeyboardButton("Roadmap Link", url="https://vkinha.com/roadmap.html")]]}
    ]

    if "message_ids" not in context.bot_data:
        context.bot_data["message_ids"] = []
    if "current_message_index" not in context.bot_data:
        context.bot_data["current_message_index"] = 0

    while True:
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
            await asyncio.sleep(900)

        except Exception as e:
            logger.error(f"Error in periodic messages: {e}")
            await asyncio.sleep(900)

async def get_chat_id(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

# Função para lidar com requisições webhook
async def webhook_handler(request):
    app = request.app['telegram_app']
    update = Update.de_json(json.loads(await request.text()), app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

async def setup_webhook(application):
    # Remove qualquer webhook existente e configura o novo
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

async def main():
    # Cria a aplicação Telegram
    application = Application.builder().token(TOKEN).build()

    # Adiciona handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("chatid", get_chat_id))

    # Agenda mensagens periódicas
    job_queue = application.job_queue
    job_queue.run_repeating(
        callback=send_periodic_messages,
        interval=900,  # 15 minutos
        first=5,  # Inicia após 5 segundos
        chat_id=GROUP_CHAT_ID
    )

    # Configura o servidor web com aiohttp
    app = web.Application()
    app['telegram_app'] = application
    app.router.add_post('/webhook', webhook_handler)

    # Inicializa a aplicação Telegram
    await application.initialize()
    await setup_webhook(application)
    await application.start()

    # Inicia o servidor web
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    logger.info(f"Server running on port {PORT}")
    
    # Mantém o loop rodando
    while True:
        await asyncio.sleep(3600)  # Mantém o processo ativo

if __name__ == '__main__':
    asyncio.run(main())