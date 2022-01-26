from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold

from botapp.utils import confirm_group_keyboard, teachers_links, encode_start_group_user, send_other_teachers_in_group, opros_state, hash_, cb_confirm_group
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

class StartStates(StatesGroup):
    choose_group_inline = State()


@dp.message_handler(commands=['teachers_left'], state='*')
async def teachers_left(message: types.Message):
    r = models.Result.objects.filter(is_active=True, user_id=hash_(message.from_user.id)).first()
    if not r:
        return await message.answer(L['user_no_group'])
    await send_other_teachers_in_group(message, r.teacher_n_group.group)


@dp.message_handler(commands=['start'], state='*', deep_link='g')
async def start_group(message: types.Message, payload: str):
    try:
        group = models.Group.objects.get(id=payload)
    except models.Group.DoesNotExist:
        return await message.answer(L['wrong_link'])

    teachers = group.teacher_need_votes()
    text = L['group_teachers_text' + opros_state()].format(
        group_name=group.name.upper(),
        results_link=group.faculty.poll_result_link,
        teachers=teachers_links(teachers),
        start_group_link=encode_start_group_user(group.id))
    await message.reply(text)


@dp.message_handler(commands=['start'], state='*', deep_link='gu')
async def start_group_user(message: types.Message, payload: str):
    try:
        group = models.Group.objects.get(id=payload)
    except models.Group.DoesNotExist:
        return await message.answer(L['wrong_link'])

    await send_other_teachers_in_group(message, group)


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    r = models.Result.objects.filter(is_active=True, user_id=hash_(message.from_user.id)).first()
    if r:
        return await send_other_teachers_in_group(message, r.teacher_n_group.group)

    markup = InlineKeyboardMarkup(row_width=1)
    BTN_SEARCH_GROUP = L["btn_search_group"]
    markup.insert(
        InlineKeyboardButton(
            BTN_SEARCH_GROUP,
            switch_inline_query_current_chat=""
        )
    )
    await message.answer(L["begin_search_group"], reply_markup=markup)
    await StartStates.choose_group_inline.set()


@dp.inline_handler(state=StartStates.choose_group_inline)
async def choose_group_inline(inline_query: types.InlineQuery, state: FSMContext):
    if not inline_query.query:
        return
    offset = int(inline_query.offset) if inline_query.offset else 0
    limit = 5

    groups = models.Group.objects.filter(name__startswith=inline_query.query.upper())[offset:offset+limit]
    if not groups:
        return

    inline_query_results = []
    for group in groups:
        markup = confirm_group_keyboard(group)
        title=L["result_title_search_group"].format(group=group)
        message_text = L["result_message_search_group"].format(group=group)
        description = L["result_description_search_group"].format(group=group)
        inline_query_results.append(
            types.InlineQueryResultArticle(
                id=group.id,
                title=title,
                input_message_content=types.InputTextMessageContent(
                    message_text=message_text, parse_mode="HTML"
                ),
                reply_markup=markup,
                description=description,
            )
        )
    await inline_query.answer(
        inline_query_results,
        cache_time=1,
        next_offset=offset + 5 if inline_query_results else None,
    )


@dp.callback_query_handler(cb_confirm_group.filter(), state=StartStates.choose_group_inline)
async def choose_group(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.answer()

    group_id = callback_data.get("group_id")
    group = models.Group.objects.get(id=group_id)
    message = types.Message(**{"from": query.from_user, "chat": query.from_user})
    await state.finish()
    await send_other_teachers_in_group(message, group)


@dp.message_handler(commands=['help'], state='*')
async def help_cmd(message: types.Message):
    await message.answer(L['help_text'])


@dp.message_handler(state='*', chat_type=types.ChatType.PRIVATE)
async def text_fallback(message: types.Message):
    if message.via_bot and message.via_bot.id == message.bot.id:
        return
    await message.answer(L['unknown_cmd'])


@dp.callback_query_handler(state='*')
async def query_fallback(query: types.CallbackQuery):
    await query.answer(L['callback_no_state'], show_alert=True)
