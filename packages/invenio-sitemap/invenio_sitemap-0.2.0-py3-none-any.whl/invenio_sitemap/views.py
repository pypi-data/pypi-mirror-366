# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# invenio-sitemap is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""

from flask import Blueprint, abort, current_app, make_response, render_template
from invenio_cache import current_cache

from .cache import SitemapCache, SitemapIndexCache

blueprint = Blueprint(
    "invenio_sitemap",
    __name__,
    template_folder="templates",
    static_folder="static",
)


def _get_cached_or_404(cache_cls, page):
    """Get cached entries or abort to 404 immediately."""
    cache = cache_cls(current_cache)
    data = cache.get(page)
    if data:
        return data
    else:
        abort(404)


def xml_response(body):
    """Wrap the body in an XML response."""
    response = make_response(body)
    response.headers["Content-Type"] = "application/xml"
    return response


@blueprint.route("/sitemap.xml", methods=["GET"])
def sitemap_root():
    """Get all sitemap root."""
    if not current_app.config["SITEMAP_ROOT_VIEW_ENABLED"]:
        abort(404)
    entries = _get_cached_or_404(SitemapIndexCache, 0)
    sitemap_index = render_template(
        "invenio_sitemap/sitemap_index.xml",
        entries=entries,
    )
    return xml_response(sitemap_index)


@blueprint.route("/sitemap_index_<int:page>.xml", methods=["GET"])
def sitemap_index(page):
    """Get the sitemap index."""
    entries = _get_cached_or_404(SitemapIndexCache, page)
    sitemap_index = render_template(
        "invenio_sitemap/sitemap_index.xml",
        entries=entries,
    )
    return xml_response(sitemap_index)


@blueprint.route("/sitemap_<int:page>.xml", methods=["GET"])
def sitemap(page):
    """Get the sitemap page."""
    entries = _get_cached_or_404(SitemapCache, page)
    sitemap = render_template(
        "invenio_sitemap/sitemap.xml",
        entries=entries,
    )
    return xml_response(sitemap)
