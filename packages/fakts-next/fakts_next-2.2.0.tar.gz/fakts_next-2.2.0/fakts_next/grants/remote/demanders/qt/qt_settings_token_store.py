import logging
from qtpy import QtCore

from fakts_next.grants.remote.models import FaktsEndpoint


from typing import Dict, Optional

import json
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class EndpointDefaults(BaseModel):
    """A serialization helper for the
    default token store"""

    default_token: Dict[str, str] = {}


class QTSettingTokenStore(BaseModel):
    """Retrieves and stores users matching the currently
    active fakts_next grant"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: QtCore.QSettings  # type: ignore
    """The settings to use to store the tokens"""
    save_key: str
    """The key to use to store the tokens"""

    async def aput_default_token_for_endpoint(self, endpoint: FaktsEndpoint, token: str) -> None:
        """A function that puts the default token for an endpoint
        from the settings

        Parameters
        ----------
        endpoint : FaktsEndpoint
            The endpoint to put the token for
        token : str
            The token to put, or None to delete the token
        """

        un_storage = self.settings.value(self.save_key, None)  # type: ignore
        if not un_storage:
            storage = EndpointDefaults()
        else:
            try:
                storage = EndpointDefaults(**json.loads(un_storage))  # type: ignore
            except Exception as e:
                print("Error loading token store", e)
                storage = EndpointDefaults()

        if endpoint.base_url in storage.default_token:
            del storage.default_token[endpoint.base_url]
        else:
            storage.default_token[endpoint.base_url] = token

        self.settings.setValue(self.save_key, storage.model_dump_json())  # type: ignore

    async def aget_default_token_for_endpoint(self, endpoint: FaktsEndpoint) -> Optional[str]:
        """A function that gets the default token for an endpoint
        from the settings

        Parameters
        ----------
        endpoint : FaktsEndpoint
            The endpoint to get the token for

        Returns
        -------
        Optional[str]
            The token for the endpoint, or None if there is no token
        """

        un_storage = self.settings.value(self.save_key, None)  # type: ignore
        if not un_storage:
            return None
        try:
            storage = EndpointDefaults(**json.loads(un_storage))  # type: ignore
            if endpoint.base_url in storage.default_token:
                return storage.default_token[endpoint.base_url]
        except Exception as e:
            print(e)
            return None

        return None
