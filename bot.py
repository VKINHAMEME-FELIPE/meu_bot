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

async def send_periodic_messages(application):
    messages = [
        {
            "text": "Visite nosso site: www.vkinha.com",
            "keyboard": []
        },
        {
            "text": "O Projeto é novo visualize melhor nosso RoadMap",
            "keyboard": [[InlineKeyboardButton("RoadMap", url="https://vkinha.com/roadmap.html")]]
        },
        {
            "text": "Vocês já seguem nosso Twitter(X) ou Instagram?",
            "keyboard": [
                [InlineKeyboardButton("Twitter(X)", url="https://x.com/vkinhacoin")],
                [InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")]
            ]
        },
        {
            "text": "Já está programado a pré-venda DxSale\nClique em: Leave some votes and get this sale trending! no DxSale e deixe seu apoio",
            "keyboard": [[InlineKeyboardButton("DxSale", url="https://www.dx.app/dxsale/view?address=0x0597Ce945ED83C81AdC47c97139B5602ddb03c69&chain=56")]]
        },
        {
            "text": "Você viu que estamos com parcerias sendo desenvolvidas com Azbit, CryptoPix, Bifinance, Byconomy, CertiK e Gate.io",
            "keyboard": [
                [InlineKeyboardButton("Azbit", url="https://azbit.com"), InlineKeyboardButton("CryptoPix", url="https://cryptopix.com")],
                [InlineKeyboardButton("Bifinance", url="https://bifinance.com"), InlineKeyboardButton("Byconomy", url="https://byconomy.com")],
                [InlineKeyboardButton("CertiK", url="https://certik.com"), InlineKeyboardButton("Gate.io", url="https://gate.io")]
            ]
        }
    ]

    if "message_ids" not in application.bot_data:
        application.bot_data["message_ids"] = []

    message_index = 0
    total_messages = len(messages)

    while True:
        try:
            chat_id = application.bot_data.get("chat_id")
            if not chat_id:
                logger.warning("Nenhum chat_id definido para mensagens periódicas.")
                await asyncio.sleep(900)
                continue

            language = application.bot_data.get("language", "en")
            translated_text = translate_message(messages[message_index]["text"], language)
            reply_markup = InlineKeyboardMarkup(messages[message_index]["keyboard"]) if messages[message_index]["keyboard"] else None

            if message_index >= 2 and len(application.bot_data["message_ids"]) >= 2:
                message_to_delete = application.bot_data["message_ids"].pop(0)
                try:
                    await application.bot.delete_message(chat_id=chat_id, message_id=message_to_delete)
                    logger.info(f"Mensagem {message_to_delete} deletada para evitar flood.")
                except Exception as e:
                    logger.error(f"Erro ao deletar mensagem {message_to_delete}: {e}")

            sent_message = await application.bot.send_message(
                chat_id=chat_id,
                text=translated_text,
                reply_markup=reply_markup
            )
            application.bot_data["message_ids"].append(sent_message.message_id)
            logger.info(f"Mensagem enviada: {translated_text}, ID: {sent_message.message_id}")

            message_index = (message_index + 1) % total_messages
            await asyncio.sleep(900)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem periódica: {e}")
            await asyncio.sleep(900)

async def post_init(application):
    """Função chamada após a inicialização do Application para agendar tarefas."""
    application.create_task(send_periodic_messages(application))

def main():
    logger.info("Iniciando o bot...")
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Adiciona os handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Atualiza chat_id e idioma
    async def update_chat_info(update: Update, context):
        application.bot_data["chat_id"] = update.effective_chat.id
        language = update.message.from_user.language_code or 'en'
        application.bot_data["language"] = language[:2].lower()
        logger.info(f"Chat ID atualizado: {update.effective_chat.id}, Idioma: {application.bot_data['language']}")

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, update_chat_info, block=False))

    # Configura o webhook antes de iniciar
    asyncio.run(set_webhook(application))

    # Inicia o webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"https://meu-bot-t.onrender.com/{TOKEN}"
    )
    logger.info("Bot está rodando com webhook...")

if __name__ == '__main__':
    main()