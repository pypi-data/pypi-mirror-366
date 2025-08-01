from typing import Any
from typing import ClassVar
from typing import Optional

from amsdal_models.builder.validators.options_validators import validate_options
from amsdal_utils.models.enums import ModuleType
from pydantic.fields import Field
from pydantic.functional_validators import field_validator

from amsdal.contrib.frontend_configs.models.frontend_activator_config import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_async_validator import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_control_action import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_option import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_slider_option import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_text_mask import *  # noqa: F403
from amsdal.contrib.frontend_configs.models.frontend_config_validator import *  # noqa: F403


class FrontendControlConfig(FrontendConfigSkipNoneBase):  # noqa: F405
    __module_type__: ClassVar[ModuleType] = ModuleType.CONTRIB
    type: str = Field(title='Type')
    name: str = Field(title='Name')
    label: str | None = Field(None, title='Label')
    required: bool | None = Field(None, title='Required')
    hideLabel: bool | None = Field(None, title='Hide Label')  # noqa: N815
    actions: list['FrontendConfigControlAction'] | None = Field(None, title='Actions')  # noqa: F405
    validators: list['FrontendConfigValidator'] | None = Field(None, title='Validators')  # noqa: F405
    asyncValidators: list['FrontendConfigAsyncValidator'] | None = Field(  # noqa: F405, N815
        None,
        title='Async Validators',
    )
    activators: list['FrontendActivatorConfig'] | None = Field(None, title='Activators')  # noqa: F405
    additionalText: str | None = Field(None, title='Additional Text')  # noqa: N815
    value: Any | None = Field(None, title='Value')
    placeholder: str | None = Field(None, title='Placeholder')
    options: list['FrontendConfigOption'] | None = Field(None, title='Options')  # noqa: F405
    mask: Optional['FrontendConfigTextMask'] = Field(None, title='Mask')  # noqa: F405
    controls: list['FrontendControlConfig'] | None = Field(None, title='Controls')
    showSearch: bool | None = Field(None, title='Show Search')  # noqa: N815
    sliderOptions: Optional['FrontendConfigSliderOption'] = Field(None, title='Slider Option')  # noqa: F405, N815
    customLabel: list[str] | None = Field(None, title='Custom Label')  # noqa: N815
    control: Optional['FrontendControlConfig'] = Field(None, title='Control')
    entityType: str | None = Field(None, title='Entity Type')  # noqa: N815

    @field_validator('type')
    @classmethod
    def validate_value_in_options_type(cls: type, value: Any) -> Any:  # type: ignore # noqa: A003
        return validate_options(
            value,
            options=[
                'Bytes',
                'array',
                'checkbox',
                'date',
                'dateTriplet',
                'datetime',
                'dict',
                'dropzone',
                'email',
                'file',
                'group',
                'group_switch',
                'group_toggle',
                'info-group',
                'infoscreen',
                'multiselect',
                'number',
                'number-operations',
                'number-slider',
                'number_equals',
                'number_initial',
                'number_minus',
                'number_plus',
                'object',
                'object_group',
                'object_latest',
                'password',
                'phone',
                'radio',
                'select',
                'text',
                'textarea',
                'time',
                'toggle',
            ],
        )
