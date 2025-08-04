from typing import Any, Dict, List, TYPE_CHECKING, Optional

from ..types.attachments.image import PhotoAttachmentRequestPayload

from ..types.users import User
from ..types.command import BotCommand

from ..enums.http_method import HTTPMethod
from ..enums.api_path import ApiPath

from ..connection.base import BaseConnection


if TYPE_CHECKING:
    from ..bot import Bot


class ChangeInfo(BaseConnection):
    
    """
    Класс для изменения информации о боте.

    Args:
        bot (Bot): Объект бота
        name (str, optional): Новое имя бота
        description (str, optional): Новое описание
        commands (List[BotCommand], optional): Список команд
        photo (PhotoAttachmentRequestPayload, optional): Данные фото
    """
    
    def __init__(
            self,
            bot: 'Bot',
            name: Optional[str] = None, 
            description: Optional[str] = None,
            commands: Optional[List[BotCommand]] = None,
            photo: Optional[PhotoAttachmentRequestPayload] = None
        ):
            self.bot = bot
            self.name = name
            self.description = description
            self.commands = commands
            self.photo = photo

    async def fetch(self) -> User:
        
        """Отправляет запрос на изменение информации о боте.

        Returns:
            User: Объект с обновленными данными бота
        """
        
        if self.bot is None:
            raise RuntimeError('Bot не инициализирован')
        
        json: Dict[str, Any] = {}

        if self.name: 
            json['name'] = self.name
        if self.description: 
            json['description'] = self.description
        if self.commands: 
            json['commands'] = [command.model_dump() for command in self.commands]
        if self.photo: 
            json['photo'] = self.photo.model_dump()

        return await super().request(
            method=HTTPMethod.PATCH, 
            path=ApiPath.ME,
            model=User,
            params=self.bot.params,
            json=json
        )