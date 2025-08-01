from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from easybits_module_interface.models.base import DynamicFieldsDataClass, BaseDataClass
from easybits_module_interface.models.module import AvailableModule, BotModule, ContextProvider


@dataclass
class Tool(BaseDataClass):
    id: int
    position: int
    template: str
    send_intermediate_result: bool = False
    status_report: Optional[str] = None


@dataclass
class RouterConfig(BaseDataClass):
    tool_sequence: dict[str, Tool]

    @classmethod
    def from_dict(cls, **kwargs) -> 'RouterConfig':
        """
        Classmethod to create a RouterConfig instance from a dictionary

        :param kwargs: Dictionary containing the RouterConfig data
        :returns: A freshly created RouterConfig instance
        """
        tool_sequence = kwargs.pop('tool_sequence', [])
        
        return super().from_dict(
            **kwargs,
            tool_sequence={str(val.get('position', idx)): Tool.from_dict(**val) for idx, val in enumerate(tool_sequence)}
        )


@dataclass
class ToolChainParserConfig(BaseDataClass):
    router_config: RouterConfig | None = None
    purpose: str | None = None
    command: str | None = None

    @classmethod
    def from_dict(cls, **kwargs) -> 'ToolChainParserConfig':
        """
        Classmethod to create a ToolChainParserConfig instance from a dictionary

        :param kwargs: Dictionary containing the ToolChainParserConfig data
        :returns: A freshly created ToolChainParserConfig instance
        """
        router_config = kwargs.pop('router_config', [])
        return super().from_dict(
            **kwargs,
            router_config=RouterConfig.from_dict(**router_config) if router_config else None
        )

    def __getitem__(self, name):
        return getattr(self, name)

    def get(self, name, default=None):
        return getattr(self, name, default)


@dataclass
class ToolChainModule(BaseDataClass):
    """
    ToolChainModule entity to represent a BotModule that is part of a ToolChain
    """
    id: int
    module: AvailableModule
    parser_configuration: dict = field(default_factory=dict)
    context_providers: list[ContextProvider] = field(default_factory=list)
    configuration_values: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, **kwargs) -> 'ToolChainModule':
        """
        Classmethod to create a ToolChainModule instance from a dictionary

        :param kwargs: Dictionary containing the ToolChainModule data
        :returns: A freshly created ToolChainModule instance
        """
        context_providers = kwargs.pop('context_providers', [])
        module = kwargs.pop('module', {})

        return super().from_dict(
            **kwargs,
            module=AvailableModule.from_dict(**module) if module else None,
            context_providers=[ContextProvider.from_dict(**c) for c in context_providers]
        )


@dataclass
class ToolChain(BaseDataClass):
    """
    ToolChain entity to represent a sequence of BotModules that are executed in a sequence
    """
    id: int
    name: str
    tool_chain_modules: list[ToolChainModule]
    is_active: bool = True
    parser_configuration: ToolChainParserConfig | None = None
    has_reengagement: bool = False
    reengagement_message: str | None = None
    reengagement_timeout_minutes: int | None = None

    @property
    def internal_id(self) -> str:
        return f'T{self.id}'

    @property
    def intentions(self) -> List[str]:
        """
        Getter for the intentions of the ToolChain

        :returns: List of intentions
        """
        return self.get_module_by_index(0).module.intentions

    def get_module_by_index(self, index):
        """
        Getter for a ToolChainModule by index

        :param index: Index of the ToolChainModule to retrieve
        :returns: ToolChainModule instance
        """
        tool = self.parser_configuration.router_config.tool_sequence.get(str(index))
        if not tool:
            return None
        module = [chain_module for chain_module in self.tool_chain_modules if chain_module.id == tool.id]
        return module[0] if module else None

    @property
    def module(self) -> AvailableModule:
        return self.get_module_by_index(0).module

    @property
    def configuration_values(self) -> dict:
        return self.get_module_by_index(0).configuration_values

    @property
    def context_providers(self) -> List[ContextProvider]:
        return self.get_module_by_index(0).context_providers

    @classmethod
    def from_dict(cls, **kwargs) -> 'ToolChain':
        """
        Classmethod to create a ToolChain instance from a dictionary

        :param kwargs: Dictionary containing the ToolChain data
        :returns: A freshly created ToolChain instance
        """
        tool_chain_modules = kwargs.pop('tool_chain_modules', [])
        config = kwargs.pop('parser_configuration', {})
        return super().from_dict(
            **kwargs,
            parser_configuration=ToolChainParserConfig.from_dict(**config) if config else None,
            tool_chain_modules=[ToolChainModule.from_dict(**i) for i in tool_chain_modules]
        )
