# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# invenio-sitemap is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tasks."""

from datetime import datetime, timezone

from celery import shared_task
from flask import current_app
from invenio_base import invenio_url_for
from invenio_cache import current_cache

from .cache import SitemapCache, SitemapIndexCache
from .utils import format_to_w3c, parse_from_w3c


@shared_task(ignore_results=True)
def update_sitemap_cache():
    """Update the cache with sitemap related content."""
    # Sitemaps
    max_count = current_app.config["SITEMAP_MAX_ENTRY_COUNT"]
    lastmods = []
    cache_sitemap = SitemapCache(current_cache)
    i = 0
    for batch in batched(_iterate_url_entries(), max_count):
        cache_sitemap.set(i, batch)
        lastmods.append(_get_latest_lastmod(batch))
        i += 1

    # Delete any cached entry that are now stale
    # Usually, this would delete at most 1 entry since there is rarely a mass
    # removal between runs. This is more efficient than previous indiscriminate clearing
    cache_sitemap.delete_included_and_higher(i)

    # Sitemap indices
    cache_sitemap_index = SitemapIndexCache(current_cache)
    j = 0
    for batch in batched(_iterate_sitemap_entries(lastmods), max_count):
        cache_sitemap_index.set(j, batch)
        j += 1

    # Delete any cached entry that are now stale
    # again, unlikely that mass deletions occur
    cache_sitemap_index.delete_included_and_higher(j)


def batched(iterable, n):
    """Batch data from iterable into tuples of length n (or smaller if less).

    This is more or less lifted from Python 3.12's batched equivalent.

    batched('ABCDEFG', 3) → ('A', 'B', 'C') ('D', 'E', 'F') ('G',)

    :param iterable: any iterable
    :param n: batch size, n >= 1
    :raises ValueError: n must at least one
    :yield: tuple[n items of iterable]
    """
    # TODO: When Python v3.12 is the norm just use its `batched`
    if n < 1:
        raise ValueError("n must be at least one")

    batch = []
    iterator = iter(iterable)

    for e in iterator:
        batch.append(e)
        if len(batch) == n:
            yield tuple(batch)
            batch = []

    if len(batch) > 0:
        yield tuple(batch)


def _iterate_url_entries():
    """Iterate over all SitemapSections and yield their sitemap entries."""
    sections = current_app.config.get("SITEMAP_SECTIONS", [])
    for section in sections:
        for entity in section.iter_entities():
            yield section.to_dict(entity)


def _get_latest_lastmod(entries):
    """Return most recent lastmod in w3c datetime format.

    :param entries: list[dict] where dict is an entry dict.
    """
    now_dt = datetime.now(timezone.utc)
    now_dt_as_w3c_str = format_to_w3c(now_dt)
    result = max(
        (e["lastmod"] if e.get("lastmod") else now_dt_as_w3c_str for e in entries),
        key=lambda e: parse_from_w3c(e),
        default=now_dt_as_w3c_str,  # for degenerate cases of entries == []
    )
    return result


def _iterate_sitemap_entries(lastmods):
    """Generate sitemap entries from lastmods.

    :param lastmods: str. W3C datetime format
    :yield: sitemap entry dict
    """
    for i, lastmod in enumerate(lastmods):
        yield {
            "loc": invenio_url_for("invenio_sitemap.sitemap", page=i),
            "lastmod": lastmod,
        }
