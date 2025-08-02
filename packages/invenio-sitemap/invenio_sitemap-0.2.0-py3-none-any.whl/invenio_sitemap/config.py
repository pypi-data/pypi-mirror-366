# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# invenio-sitemap is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration."""

SITEMAP_MAX_ENTRY_COUNT = 10000
"""Maximum number of entries (<url> or <sitemap>) per file.

The Sitemap protocol sets it at 50_000, but it also sets the max size of the
resulting file at 50 MiB. Following the initial Zenodo implementation, we
set it much lower than 50_000 so as to not have to check for generated size.

Following the initial Zenodo implementation, we use the same config for the
number of entries in the Sitemap Index and Sitemap files.
"""

SITEMAP_SECTIONS = []
"""Instances of `sitemap.SitemapSection` that will populate the Sitemap files."""

SITEMAP_ROOT_VIEW_ENABLED = False
"""Enable the `/sitemap.xml` endpoint serving the first sitemap index."""
