from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
import logging
import requests
from googletrans import Translator

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Insira o token do seu bot aqui
TOKEN = '7852634722:AAFPO4V3-6w4NMmUxNatzz4EedyMrE8Mv6w'

# Chave da API de geolocalização (substitua pela sua chave)
IPINFO_TOKEN = '1e1946fa6728b1'

# Função para obter a localização via IP
def get_location_by_ip(ip):
    url = f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('country')  # Retorna o código do país (ex: 'BR' para Brasil)
    return None

# Função para traduzir a mensagem
def translate_message(text, dest_language):
    translator = Translator()
    translation = translator.translate(text, dest=dest_language)
    return translation.text

# Função para enviar mensagem de boas-vindas
async def welcome(update: Update, context):
    logger.info(f"Novo membro detectado: {update.message.new_chat_members}")
    # Verifica se há novos membros no grupo
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            # Obtém o IP do usuário (aproximação via IP do Telegram)
            user_ip = update.message.from_user.id  # Isso é apenas um exemplo, não é o IP real
            # Obtém a localização do usuário
            country_code = get_location_by_ip(user_ip)
            if country_code:
                # Define o idioma com base no país
                if country_code == 'BR':
                    language = 'pt'
                elif country_code == 'US':
                    language = 'en'
                elif country_code == 'ES':
                    language = 'es'
                else:
                    language = 'en'  # Idioma padrão
                # Traduz a mensagem de boas-vindas
                welcome_message = translate_message("Welcome to our official VKINHA community!", language)
                warning_message = translate_message("⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️", language)
                admin_message = translate_message("‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️", language)
                location_message = translate_message("Sua localização é:", language)
                flag = get_country_flag(country_code)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{welcome_message}\n\n{warning_message}\n\n{admin_message}\n\n{location_message} {flag}"
                )
            else:
                # Mensagem padrão se a localização não for encontrada
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Welcome to our official VKINHA community!\n\n⚡️⚡️MAKE SURE YOU ARE ON OUR OFFICIAL WEBSITE VKINHA⚡️⚡️\n\n‼️‼️ ADMIN DONT PM YOU OR ASK FOR FUNDS ‼️‼️"
                )

            # Envia os botões de comando
            keyboard = [
                [InlineKeyboardButton("Contract", url="https://bscscan.com/token/0x7Bd2024cAd405ccA960fE9989334A70153c41682")],
                [InlineKeyboardButton("Pre-Sale", callback_data='pre_sale')],
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

# Função para lidar com os botões
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'pre_sale':
        # Envia uma mensagem adicional sem remover os botões
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pre-sale prevista para começar na dxsale no dia 30/03/2025"
        )

def main():
    logger.info("Iniciando o bot...")
    # Cria uma aplicação para o bot
    application = Application.builder().token(TOKEN).build()

    # Adiciona a função de boas-vindas para novos membros
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Adiciona o handler para os botões
    application.add_handler(CallbackQueryHandler(button_handler))

    # Inicia o bot
    logger.info("Bot está rodando...")
    application.run_polling()

if __name__ == '__main__':
    main()