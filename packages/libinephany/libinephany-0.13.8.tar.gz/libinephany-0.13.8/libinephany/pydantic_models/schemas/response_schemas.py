# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

from pydantic import BaseModel

from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfigs
from libinephany.pydantic_models.configs.observer_config import AgentObserverConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class BackendResponse(BaseModel):

    inephany_model_status: str
    actions_array: list[Any]
    hidden_states: list[list[Any]] | None = None


class AgentScheduleResponse(BaseModel):
    action: float
    hyperparameter_internal_value: float | int
    agent_type: str
    inephany_model_status: str


class ClientScheduleResponse(BaseModel):
    actions: dict[str, AgentScheduleResponse] = {}

    response_time: float | None = None


class ClientPolicySchemaResponse(BaseModel):
    observation_clipping_threshold: float
    invalid_observation_threshold: float
    invalid_observation_replacement_value: float

    standardizer: str
    standardizer_arguments: dict[str, Any]

    agent_observer_configs: dict[str, AgentObserverConfig]
    hyperparameter_configs: HParamConfigs
