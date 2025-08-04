"""
This package contains everything related to the generation of Kubernetes manifests via Nyl.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from concurrent.futures import Future, as_completed
from typing import Any, ClassVar, Generic, Sequence, TypeVar

from stablehash import stablehash

from nyl.resources import NylResource
from nyl.tools.types import Resource, ResourceList

T = TypeVar("T")


class Generator(ABC, Generic[T]):
    """
    Base class for generating Kubernetes resources from Nyl resources.
    """

    resource_type: ClassVar[type[Any]]

    def __init_subclass__(cls, resource_type: type[T], **kwargs: Any) -> None:
        cls.resource_type = resource_type
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def generate(self, /, resource: T) -> ResourceList:
        """
        Evaluate a Nyl resource and return a list of the generated Kubernetes manifests.
        """

        raise NotImplementedError


def reconcile_generator(
    generator: Generator[Resource],
    initial_resources: ResourceList,
    new_generation_callback: Callable[[Resource], Future[ResourceList]],
    skip_resources: Sequence[type[NylResource]] = (),
) -> ResourceList:
    """
    Recursively reconcile all Nyl resources in the list of resources using the given generator.

    Args:
        generator: The generator to use for generating resources from Nyl resources.
        initial_resources: The list of resources to reconcile.
        new_generation_callback: A callback to call on each generated resource, giving the opportunity to modify it
            or generate other resources from it. This callback should return a Future, allowing the reconciliation to be
            asynchronous. The callback should take a single argument, which is the resource to generate from.
        skip_resources: A list of Nyl resources to ignore.
    """

    queue: list[Future[ResourceList]] = []

    future = Future[ResourceList]()
    future.set_result(initial_resources)
    queue.append(future)

    result = ResourceList([])
    seen = set()
    loops = 0

    while queue:
        if loops > 1000:
            raise RuntimeError("Reconciliation loop limit exceeded (1000).")

        future = next(as_completed(queue))
        queue.remove(future)
        for resource in future.result():
            resource_hash = stablehash(resource).hexdigest()
            if resource_hash in seen:
                # If we've seen this resource in its exact state before, then it has not been further expanded or
                # transformed, and we consider it final.
                result.append(resource)

            else:
                seen.add(resource_hash)
                if any(t.matches(resource) for t in skip_resources):
                    future = Future[ResourceList]()
                    future.set_result(ResourceList([resource]))
                    queue.append(future)
                else:
                    for generated_resource in generator.generate(resource):
                        queue.append(new_generation_callback(generated_resource))
                loops += 1

    return result
