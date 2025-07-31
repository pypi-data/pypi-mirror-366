#!/usr/bin/env python

"""Tests for `verigen` package."""

import pytest

from verigen import common


def test_add():
    """Test Add"""
    assert common.add(3, 5) == 8


def test_add_list():
    """Test Add List"""
    with pytest.raises(TypeError):
        common.add([3], "5")
