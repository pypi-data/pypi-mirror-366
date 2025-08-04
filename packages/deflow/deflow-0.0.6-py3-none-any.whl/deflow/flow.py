# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
"""Flow is the core module."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, cast

from ddeutil.workflow import Result, Workflow
from ddeutil.workflow import config as workflow_config
from typing_extensions import Self

from .__types import DictData, TupleStr
from .conf import ASSETS_PATH, dynamic

Version = Literal["v1", "v2", "v3"]
RUN_MODES: TupleStr = (
    "N",
    "R",
    "F",
    "T",
)


def workflow_factory(
    name: str,
    version: str,
    *,
    extras: Optional[DictData] = None,
) -> Workflow:
    """Workflow function for create the Workflow instance base on the version of
    data framework.

    Args:
        name (str): A name of data pipeline.
        version (str): A version of data framework.
        extras: An extra parameter that want to override core config values.

    Returns:
        Workflow: A workflow instance that already override config that fit with
            this package.
    """
    extras: DictData = {
        **{
            "conf_path": ASSETS_PATH / f"{version}/templates",
            "registry_caller": [
                f"deflow.assets.{version}.core",
                *dynamic("deflow_registry_caller", extras=extras),
            ],
            "conf_paths": [dynamic("deflow_conf_path", extras=extras)],
        },
        **(extras or {}),
    }
    # NOTE: Get the current audit path for override with name of metadata
    #   config, it will add `/{metadata}={name}` to the end of the URL path.
    audit_conf: dict[str, Any] = workflow_config.audit_conf
    if version == "v1":
        if audit_conf["type"] == "file":
            current_audit_url_path: str = audit_conf["path"]
            audit_conf["path"] = current_audit_url_path + f"/stream={name}"
        return Workflow.from_conf(
            name="stream-workflow",
            extras=extras | {"audit_conf": audit_conf},
        )
    elif version == "v2":
        if audit_conf["type"] == "file":
            current_audit_url_path: str = audit_conf["path"]
            audit_conf["path"] = current_audit_url_path + f"/pipeline={name}"
        return Workflow.from_conf(
            name="pipeline-workflow",
            extras=extras | {"audit_conf": audit_conf},
        )
    raise NotImplementedError(f"Flow version: {version!r} does not implement.")


class Flow:
    """Flow object for manage workflow model release and test via configuration.
    This is the core object for this package that active data pipeline from
    the current data framework version.

    Attributes:
        name (str): A main workflow parameter name.
        version (str): A version of data framework.
        extras (DictData): An extra parameters that want to override the
            workflow config.
    """

    def __init__(
        self,
        name: str,
        *,
        version: Optional[Version] = None,
        extras: Optional[DictData] = None,
    ) -> None:
        self.name: str = name

        if (_v := dynamic("version", f=cast(str, version))) not in (
            "v1",
            "v2",
            "v3",
        ):
            raise ValueError(
                "Version of data framework should be one of ('v1', 'v2', 'v3') "
                "only."
            )
        self.version: Version = cast(Version, _v)

        self.extras: DictData = extras or {}

        # NOTE: Factory the workflow from the override params.
        self.workflow: Workflow = workflow_factory(
            name,
            version=self.version,
            extras=self.extras,
        )

    def __repr__(self) -> str:
        """Override __repr__ method."""
        return f"{self.__class__.__name__}(name={self.name})"

    def __str__(self) -> str:
        """Override __str__ method."""
        return self.name

    def option(self, key: str, value: Any) -> Self:
        """Update the extras option with specific key and value.

        :param key: A key of the extra parameter that want to update.
        :param value: A value of the extra parameter that want to update.
        """
        self.extras[key] = value
        return self

    def options(self, values: dict[str, Any]) -> Self:
        """Update the extras option with mapping values.

        :param values: A mapping value that want to update.
        """
        self.extras.update(values)
        return self

    def run(
        self, dt: Optional[datetime] = None, mode: Optional[str] = None
    ) -> Result:
        """Start release dynamic pipeline with this flow name.

        :param dt: (datetime) A release datetime that want to run.
        :param mode: (str) A running mode of this flow.

        :rtype: Result
        """
        if mode:
            assert mode in RUN_MODES, "The running mode does not valid."
        return self.workflow.release(
            release=dt or datetime.now(),
            params={
                "name": self.name,
                "run-mode": mode or "N",
            },
        )

    def test(self) -> Result:
        """Test running flow on local without integration testing.

        :rtype: Result
        """
        return self.run(mode="TEST")

    def ui(self) -> str:
        """Return graph of this flow from the config data."""

    def docs(self) -> str:
        """Return markdown statement that was generated base on version of data
        framework.
        """
