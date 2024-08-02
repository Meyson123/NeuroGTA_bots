import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Замените 'YOUR_TOKEN_HERE' на токен вашего бота
TOKEN = '7341349790:AAE808M6j_77uNA0pYPK355Y4tUlwzS6gzM'

# Включите логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Бот активен и готов назначать администраторов пустышек!')

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        try:
            chat_id = update.effective_chat.id
            user_id = member.id

            # Проверка прав бота
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != 'administrator' or not bot_member.can_promote_members:
                await update.message.reply_text(f'Бот не имеет прав для назначения администраторов.')
                return

            # Назначение нового администратора без прав
            await context.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                is_anonymous=False,
                can_manage_chat=True,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_topics=False
            )
            await update.message.reply_text(f'{member.full_name} теперь администратор без прав!')
        except Exception as e:
            await update.message.reply_text(f'Не удалось выдать админские права {member.full_name}: {e}')

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    application.run_polling()

if __name__ == '__main__':
    main()
