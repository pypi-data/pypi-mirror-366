from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from easybits_module_interface.models.base import BaseDataClass
from easybits_module_interface.models.enum import MessageTypes, SystemMessageEvents


@dataclass
class ContextProvider(BaseDataClass):
    """
    Configuration for a context provider
    """
    #: name of resulting key in context
    key: str = ""
    #: name of the context provider to use
    provider_name: str = ""


@dataclass
class AvailableModule(BaseDataClass):
    """
    Module config template
    """
    #: Internal ID
    id: int
    #: verbose identifier of module
    name: str
    #: description of module
    description: str
    #: indicates that the module supports reengagement
    supports_reengagement: bool = False
    #: Layout of configuration values
    configuration_layout: Optional[Dict] = None
    #: List of supported context providers by the module
    supported_context_providers: Optional[List] = None
    #: Indicates if the module is allowed to be used
    #:   without any pre-selection process
    is_passive: bool = False
    # The following attributes are commented out, as they
    # are only used in the client applications.
    #: Indicates if the module is available to be used
    #is_published: bool = True
    #: Indicates if the module is visible for users
    #is_visible: bool = True
    #: Indicates if the module is the default module
    #    that is used during the default module prediction
    #    phase of the parser.
    is_default: bool = False
    #: String of comma separated intentions that the module supports
    intentions: Optional[str] = None


@dataclass
class BotModule(BaseDataClass):
    """
    Configuration for a bot specific module.
    """
    #: internal identifier of bot module
    id: int
    #: instance of :py:obj:`~.AvailableModule`
    module: AvailableModule = None
    #: indicates that the module is active
    is_active: bool = False
    #: indicates that the module uses reengagement
    has_reengagement: bool = False
    #: list of instances of :py:obj:`~.ContextProvider` \
    #  that are used to extract context from incoming messages
    context_providers: List[ContextProvider] = field(default_factory=list)
    #: configuration values for the module
    configuration_values: Dict = field(default_factory=dict)
    #: configuration values for the parser
    parser_configuration: Dict = field(default_factory=dict)
    #: desired reengagement message
    reengagement_message: str = None
    #: Timeout in minutes for reengagement message
    reengagement_timeout_minutes: int = None

    @property
    def name(self):
        return self.module.name

    @property
    def intentions(self):
        return self.module.intentions

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Creates an instance from given kwargs

        :param kwargs: object as kwargs
        :return: :py:obj:`~.BotModule` instance
        """
        module = kwargs.pop('module', None)
        context_providers = kwargs.pop('context_providers', [])

        return super().from_dict(
            **kwargs,
            module=AvailableModule.from_dict(**module) if module else None,
            context_providers=[ContextProvider.from_dict(**c) for c in context_providers]
        )


@dataclass
class ConfigureModuleContext(BaseDataClass):
    """
    Integration config template
    """
    id: str = None
    #: name of the integration
    name: str = None
    #: list of instances of :py:obj:`~.ContextProvider`
    context_providers: List[ContextProvider] = field(default_factory=list)
    #: indicates that the integration is ready to consume messages
    is_active: bool = False
    #: indicates that the integration supports reengagement
    re_engagement: bool = False

    #: layout of configuration values
    configuration_layout: Optional[Dict] = None
    #: indicates that the module supports reengagement
    supports_reengagement: bool = False
    #: description of module
    description: str = None



