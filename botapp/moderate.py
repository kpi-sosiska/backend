import random
from contextlib import suppress

from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.utils import exceptions
from aiogram.utils.callback_data import CallbackData

from mainapp.models import Locale as L, Result
from .bot import dp, bot
from .utils import censure

cb = CallbackData('moderate', 'id', 'status')
kb = {'🤷': 'skip', '👍': 'ok', '👎': 'neok'}.items()
start_kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Поехали', callback_data=cb.new(0, 'skip')))


@dp.message_handler(commands=['moderate'])
async def start_moderate(message: types.Message):
    if not await bot.get_chat_member(L['admin_chat_id'], message.from_user.id):
        raise SkipHandler
    await message.reply("Отмечайте допустимые комментарии кнопкой 👍, недопустимые 👎 или,"
                        " если есть сомнения, пропустите 🤷", reply_markup=start_kb)


@dp.callback_query_handler(cb.filter())
async def moderate_handler(query: types.CallbackQuery, callback_data: dict):
    id_, status = callback_data['id'], callback_data['status']
    if status != 'skip':
        Result.objects.filter(id=id_).update(open_answer_moderate=status == 'ok')

    comment = _get_comment()
    if comment is None:
        with suppress(exceptions.MessageNotModified):
            return await query.message.edit_text("Комментарии пока что закончились. Нажми кнопку что бы обновить",
                                                 reply_markup=start_kb)
        return await query.answer()

    await query.message.edit_text(censure(comment.open_question_answer), reply_markup=_keyboard(comment.id))


def _get_comment():
    q = Result.objects.filter(is_active=True, open_question_answer__isnull=False,
                              open_answer_moderate__isnull=True, teacher_n_group__teacher__teacherfacultyresult__isnull=False)
    rand_id = random.randint(0, q.count())
    return q.filter(id__gte=rand_id).first()


def _keyboard(id_):
    return types.InlineKeyboardMarkup().row(*[
        types.InlineKeyboardButton(text, callback_data=cb.new(id=id_, status=status))
        for text, status in kb
    ])
