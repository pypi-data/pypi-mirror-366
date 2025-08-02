from mtbs.mtbs import Mtbs
def main():

    _mtbs = Mtbs(env="prd")
    _db_list = _mtbs.databases_list()
    # print(_mtbs.send_sql(query="SELECT * FROM uploaded_file limit 1", database=_db_list['Uploads API'], raw=False, cache_enabled=True))
    print(_mtbs.send_sql(query="SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';", database=_db_list['Uploads API'], raw=False, cache_enabled=True))

    
    #_mtbs.send_sql(query="SELECT * FROM my_table", database="my_database", raw=True, cache_enabled=True)