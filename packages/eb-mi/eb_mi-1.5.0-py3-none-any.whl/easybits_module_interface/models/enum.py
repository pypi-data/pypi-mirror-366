from enum import Enum


class MessageTypes(Enum):
    SYSTEM_MESSAGE_PARSER = 'system_message_parser'
    SYSTEM_MESSAGE_CONTROLLER = 'system_message_controller'
    SYSTEM_MESSAGE_DATASINK = 'system_message_datasink'
    INCOMING_MESSAGE = 'incoming_message'
    OUTGOING_MESSAGE = 'outgoing_message'
    OUTGOING_MESSAGE_IMAGE = 'outgoing_message_image'
    OUTGOING_MESSAGE_AUDIO = 'outgoing_message_audio'


class SystemMessageEvents(Enum):
    SAVE = 'save'
    DELETE = 'delete'
    CONFIGURE_PROXY_MODE = 'configure_proxy_mode'



