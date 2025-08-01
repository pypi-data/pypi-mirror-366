from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from easybits_module_interface.models.base import DynamicFieldsDataClass, BaseDataClass
from easybits_module_interface.models.enum import MessageTypes, SystemMessageEvents
from easybits_module_interface.models.module import AvailableModule


@dataclass
class MessageMeta(DynamicFieldsDataClass):
    """
    Meta data for messages.

    This class is dynamic, meaning using the from_dict method
    will create a new dataclass with the fields provided in the kwargs.

    This is useful to add more meta data to the message without
    changing the class definition.
    """
    #: type of message
    type: MessageTypes
    #: event type of message
    event: Optional[str] = None
    #: internal ID of communication channel
    communicationChannelId: Optional[str] = None
    #: type identifier of the controller used for communication
    controller: Optional[str] = None
    #: ID of the user can be used for tracking/state management
    internalUserId: Optional[str] = None
    #: ID of the bot used for communication
    botId: Optional[str] = None

    #: [Optional] configured language of bot used inside modules to generate responses
    language: Optional[str] = None
    #: [Optional] internal tracking ID of the message
    messageId: Optional[str] = None


@dataclass
class UserMessage(BaseDataClass):
    """
    Object to describe message content aka a UserMessage
    """
    #: content of incoming message
    incoming: Optional[str] = None
    #: content of incoming file
    incoming_file: Optional[str] = None
    #: content of outgoing message
    outgoing: Optional[str] = None


@dataclass
class Message(BaseDataClass):
    #: message meta data
    meta: MessageMeta
    #: extracted context from incoming message
    context: Optional[Union[Dict, 'ConfigureModuleContext']] = None
    #: message content
    message: Optional[UserMessage] = None
    #: configuration values forwarded to the module
    config: Optional[Dict] = None

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Creates an instance from given kwargs

        :param kwargs: object as kwargs
        :return: :py:obj:`~.Message` instance
        """
        meta_data = kwargs.pop('meta', None)
        if meta_data is not None:
            meta_data = MessageMeta.from_dict(**meta_data)
        message = kwargs.pop('message', None)
        if message is not None:
            message = UserMessage.from_dict(**message)

        context = kwargs.pop('context', None)
        is_configure_module_message = (
            meta_data
            and meta_data.type == MessageTypes.SYSTEM_MESSAGE_PARSER.value
            and meta_data.event in [
                SystemMessageEvents.SAVE.value,
                SystemMessageEvents.DELETE.value,
            ]
        )
        if is_configure_module_message:
            context = AvailableModule.from_dict(**context)

        config = kwargs.pop('config', None)

        return super().from_dict(
            context=context,
            meta=meta_data,
            message=message,
            config=config,
        )

