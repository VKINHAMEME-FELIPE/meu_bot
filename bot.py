from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler
import logging
from deep_translator import GoogleTranslator  # Usando deep-translator

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Insira o token do seu bot aqui
TOKEN = '7852634722:AAFPO4V3-6w4NMmUxNatzz4EedyMrE8Mv6w'

# Função para traduzir a mensagem
def translate_message(text, dest_language):
    # Lista de idiomas suportados pelo deep-translator (Google Translate)
    supported_languages = ['pt', 'en', 'es']  # Adicione mais se necessário
    if dest_language not in supported_languages:
        dest_language = 'en'  # Fallback para inglês
    translator = GoogleTranslator(source='auto', target=dest_language)
    return translator.translate(text)

# Função para enviar mensagem de boas-vindas
async def welcome(update: Update, context):
    logger.info(f"Novo membro detectado: {update.message.new_chat_members}")
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            # Obtém o idioma do usuário via Telegram API
            language = update.message.from_user.language_code or 'en'  # 'en' como padrão
            # Usa apenas os primeiros dois caracteres (ex.: 'pt-BR' -> 'pt')
            language = language[:2].lower()

            # Traduz as mensagens com base no idioma do usuário
            welcome_message = translate_message("Welcome to our official VKINHA community!", language)
            warning_message = translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", language)
            admin_message = translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", language)

            # Envia a mensagem de boas-vindas
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{welcome_message}\n\n{warning_message}\n\n{admin_message}"
            )

            # Envia os botões de comando
            keyboard = [
                [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                [InlineKeyboardButton("Pre-Sale", url=https://www.dx.app/dxsale/view?address=0x0597Ce945ED83C81AdC47c97139B5602ddb03c69&chain=56")],
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

        # Deleta a mensagem que informa que o novo membro entrou no grupo
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

# Função para lidar com os botões
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'pre_sale':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pre-sale prevista para começar na dxsale no dia 30/03/2025"
        )

# Função para iniciar o bot
def main():
    logger.info("Iniciando o bot...")
    application = Application.builder().token(TOKEN).build()

    # Adiciona os handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Configuração do webhook
    try:
        application.run_webhook(
            listen="0.0.0.0",  # Escuta em todos os IPs
            port=10000,        # Porta que o Render usa
            url_path=TOKEN,    # Caminho do webhook
            webhook_url=f"https://meu-bot-telegram-gepf.onrender.com/{TOKEN}"  # URL do webhook
        )
        logger.info("Bot está rodando com webhook...")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")

if __name__ == '__main__':
    main()