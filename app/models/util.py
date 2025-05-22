from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

from app.extensions import db


class utcnow(expression.FunctionElement):
    type = db.DateTime()
    inherit_cache = True

@compiles(utcnow, 'mariadb')
def pg_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP"
