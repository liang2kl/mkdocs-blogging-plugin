#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from mkdocs_blogging_plugin import plugin


def test_sorted_pages_mock():
    obj = plugin.BloggingPlugin()
    with pytest.raises(KeyError):
        obj.sorted_pages([mock.MagicMock()])


def test_sorted_pages_with_sort():
    obj = plugin.BloggingPlugin()
    obj.sort = {"from": ""}
    obj.sorted_pages([mock.MagicMock()])


def test_sorted_pages_empty_page_meta():
    obj = plugin.BloggingPlugin()
    obj.sort = {"from": ""}
    page = mock.MagicMock()
    page.meta = {}
    obj.sorted_pages([page])
