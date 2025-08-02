# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# invenio-sitemap is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""Cache wrapper."""


NAMESPACE = "invenio_sitemap"


class BaseSitemapCache:
    """Interface to the cache for Sitemap related content.

    The typical keys used in the interface of methods of this class are the
    integer indices of the batched content. As such `iterate_keys` returns these
    integer indices only. However, there is no enforcement that only such indices
    are used (those other kinds of keys will simply be ignored by
    ``delete_included_and_higher`` and ``iterate_keys``).

    This class namespaces keys under the hood with respect to interaction with the
    underlying cache.
    """

    def __init__(self, cache):
        """Constructor.

        :param cache: current_cache instance
        """
        self._cache = cache

    def get(self, key):
        """Retrieve cached value or None if key not found."""
        key_ = self._key(key)
        return self._cache.get(key_)

    def has(self, key):
        """If there is `key` in the cache."""
        key_ = self._key(key)
        return self._cache.has(key_)

    def set(self, key, value):
        """Set `value` at `key`."""
        key_ = self._key(key)
        self._cache.set(key_, value, timeout=-1)

    def delete(self, key):
        """Delete `key` entry."""
        key_ = self._key(key)
        self._cache.delete(key_)

    def delete_included_and_higher(self, key):
        """Clear entry at key and any subsequent ones."""
        # `key` must be an integer
        if not isinstance(key, int):
            return

        j = key
        while self.has(j):
            self.delete(j)
            j += 1

    def iterate_keys(self):
        """Yield integer index keys.

        These are exclusively keys of the form 0, 1, 2, ... Others, if any, are ignored.
        """
        j = 0
        # In practice, there typically won't be a large number of calls
        # since each page covers a lot of data.
        while self.has(j):
            yield j
            j += 1

    # plumbing
    def _key(self, key):
        """Build key for current_cache."""
        return f"{NAMESPACE}:{self.prefix}:{key}"


class SitemapCache(BaseSitemapCache):
    """Interface to the cache for Sitemap related content."""

    prefix = "sitemap"


class SitemapIndexCache(BaseSitemapCache):
    """Interface to the cache for Sitemap Index related content."""

    prefix = "sitemap_index"
