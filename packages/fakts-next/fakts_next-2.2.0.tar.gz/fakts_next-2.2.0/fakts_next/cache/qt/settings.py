import logging
from qtpy import QtCore


from fakts_next.grants.remote.models import FaktsEndpoint
from typing import Optional, Dict
import datetime
from fakts_next.protocols import FaktValue
from pydantic import BaseModel, ConfigDict, Field
from fakts_next.cache.model import CacheModel

logger = logging.getLogger(__name__)


class QtSettingsCache(BaseModel):
    """Retrieves and stores users matching the currently
    active fakts grant"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: QtCore.QSettings  # type: ignore #
    save_key: str = "fakts_cache"
    hash: str = Field(
        default_factory=lambda: "",
        description="Validating against the hash of the config",
    )

    async def aset(self, value: Dict[str, FaktValue]) -> None:
        """Stores the value in the settings

        Parameters
        ----------
        value : Dict[str, FaktValue]
            The value to store
        """

        cache = CacheModel(config=value, created=datetime.datetime.now(), hash=self.hash)

        self.settings.setValue(self.save_key, cache.model_dump_json())  # type: ignore #

    async def aload(self) -> Optional[Dict[str, FaktValue]]:
        """Loads the value from the settings

        Returns
        -------
        Optional[Dict[str, FaktValue]]
            The value, or None if there is no value
        """

        un_storage: str = self.settings.value(self.save_key, None)  # type: ignore #
        if not un_storage:
            return None

        if not isinstance(un_storage, str):
            logger.warning("Cache is not a string")
            raise ValueError("Cache is not a string")
        try:
            storage = CacheModel.model_validate_json(un_storage)
            if storage.hash != self.hash:
                return None

            return storage.config
        except Exception as e:
            logger.error("Cache is not a string", exc_info=e)

        return None

    async def areset(self) -> Optional[FaktsEndpoint]:
        """A function that gets the default endpoint

        Returns
        -------
        Optional[FaktsEndpoint]
            The stored endpoint, or None if there is no endpoint

        """

        self.settings.setValue(self.save_key, None)  # type: ignore #
