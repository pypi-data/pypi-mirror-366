# ingres/ingresdbi.py
# Copyright 2009 Ingres Corporation
#
# This module is part of SQLAlchemy and is released under
# the Apache-2.0 License: https://opensource.org/license/apache-2-0/
"""
Ingres DB connector for the ingresdbi module, which can be downloaded from
http://esd.ingres.com.
"""
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy_ingres.base import IngresDialect
from sqlalchemy_ingres.base import sqlalchemy_version_tuple


class Ingres_ingresdbi(IngresDialect):
    driver = "ingresdbi"
    supports_statement_cache = False  # NOTE `IngresDialect.supports_statement_cache` is not actually picked up by SA warning code, _generate_cache_attrs() checks dict of subclass, not the entire class

    def __init__(self, **kwargs):
        IngresDialect.__init__(self, **kwargs)

    if sqlalchemy_version_tuple >= (2, 0):

        @classmethod
        def import_dbapi(cls):
            return __import__("ingresdbi")

    else:

        @classmethod
        def dbapi(cls):
            return __import__("ingresdbi")

    def create_connect_args(self, url):
        opts = url.translate_connect_args(username="uid", password="pwd", host="vnode")
        opts.update(url.query)

        return ([], opts)


class IngresExecutionContext(DefaultExecutionContext):
    def __init__(self, **kwargs):
        DefaultExecutionContext.__init__(self, **kwargs)

    def create_cursor(self):
        return self._connection.connection.cursor()


dialect = Ingres_ingresdbi
