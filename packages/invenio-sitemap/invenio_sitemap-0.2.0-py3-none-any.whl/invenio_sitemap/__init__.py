# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# invenio-sitemap is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sitemap indices and sitemaps for InvenioRDM."""

from .cache import SitemapCache, SitemapIndexCache
from .ext import InvenioSitemap
from .sitemap import SitemapSection
from .utils import format_to_w3c, iterate_urls_of_sitemap_indices

__version__ = "0.2.0"

__all__ = (
    "__version__",
    "InvenioSitemap",
    "SitemapCache",
    "SitemapIndexCache",
    "SitemapSection",
    "format_to_w3c",
    "iterate_urls_of_sitemap_indices",
)
