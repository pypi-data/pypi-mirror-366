# Copyright (C) 2025 taitep <taitep@taitep.se>
#
# This file is licensed under the GNU GPL v3

from dataclasses import dataclass, field


@dataclass
class Consumable:
    """
    Bool that resets to False when used.
    """

    value: bool = field(default=False)
    reset: bool = field(default=False)

    def __bool__(self):
        """
        Consume and return value.
        """

        value = self.value
        self.value = self.reset
        return value
