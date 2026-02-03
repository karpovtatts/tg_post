"""
Обработчики команд Telegram бота
"""


from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from app.bot.api_client import APIClient
from app.bot.retry import retry_with_backoff
from app.core.logging_config import get_logger

router = Router()
logger = get_logger(__name__)
api_client = APIClient()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создать главную клавиатуру с командами"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/recent"),
                KeyboardButton(text="/pinned"),
            ],
            [
                KeyboardButton(text="/help"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Введите команду или поисковый запрос",
    )
    return keyboard


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        welcome_text = (
            "👋 Добро пожаловать в PromptVault!\n\n"
            "Я помогу вам найти и получить промпты из вашего хранилища.\n\n"
            "📋 Доступные команды:\n"
            "/get <запрос> - найти промпт по тексту\n"
            "/recent - последние промпты\n"
            "/pinned - закрепленные промпты\n"
            "/help - справка\n\n"
            "Просто отправьте текст для поиска, и я найду подходящие промпты!"
        )

        await message.answer(welcome_text, reply_markup=get_main_keyboard())
        logger.info(f"Команда /start выполнена для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении /start: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try:
        help_text = (
            "📖 Справка по командам:\n\n"
            "/start - начать работу с ботом\n"
            "/get <запрос> - найти промпт по тексту или ID\n"
            "   Пример: /get landscape\n"
            "   Пример: /get 123\n\n"
            "/recent - показать последние 10 промптов\n"
            "/pinned - показать закрепленные промпты\n\n"
            "💡 Совет: Вы также можете просто отправить текст для поиска!"
        )

        await message.answer(help_text)
        logger.info(f"Команда /help выполнена для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении /help: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@router.message(Command("get"))
async def cmd_get(message: Message):
    """Обработчик команды /get - поиск промпта"""
    try:
        # Извлечение аргумента команды
        command_args = message.text.split(maxsplit=1)
        if len(command_args) < 2:
            await message.answer(
                "❌ Укажите поисковый запрос или ID промпта.\nПример: /get landscape\nПример: /get 123"
            )
            return

        query = command_args[1].strip()

        # Проверка, является ли запрос числом (ID)
        if query.isdigit():
            prompt_id = int(query)
            result = await retry_with_backoff(api_client.get_prompt_by_tg_id, tg_message_id=prompt_id)

            if result:
                await send_prompt(message, result)
            else:
                await message.answer(f"❌ Промпт с ID {prompt_id} не найден.")
            return

        # Поиск по тексту
        await message.answer("🔍 Ищу промпты...")

        # Используем поиск через API
        # Для упрощения используем прямой запрос к API
        import aiohttp

        search_url = f"{api_client._base_url}/api/v1/search"
        params = {"q": query, "limit": 5}
        headers = api_client.headers

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    prompts = data.get("items", [])

                    if not prompts:
                        await message.answer(f"❌ Промпты по запросу '{query}' не найдены.")
                        return

                    # Отправляем первый найденный промпт
                    if len(prompts) > 0:
                        await send_prompt(message, prompts[0])

                        # Если найдено больше одного, предлагаем посмотреть остальные
                        if len(prompts) > 1:
                            await message.answer(
                                f"📋 Найдено промптов: {data.get('total', len(prompts))}\n"
                                f"Показан первый результат. Уточните запрос для более точного поиска."
                            )
                else:
                    await message.answer("❌ Ошибка при поиске. Попробуйте позже.")

        logger.info(f"Команда /get выполнена для пользователя {message.from_user.id}, запрос: {query}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении /get: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка при поиске. Попробуйте позже.")


@router.message(Command("recent"))
async def cmd_recent(message: Message):
    """Обработчик команды /recent - последние промпты"""
    try:
        await message.answer("📋 Загружаю последние промпты...")

        import aiohttp

        url = f"{api_client._base_url}/api/v1/prompts"
        params = {"limit": 10, "page": 1}
        headers = api_client.headers

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    prompts = data.get("items", [])

                    if not prompts:
                        await message.answer("❌ Промпты не найдены.")
                        return

                    # Отправляем список промптов
                    text = f"📋 Последние {len(prompts)} промптов:\n\n"
                    for i, prompt in enumerate(prompts[:10], 1):
                        preview = prompt.get("text", "")[:100]
                        if len(prompt.get("text", "")) > 100:
                            preview += "..."

                        pinned_icon = "📌 " if prompt.get("is_pinned") else ""
                        text += f"{i}. {pinned_icon}ID: {prompt.get('id')}\n"
                        text += f"   {preview}\n\n"

                    await message.answer(text)

                    # Отправляем первый промпт полностью
                    if prompts:
                        await send_prompt(message, prompts[0])
                else:
                    await message.answer("❌ Ошибка при загрузке промптов.")

        logger.info(f"Команда /recent выполнена для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении /recent: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@router.message(Command("pinned"))
async def cmd_pinned(message: Message):
    """Обработчик команды /pinned - закрепленные промпты"""
    try:
        await message.answer("📌 Загружаю закрепленные промпты...")

        import aiohttp

        url = f"{api_client._base_url}/api/v1/prompts"
        params = {"limit": 10, "page": 1, "pinned": True}
        headers = api_client.headers

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    prompts = data.get("items", [])

                    if not prompts:
                        await message.answer("❌ Закрепленные промпты не найдены.")
                        return

                    # Отправляем список
                    text = f"📌 Закрепленные промпты ({len(prompts)}):\n\n"
                    for i, prompt in enumerate(prompts[:10], 1):
                        preview = prompt.get("text", "")[:100]
                        if len(prompt.get("text", "")) > 100:
                            preview += "..."

                        text += f"{i}. ID: {prompt.get('id')}\n"
                        text += f"   {preview}\n\n"

                    await message.answer(text)

                    # Отправляем первый промпт полностью
                    if prompts:
                        await send_prompt(message, prompts[0])
                else:
                    await message.answer("❌ Ошибка при загрузке закрепленных промптов.")

        logger.info(f"Команда /pinned выполнена для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении /pinned: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


async def send_prompt(message: Message, prompt_data: dict):
    """
    Отправить промпт пользователю в удобном формате

    Args:
        message: Сообщение от пользователя
        prompt_data: Данные промпта
    """
    try:
        text = prompt_data.get("text", "")
        prompt_id = prompt_data.get("id", "?")
        is_pinned = prompt_data.get("is_pinned", False)
        tags = prompt_data.get("tags", [])

        # Формируем сообщение
        header = f"📝 Промпт #{prompt_id}"
        if is_pinned:
            header += " 📌"

        if tags:
            tag_names = ", ".join([tag.get("name", "") for tag in tags])
            header += f"\n🏷 Теги: {tag_names}"

        # Ограничение длины для Telegram (4096 символов)
        max_length = 4000
        if len(text) > max_length:
            text = text[:max_length] + "\n\n... (текст обрезан)"

        full_text = f"{header}\n\n{text}"

        await message.answer(full_text)

        logger.info(f"Промпт {prompt_id} отправлен пользователю {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке промпта: {e}", extra={"error": str(e)})
        await message.answer("❌ Ошибка при отправке промпта.")


@router.message()
async def handle_text_message(message: Message):
    """
    Обработчик текстовых сообщений (поиск без команды)
    """
    # Игнорируем команды (они обрабатываются отдельно)
    if message.text and message.text.startswith("/"):
        return

    # Игнорируем сообщения из каналов
    if message.chat.type != "private":
        return

    try:
        query = message.text.strip()
        if not query:
            return

        await message.answer("🔍 Ищу промпты...")

        # Используем поиск
        import aiohttp

        search_url = f"{api_client._base_url}/api/v1/search"
        params = {"q": query, "limit": 3}
        headers = api_client.headers

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    prompts = data.get("items", [])

                    if not prompts:
                        await message.answer(
                            f"❌ Промпты по запросу '{query}' не найдены.\n"
                            "Попробуйте другой запрос или используйте /help для справки."
                        )
                        return

                    # Отправляем найденные промпты
                    total = data.get("total", len(prompts))
                    if total > 3:
                        await message.answer(
                            f"📋 Найдено промптов: {total}\nПоказаны первые {len(prompts)} результатов."
                        )

                    for prompt in prompts:
                        await send_prompt(message, prompt)
                else:
                    await message.answer("❌ Ошибка при поиске. Попробуйте позже.")

        logger.info(f"Поиск выполнен для пользователя {message.from_user.id}, запрос: {query}")
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {e}", extra={"error": str(e)})
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
