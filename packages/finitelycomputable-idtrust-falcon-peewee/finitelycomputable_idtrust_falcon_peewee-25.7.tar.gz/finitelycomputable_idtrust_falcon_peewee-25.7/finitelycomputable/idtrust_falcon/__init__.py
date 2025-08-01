from finitelycomputable.idtrust_falcon.peewee import *

def add_routes(application, base_path):
    from finitelycomputable import idtrust_app_falcon
    idtrust_app_falcon.add_routes(application, base_path)
