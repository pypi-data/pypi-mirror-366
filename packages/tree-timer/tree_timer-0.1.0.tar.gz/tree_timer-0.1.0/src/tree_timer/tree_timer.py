"""TreeTimer: A Hierarchical Timer Class for Nested Execution Scopes."""

from contextlib import contextmanager
from time import perf_counter
from typing import Any, Iterator


class TreeTimer:
    """A hierarchical timer for measuring nested execution scopes.

    Allows structured timing of named code blocks using context managers. Each
    scope can have sub-scopes, either as single child timers or lists of timers,
    and the entire structure can be visualized in a tree format.
    """

    def __init__(self) -> None:
        """Initializes the TreeTimer."""
        self._start: float | None = None
        self._total: float = 0.0
        self._children: dict[Any, "TreeTimer | list[TreeTimer]"] = {}

    def __enter__(self) -> "TreeTimer":
        """Starts the timer when entering a `with` block.

        Returns:
            TreeTimer: The instance itself.
        """
        self._start = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Stops the timer when exiting a `with` block.

        Args:
            exc_type: The type of exception raised, if any.
            exc_val: The exception instance raised, if any.
            exc_tb: The traceback object, if any.
        """
        self._stop()

    def __repr__(self, indent: int = 0, scope_name: str = "root") -> str:
        """Returns a string representation of the timing tree.

        Args:
            indent (int, optional): The indentation level. Defaults to 0.
            scope_name (str, optional): The name of the current scope. Defaults to "root".

        Returns:
            str: A formatted string representing the timer tree.
        """
        pad = "  " * indent
        lines = [f"{pad}{scope_name}: {self.total:.6f}s"]
        for key, child in self._children.items():
            if isinstance(child, TreeTimer):
                lines.append(child.__repr__(indent + 1, str(key)))
            elif isinstance(child, list):
                sum_total = sum(c.total for c in child)
                lines.append(f"{pad}  {key}: {sum_total:.6f}s")
                for i, c in enumerate(child):
                    lines.append(c.__repr__(indent + 2, f"[{i}]"))
        return "\n".join(lines)

    def _stop(self) -> None:
        """Stops the timer and accumulates elapsed time."""
        if self._start is not None:
            self._total += perf_counter() - self._start
            self._start = None

    @property
    def total(self) -> float:
        """Calculates the total elapsed time for this scope and its children.

        Returns:
            float: Total time in seconds.
        """
        if self._total > 0:
            return self._total
        return sum(
            v.total if isinstance(v, TreeTimer) else sum(c.total for c in v)
            for v in self._children.values()
        )

    def add_series(self, key: Any, n: int) -> list["TreeTimer"]:
        """Adds a series of `n` child timers under the given key.

        Args:
            key (Any): Identifier for the group of timers.
            n (int): Number of timers to create.

        Returns:
            list[TreeTimer]: A list of newly created timers.

        Raises:
            ValueError: If the key already exists in the children.
        """
        if key in self._children:
            raise ValueError(f"Timer with key '{key}' already exists.")
        series = [TreeTimer() for _ in range(n)]
        self._children[key] = series
        return series

    @contextmanager
    def add_scope(self, key: Any) -> Iterator["TreeTimer"]:
        """Adds a named child timer as a context manager.

        Args:
            key (Any): Name of the child scope.

        Yields:
            TreeTimer: A timer instance that is automatically started and stopped.

        Raises:
            ValueError: If the key already exists in the children.
        """
        if key in self._children:
            raise ValueError(f"Timer with key '{key}' already exists.")

        timer = TreeTimer()
        self._children[key] = timer
        timer._start = perf_counter()
        try:
            yield timer
        finally:
            timer._stop()

    def to_dict(self, scope_name: str = "root") -> dict[str, Any]:
        """Converts the timer and its children into a nested dictionary.

        Args:
            scope_name (str, optional): The name of the current scope. Defaults to "root".

        Returns:
            dict[str, Any]: Dictionary representation of the timer tree.
        """
        children = []

        for key, child in self._children.items():
            if isinstance(child, TreeTimer):
                children.append(child.to_dict(str(key)))
            elif isinstance(child, list):
                group = {
                    "name": str(key),
                    "total": sum(c.total for c in child),
                    "children": [c.to_dict(f"[{i}]") for i, c in enumerate(child)],
                }
                children.append(group)

        return {
            "name": scope_name,
            "total": self.total,
            "children": children,
        }
