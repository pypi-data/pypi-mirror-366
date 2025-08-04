import copy
from pathlib import Path
from typing import cast

from pydantic import BaseModel, Field

from deflow.assets.utils import ConfData, get_conf

from ....__types import DictData
from ...models import AbstractModel
from .utils import get_assets


class Task(BaseModel):
    name: str
    operator: str


class Dag(AbstractModel):
    assets: list[str] = Field(default_factory=list)

    @classmethod
    def load_conf(cls, name: str, path: Path) -> DictData:
        """Construct Node model from an input node name and config path."""
        data: ConfData = get_conf(name=name, path=path)

        if (t := data.pop("type")) != cls.__name__:
            raise ValueError(f"Type {t!r} does not match with {cls}")

        return cast(DictData, copy.deepcopy(data))

    def asset(self, name: str) -> DictData:
        """Get the asset data with a specific name.

        :param name: (str) An asset name that want to load from the config path.
        """
        if name not in self.assets:
            raise ValueError(f"This asset, {name!r}, does not exists.")
        return get_assets(name, path=self.conf_dir)

    def sync_assets(self) -> DictData:
        """Return mapping of its asset name and asset data from the conf path.

        :rtype: DictData
        """
        return {
            asset_name: self.asset(asset_name) for asset_name in self.assets
        }
