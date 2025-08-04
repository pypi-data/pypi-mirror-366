import json
from pathlib import Path
from typing import Union

from ddeutil.io import YamlEnvFl

from ....__types import DictData, ListData


def get_assets(name: str, path: Path) -> Union[DictData, ListData]:
    """Get the node asset data from a specific path."""
    data: Union[DictData, ListData] = {}
    if (file := (path / name)).exists():
        if file.is_dir():
            raise NotImplementedError(
                f"Asset location does not support for dir type, {file}."
            )

        if file.suffix in (".yml", ".yaml"):
            data = YamlEnvFl(path=file).read()
        elif file.suffix in (".json",):
            data = json.loads(file.read_text(encoding="utf-8"))
        elif file.suffix in (".sql", ".txt"):
            data["raw_text"] = file.read_text(encoding="utf-8")
        else:
            raise NotImplementedError(
                f"Asset file format does not support yet, {file}. "
                f"For the currently, it already support for `json`, `yaml`, "
                f"and `sql` file formats."
            )

    return data
