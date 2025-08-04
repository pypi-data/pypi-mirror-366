import copy
from pathlib import Path
from typing import Any, Optional

from ddeutil.workflow.job import Rule
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Literal, Self

from ....__types import DictData
from ...models import AbstractModel
from ...utils import ConfData, get_conf, get_data


class Deps(BaseModel):
    """Dependency model."""

    name: str = Field(description="A node name")
    trigger_rule: Optional[Rule] = Field(default=None)


class Node(BaseModel):
    """Node model.

        The node model will represent the minimum action for ETL/ELT/EL or
    trigger or hook external API/SDK.
    """

    type: Literal["Node"] = "Node"
    conf_dir: Path = Field(description="A dir path of this config data.")
    name: str = Field(description="A node name.")
    pipeline_name: Optional[str] = Field(
        default=None, description="A pipeline name of this node."
    )
    desc: Optional[str] = Field(default=None)
    upstream: list[Deps] = Field(default_factory=list)
    operator: str = Field(description="An node operator.")
    task: str = Field(description="A node task.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="An any parameters that want to use on this node.",
    )

    @classmethod
    def from_conf(cls, name: str, path: Path) -> Self:
        """Construct Node model from an input node name and config path."""
        data: DictData = get_data(name=name, path=path)

        if (t := data.get("type", "EMPTY")) != cls.__name__:
            raise ValueError(f"Type {t!r} does not match with {cls}")

        loader_data: DictData = copy.deepcopy(data)
        return cls.model_validate(obj=loader_data)


class Lineage(BaseModel):
    inlets: list[Deps] = Field(default_factory=list)
    outlets: list[Deps] = Field(default_factory=list)


class Pipeline(AbstractModel):
    """Pipeline model."""

    type: Literal["Pipeline"] = "Pipeline"
    name: str = Field(description="A pipeline name.")
    desc: Optional[str] = Field(
        default=None,
        description=(
            "A pipeline description that allow to write with markdown syntax."
        ),
    )
    nodes: dict[str, Node] = Field(
        default_factory=list, description="A list of Node model."
    )

    @classmethod
    def load_conf(cls, name: str, path: Path) -> DictData:
        """Load config data from a specific searching path."""
        load_data: ConfData = get_conf(name, path=path)

        # NOTE: Start prepare node config data.
        nodes: dict[str, Node] = {}
        for child in load_data["children"]:
            if child["conf"].get("type", "EMPTY") != Node.__name__:
                continue

            try:
                node = Node.model_validate(child["conf"])
                nodes[node.name] = node
            except ValidationError:
                continue
        return {"nodes": nodes, **load_data["conf"]}

    def node(self, name: str) -> Node:
        """Get the Node model with pass the specific node name.

        Args:
            name (str): A node name.

        Returns:
            Node: A Node model instance that match with an input name.
        """
        if name not in self.nodes:
            raise ValueError(
                f"Node name: {name!r} does not exist or set on this pipline."
            )
        return self.nodes[name]

    def node_priorities(self) -> list[list[str]]:
        """Generate the Node priorities that convert from its upstream field.

        Returns:
            list[list[str]]: Order of priority node name.
        """

        if not self.nodes:
            return []

        # NOTE: Build reverse adjacency list and in-degree count in one pass
        in_degree: dict[str, int] = {}

        # NOTE: node -> [nodes that depend on it]
        dependents = {}

        for node in self.nodes:
            in_degree[node] = 0
            dependents[node] = []

        # NOTE: Build graph
        for node, config in self.nodes.items():
            if config.upstream:
                for upstream in config.upstream:
                    upstream_name = upstream.name

                    # NOTE: Add upstream node if not seen before
                    if upstream_name not in in_degree:
                        in_degree[upstream_name] = 0
                        dependents[upstream_name] = []

                    # NOTE: Update relationships
                    in_degree[node] += 1
                    dependents[upstream_name].append(node)

        # NOTE: Kahn's algorithm with level-by-level processing
        result: list[list[str]] = []
        current_level: list[str] = [
            node for node, degree in in_degree.items() if degree == 0
        ]

        while current_level:

            # NOTE: For consistent output
            current_level.sort()

            # NOTE: Shallow copy
            result.append(current_level[:])

            next_level: list[str] = []
            for node in current_level:

                # NOTE: Decrease in-degree for all dependents
                for dependent in dependents[node]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_level.append(dependent)

            current_level = next_level

        # NOTE: Cycle detection
        if sum(in_degree.values()) > 0:
            raise ValueError("Circular dependency detected")

        return result

    def lineage(self) -> list[Lineage]: ...
