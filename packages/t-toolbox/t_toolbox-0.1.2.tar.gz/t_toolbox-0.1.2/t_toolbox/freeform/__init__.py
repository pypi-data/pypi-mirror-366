# Copyright (C) 2025 taitep <taitep@taitep.se>
#
# This file is licensed under the GNU GPL v3 or later.
# See <https://www.gnu.org/licenses/>

class Freeform:
    """
    Class that can have any fields the user wants.
    """

    def __init__(self, **fields) -> None:
        for field, value in fields.items():
            self.__setattr__(field, value)
