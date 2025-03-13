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
GROUP_CHAT_ID = '-1002405955713'  # ID do seu grupo

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

async def send_periodic_messages(context: CallbackContext):
    messages = [
        {"text": "🌟 Atualização VKINHA: Fique por dentro do nosso projeto! Visite nosso site oficial: https://www.vkinha.com.br 🌟", "keyboard": None},
        {"text": "🌟 Atualização VKINHA: Você sabia que a pré-venda na Dxsale está configurada?", "keyboard": [[InlineKeyboardButton("Clique aqui!", url="https://www.dx.app/dxsale/view?address=0x0597Ce945ED83C81AdC47c97139B5602ddb03c69&chain=56")]]},
        {"text": "Você sabia que nós estamos fechando parceria com:", "keyboard": [
            [InlineKeyboardButton("Azbit", url="https://azbit.com"), InlineKeyboardButton("Bifinance", url="https://bifinance.com")],
            [InlineKeyboardButton("CertiK", url="https://www.certik.com"), InlineKeyboardButton("Gate.io", url="https://www.gate.io")],
            [InlineKeyboardButton("Cryptopix", url="https://cryptopix.com")]
        ]},
        {"text": "Siga nosso perfil no Instagram:", "keyboard": [[InlineKeyboardButton("Instagram", url="https://www.instagram.com/vkinhacoin/")]]},
        {"text": "Você conhece nosso perfil do X (Twitter)?", "keyboard": [[InlineKeyboardButton("Twitter", url="https://x.com/vkinhacoin")]]},
        {"text": "Você já viu nosso CÓDIGO? Veja, ele está verificado e auditado:", "keyboard": [[InlineKeyboardButton("BSCScan", url="https://bscscan.com/address/0x7Bd2024cAd405ccA960fE9989334A70153c41682#code")]]},
        {"text": "Apoie nossa comunidade! Deixe seu 🔥 no site da DX para nosso token entrar em alta!", "keyboard": None},
        {"text": "Obrigado por apoiar a VKINHA.", "keyboard": None},
        {"text": "Você sabia que nós iremos apoiar projetos que ajudam vidas?", "keyboard": None},
        {"text": "Veja nosso Roadmap:", "keyboard": [[InlineKeyboardButton("Roadmap Link", url="https://vkinha.com/roadmap.html")]]}
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
        logger.error(f"Erro ao enviar mensagem periódica: {e}")

async def verify_user(update: Update, context: CallbackContext):
    """Verifica se o usuário está no grupo para o airdrop."""
    if not update.message or not update.message.text.startswith('/verify'):
        return

    try:
        username = update.message.text.split()[1] if len(update.message.text.split()) > 1 else None
        if not username or not username.startswith('@'):
            await update.message.reply_text("Por favor, forneça seu username do Telegram (ex: @username).")
            return

        # Obtém o ID do usuário a partir do username
        user_id = None
        chat_member = await context.bot.get_chat_member(chat_id=GROUP_CHAT_ID, user_id=update.message.from_user.id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            user_id = update.message.from_user.id
        else:
            await update.message.reply_text("Você não está no grupo do Telegram. Entre no grupo com ID " + GROUP_CHAT_ID + " e tente novamente.")
            return

        await update.message.reply_text(f"Verificação concluída com sucesso, {username}! Você está no grupo.")
    except Exception as e:
        logger.error(f"Erro na verificação: {e}")
        await update.message.reply_text("Erro ao verificar. Tente novamente ou entre em contato com o suporte.")

async def get_chat_id(update: Update, context: CallbackContext):
    await update.message.reply_text(f"ID deste chat: {update.effective_chat.id}")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(CommandHandler("verify", verify_user))
    
    # Agenda mensagens periódicas a cada 15 minutos
    job_queue = application.job_queue
    job_queue.run_repeating(
        callback=send_periodic_messages,
        interval=900,  # 15 minutos
        first=10       # Inicia após 10 segundos
    )

    # Inicia em modo polling
    application.run_polling()

if __name__ == '__main__':
    main()