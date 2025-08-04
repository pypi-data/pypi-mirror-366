from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from ..types.message import Messages
from ..enums.http_method import HTTPMethod
from ..enums.api_path import ApiPath
from ..connection.base import BaseConnection


if TYPE_CHECKING:
    from ..bot import Bot


class GetMessages(BaseConnection):
    
    """
    Класс для получения сообщений из чата через API.

    Args:
        bot (Bot): Экземпляр бота для выполнения запроса.
        chat_id (int): Идентификатор чата.
        message_ids (List[str], optional): Список идентификаторов сообщений для выборки. По умолчанию None.
        from_time (datetime | int, optional): Временная метка начала выборки сообщений (timestamp или datetime). По умолчанию None.
        to_time (datetime | int, optional): Временная метка конца выборки сообщений (timestamp или datetime). По умолчанию None.
        count (int, optional): Максимальное количество сообщений для получения. По умолчанию 50.

    Attributes:
        bot (Bot): Экземпляр бота.
        chat_id (int): Идентификатор чата.
        message_ids (List[str] | None): Фильтр по идентификаторам сообщений.
        from_time (datetime | int | None): Начальная временная метка.
        to_time (datetime | int | None): Конечная временная метка.
        count (int): Максимальное число сообщений.
    """
    
    def __init__(
            self,
            bot: 'Bot', 
            chat_id: Optional[int] = None,
            message_ids: Optional[List[str]] = None,
            from_time: Optional[Union[datetime, int]] = None,
            to_time: Optional[Union[datetime, int]] = None,
            count: int = 50,
        ):
        self.bot = bot
        self.chat_id = chat_id
        self.message_ids = message_ids
        self.from_time = from_time
        self.to_time = to_time
        self.count = count

    async def fetch(self) -> Messages:
        
        """
        Выполняет GET-запрос для получения сообщений с учётом параметров фильтрации.

        Преобразует datetime в UNIX timestamp при необходимости.

        Returns:
            Messages: Объект с полученными сообщениями.
        """
        
        if self.bot is None:
            raise RuntimeError('Bot не инициализирован')
        
        params = self.bot.params.copy()

        if self.chat_id: 
            params['chat_id'] = self.chat_id

        if self.message_ids:
            params['message_ids'] = ','.join(self.message_ids)

        if self.from_time:
            if isinstance(self.from_time, datetime):
                params['from_time'] = int(self.from_time.timestamp())
            else:
                params['from_time'] = self.from_time

        if self.to_time:
            if isinstance(self.to_time, datetime):
                params['to_time'] = int(self.to_time.timestamp())
            else:
                params['to_time'] = self.to_time
        
        params['count'] = self.count

        return await super().request(
            method=HTTPMethod.GET, 
            path=ApiPath.MESSAGES,
            model=Messages,
            params=params
        )