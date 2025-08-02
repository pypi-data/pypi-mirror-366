# coding: utf-8
from . import errors

def makedsn(
    server_name,
    db_name,
    host = None,
    port = None,
    protocol = 'onsoctcp',
    db_locale = 'zh_CN.57372',
    client_locale = 'zh_CN.57372',
    **params
):
    """
    Return a string for use as the dsn parameter for connect().
    """
    dsn = "gbase8s:GBASEDBTSERVER={};DATABASE={};".format(server_name, db_name)
    if 'sqlh_file' in params and params['sqlh_file'] is not None:
        dsn += "SQLH_FILE={};".format(params.pop('sqlh_file'))
    elif all((host, port, protocol)):
        dsn += "HOST={};SERVICE={};PROTOCOL={};".format(host, port, protocol)
    else:
        errors.raise_error(errors.ERR_INVALID_MAKEDSN_ARG, 
                          context_error_message="The arguments for host, port, and protocol are mandatory if you do not use the argument sqlh_file.",
                          name="host|port|protocol")
    if db_locale:
        dsn += "DB_LOCALE={};".format(db_locale)
    if client_locale:
        dsn += "CLIENT_LOCALE={};".format(client_locale)
    for k, v in params.items():
        k_u = k.upper()
        if k_u not in ('GBASEDBTSERVER', 'DATABASE', 'HOST', 
                    'PORT', 'PROTOCOL', 'DB_LOCALE', 'CLIENT_LOCALE', 'SQLMODE',
                    'GCI_FACTORY', 'DELIMIDENT'):
            if v is not None:
                dsn += "{}={};".format(k_u, v)
        else:
            errors.raise_error(errors.ERR_INVALID_MAKEDSN_ARG,
                              context_error_message="not supported parameter {}".format(k),
                              name="params")
    dsn += "SQLMODE=oracle;GCI_FACTORY=4;DELIMIDENT=1;"
    return dsn
