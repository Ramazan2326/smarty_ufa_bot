from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.googleapi_utils import spreadsheet_id, service
import datetime as dt

router_servicemen = Router()

output_submit_values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Заявки!A:I',
    majorDimension='ROWS'
).execute()['values'][2:]
servicemen = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Сервисмены!A:F',
    majorDimension='ROWS'
).execute()['values'][2:]


class CommandsServCallback(CallbackData, prefix='commands'):
    foo: str


builder_commands_servicemen = InlineKeyboardBuilder()
main_servicemen_button1 = builder_commands_servicemen.button(
    text="Вывести горящие задачи",
    callback_data=CommandsServCallback(foo="/hottasks")
)
main_servicemen_button2 = builder_commands_servicemen.button(
    text="Вывести все актуальные задания",
    callback_data=CommandsServCallback(foo="/alltasks")
)
builder_commands_servicemen.adjust(1)


# Все задачи закрепленные за конкретным сервисменом
@router_servicemen.callback_query(
    CommandsServCallback.filter(F.foo == "/alltasks"))
async def callback_actual(query: CallbackQuery):
    await query.message.answer("Актуальные заявки:")
    SERV_ID = None
    USER_ID = int(query.from_user.id)
    for submit in output_submit_values:
        surname_serv = str(submit[-1])
        for serv in servicemen:
            if str(serv[1]) == surname_serv:
                SERV_ID = int(serv[0])
                if (SERV_ID == USER_ID) and (submit[5] == "не обработано"):
                    await query.message.answer(f"Заявка №{submit[0]}\n"
                                               f"{submit[2]} – {submit[5]}")


@router_servicemen.callback_query(
    CommandsServCallback.filter(F.foo == "/hottasks"))
async def callback_hottasks(query: CallbackQuery):
    await query.message.answer(
        "Горящие заявки (до крайнего срока выполнения остается 3 дня):")
    after_three_days = (dt.date.today() + dt.timedelta(days=3)).strftime(
        "%d.%m.%Y")
    SERV_ID = None
    USER_ID = int(query.from_user.id)
    for submit in output_submit_values:
        surname_serv = str(submit[-1])
        for serv in servicemen:
            if str(serv[1]) == surname_serv:
                SERV_ID = int(serv[0])
                print(after_three_days, submit[-2])
                if (SERV_ID == USER_ID) and (after_three_days == submit[-2]):
                    await query.message.answer(f"Заявка №{submit[0]}\n"
                                               f"{submit[2]} – {submit[5]}")
