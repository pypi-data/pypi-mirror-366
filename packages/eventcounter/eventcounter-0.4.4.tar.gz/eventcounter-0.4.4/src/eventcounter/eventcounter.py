## -----------------------------------------------------------
#### Class EventCounter()
# Class to log/count events, pass them to parent function
# and merge the results
## -----------------------------------------------------------

from collections import defaultdict
from typing import Optional, Iterable, Callable
from asyncio import gather, Task
from deprecated import deprecated
from multilevellogger import getMultiLevelLogger, MultiLevelLogger

logger: MultiLevelLogger = getMultiLevelLogger(__name__)

debug = logger.debug
message = logger.message
verbose = logger.verbose
error = logger.error

# FuncTypeFormatter = Callable[[str], str]
# FuncTypeFormatterParam = Optional[FuncTypeFormatter]


class EventCounter:
    """
    Count events and merge event counts from other EventCounters as a child or sibling

    Usage:

    from eventcounter import EventCounter

    stats = EventCounter("Demo counter")

    stats.log("tests")
    stats.log("errors")
    stats.log("added", 3)

    stats.print()
    """

    def __init__(
        self,
        name: str = "",
        totals: Optional[str] = None,
        # categories: set[str] = set(),
        errors: set[str] = set(),
        separator: str = ": ",
        format_spec: str = "{category:<{col_width}}{separator}{value}",
        print_func: Callable[[str], None] = print,
    ):
        assert name is not None, "param 'name' cannot be None"
        # assert categories is not None, "param 'categories' cannot be None"
        assert errors is not None, "param 'errors' cannot be None"

        self.name: str = name
        self._log: defaultdict[str, int] = defaultdict(
            int
        )  # returns 0 if key not found
        self._errors: set[str] = errors
        self._totals = totals
        self._separator: str = separator
        self._format_spec: str = format_spec
        self._print_func: Callable[[str], None] = print_func

    def log(self, category: str, count: int = 1) -> int:
        assert category is not None, "category cannot be None"
        assert count is not None, "count cannot be None"
        self._log[category] += count
        return self._log[category]

    def get_long_cat(self, category: str) -> str:
        """
        Get the long category name including the name of the EventCounter
        """
        assert category is not None, "param 'category' cannot be None"
        return f"{self.name}{self._separator}{category}"

    def _get_str(self, category: str, col_width: int = 40) -> str:
        assert category is not None, "category cannot be None"
        return self._format_spec.format(
            category=category,
            col_width=col_width,
            separator=self._separator,
            value=self.get(category),
        )

    # TODO: remove later
    @deprecated(version="0.4.0", reason="use get() instead")
    def get_value(self, category: str) -> int:
        assert category is not None, "param 'category' cannot be None"
        return self._log[category]

    def get(self, category: str) -> int:
        """ "
        Get the value of a category
        """
        assert category is not None, "param 'category' cannot be None"
        return self._log[category]

    # TODO: remove later
    @deprecated(version="0.4.0", reason="use values() property instead")
    def get_values(self) -> dict[str, int]:
        return self._log

    @property
    def values(self) -> dict[str, int]:
        return self._log.copy()

    @property
    def error_values(self) -> dict[str, int]:
        """
        Get the values of the error categories"""
        return {key: self._log[key] for key in self._log.keys() & self._errors}

    def sum(self, categories: Iterable[str]) -> int:
        """
        Sum the values of the categories
        """
        ret = 0
        for cat in categories:
            ret += self.get(cat)
        return ret

    # TODO: remove later
    @deprecated(version="0.4.0", reason="use categories() property instead")
    def get_categories(self) -> list[str]:
        return list(self._log.keys())

    @property
    def categories(self) -> list[str]:
        return sorted(self._log.keys())

    @property
    def errors(self) -> list[str]:
        return sorted(self._errors)

    # TODO: remove later
    @deprecated(version="0.4.0", reason="use error_status() property instead")
    def get_error_status(self) -> bool:
        return self.sum(self._errors) > 0

    @property
    def error_status(self) -> bool:
        return self.sum(self._errors) > 0

    def merge(self, B: "EventCounter") -> bool:
        """Merge two EventCounter instances together"""
        assert isinstance(B, EventCounter), (
            f"input is not type of 'EventCounter' but: {type(B)}"
        )

        try:
            for cat in B.categories:
                value: int = B.get(cat)
                self.log(cat, value)
                if self._totals is not None:
                    # self.log(f"{self._totals}: {cat}", value)
                    self.log(self._totals, value)
            return True
        except Exception as err:
            error(f"{err}")
        return False

    def merge_child(self, B: "EventCounter") -> bool:
        """Merge two EventCounter instances together"""
        assert isinstance(B, EventCounter), (
            f"input is not type of 'EventCounter' but: {type(B)}"
        )

        try:
            for cat in B.categories:
                value: int = B.get(cat)
                self.log(B.get_long_cat(cat), value)
                if self._totals is not None:
                    self.log(f"{self._totals}: {cat}", value)
            # self._error_status = self._error_status or B.get_error_status()
            return True
        except Exception as err:
            error(f"{err}")
        return False

    def get_header(self) -> str:
        return f"{self.name}" + (
            f"{self._separator}ERROR occurred" if self.error_status else ""
        )

    @property
    def header(self) -> str:
        return f"{self.name}" + (
            f"{self._separator}ERROR occurred" if self.error_status else ""
        )

    @property
    def col_width(self) -> int:
        """
        Set category column width based on the longest column
        """
        if len(self._log) == 0:
            return 10
        return len(max(self._log.keys(), key=len)) + 3

    def print(self, do_print: bool = True, clean: bool = False) -> Optional[str]:
        try:
            width: int = self.col_width
            if do_print:
                message(self.get_header())
                for cat in sorted(self._log):
                    if clean and self.get(cat) == 0:
                        continue
                    self._print_func(self._get_str(cat, width))
                return None
            else:
                ret = self.get_header()
                for cat in sorted(self._log):
                    if clean and self.get_value(cat) == 0:
                        continue
                    ret += f"\n{self._get_str(cat, width)}"
                return ret
        except Exception as err:
            error(f"{err}")
        return None

    @deprecated(version="0.4.0", reason="use gather() instead")
    async def gather_stats(
        self, tasks: list[Task], merge_child: bool = True, cancel: bool = True
    ) -> None:
        """
        Wrapper to gather results from tasks and return the stats and the LAST exception
        """
        await self.gather(tasks, merge_child, cancel)

    async def gather(
        self, tasks: list[Task], merge_child: bool = False, cancel: bool = False
    ) -> None:
        """
        Wrapper to gather results from tasks and return the stats and the LAST exception
        """
        if cancel:
            for task in tasks:
                task.cancel()
        for res in await gather(*tasks, return_exceptions=True):
            if isinstance(res, EventCounter):
                if merge_child:
                    self.merge_child(res)
                else:
                    self.merge(res)
            elif type(res) is BaseException:
                error(f"Task raised an exception: {res}")
        return None
