# ingres/zxjdbc.py
# Copyright 2009 Ingres Corporation
#
# This module is part of SQLAlchemy and is released under
# the Apache-2.0 License: https://opensource.org/license/apache-2-0/
"""
Support for the Ingres database using the zxjdbc connector for jPython.

Requires the Ingres JDBC driver, which can be downloaded from
http://esd.ingres.com
"""
from sqlalchemy.connectors.zxJDBC import ZxJDBCConnector
from sqlalchemy_ingres.base import IngresDialect


class Ingres_zxjdbc(ZxJDBCConnector, IngresDialect):
    jdbc_db_name = "ingres"
    jdbc_driver_name = "com.ingres.jdbc.IngresDriver"
    supports_statement_cache = False  # NOTE `IngresDialect.supports_statement_cache` is not actually picked up by SA warning code, _generate_cache_attrs() checks dict of subclass, not the entire class

    def _get_server_version_info(self, connection):
        return connection.connection.dbversion


dialect = Ingres_zxjdbc
