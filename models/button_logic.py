from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ButtonCreator:
    def __init__(self, button_info: dict):
        self.button_info = button_info

    async def get_keyboard(self) -> InlineKeyboardMarkup:
        buttons = await self._get_button_list()
        keyboard = InlineKeyboardMarkup(row_width=3)
        for button in buttons:
            keyboard.add(button)
        return keyboard

    async def _get_button_list(self) -> list:
        btn_list = []
        for key, value in self.button_info.items():
            btn_list.append(InlineKeyboardButton(text=value, callback_data=key))
        return btn_list
