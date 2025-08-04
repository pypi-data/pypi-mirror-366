#!/usr/bin/env  python3
# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum

from avin_data.utils import CategoryNotFound


class Category(enum.Enum):
    """All categories enum."""

    CURRENCY = 1
    INDEX = 2
    SHARE = 3
    BOND = 4
    FUTURE = 5
    OPTION = 6
    ETF = 7

    @classmethod
    def from_str(cls, string: str) -> Category:
        """Get enum from str.

        Args:
            string: category name.

        Returns:
            Category Enum.

        Raises:
            CategoryNotFound if category not exists.
        """
        if attr := getattr(cls, string.upper(), None):
            return attr

        raise CategoryNotFound(
            f"Category not found. Choice from {Category._member_names_}"
        )
