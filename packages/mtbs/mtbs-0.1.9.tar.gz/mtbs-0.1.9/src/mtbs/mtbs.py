
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from alive_progress import alive_bar
import diskcache
import requests
from typing import Dict, List

from mtbs import copy_firefox_cookies, headers, headers_data, mtbs_base_url, mtbs_db_list_url, payload_template, raw_to_object

def read_metabase_config_from_browser(env: str = "prd") -> tuple:
    _mtbs_db_list_url = None
    _mtbs_base_url = None
    _headers = headers
    _headers_data = headers_data
    
    db_path = copy_firefox_cookies()
    if not db_path:
        print("No Firefox profile found or cookies.sqlite not available.")
        return None, None, None, None
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT host, name, value FROM moz_cookies where host like '%metabase%{env}%';")
        cookies = cursor.fetchall()
        if not cookies:
            print(f"No cookies found for *metabase-{env}*.")
            return
        _mtbs_db_list_url = mtbs_db_list_url.format(base_url=f"https://{cookies[0][0]}")
        _mtbs_base_url = mtbs_base_url.format(base_url=f"https://{cookies[0][0]}")
        _headers['Origin'] = _headers['Origin'].format(base_url=f"https://{cookies[0][0]}")
        _headers['Referer'] =  _headers['Referer'].format(base_url=f"https://{cookies[0][0]}/question")
        _headers['Cookie'] = ";".join([f'{name}={value}' for _, name, value in cookies])
        _headers_data['Cookie'] = _headers['Cookie']
        _headers_data['Origin'] = _headers['Origin']
        _headers_data['Referer'] = _headers['Referer']
        # if (env == "preprod"):
        #     cursor.execute(f"SELECT host, name, value FROM moz_cookies where host like '.{env}.%';")
        #     cookies = cursor.fetchall()
        #     if not cookies:
        #         print(f"No cookies found for .{env}*.")
        #         return
        #     _headers['Cookie'] =  _headers['Cookie'] + ";" + ";".join([f'{name}={value}' for _, name, value in cookies])
        #     _headers_data['Cookie'] = _headers['Cookie']
        # Pour les environnements DEV et PREPROD, ajouter les cookies OAuth2
        if env in ["dev", "preprod"]:
            cursor.execute(f"SELECT host, name, value FROM moz_cookies WHERE host LIKE '.{env}.bel.cloud.bpifrance.fr';")
            oauth_cookies = cursor.fetchall()
            if oauth_cookies:
                oauth_cookie_str = ";".join([f'{name}={value}' for _, name, value in oauth_cookies])
                _headers['Cookie'] = _headers['Cookie'] + ";" + oauth_cookie_str
                _headers_data['Cookie'] = _headers['Cookie']
            else:
                print(f"Warning: No OAuth2 cookies found for .{env.value}.bel.cloud.bpifrance.fr - authentication may fail")
    return _mtbs_base_url, _mtbs_db_list_url, _headers, _headers_data

def read_cookies(cookie_file='cookies.json'):
    with open(cookie_file, 'r') as file:
        data = json.load(file)
        
    _headers = headers
    _headers_data = headers_data
    
    _mtbs_db_list_url = mtbs_db_list_url.format(base_url=f"{data[0]['Host raw']}")
    _mtbs_base_url = mtbs_base_url.format(base_url=f"{data[0]['Host raw']}")
    _headers['Origin'] = headers['Origin'].format(base_url=data[0]['Host raw'])
    _headers['Referer'] = headers['Referer'].format(base_url=f"{data[0]['Host raw']}question")
    _headers['Cookie'] = ";".join([f'{item["Name raw"]}={item["Content raw"]}' for item in data])
    _headers_data['Cookie'] = _headers['Cookie']
    _headers_data['Origin'] = _headers['Origin']
    _headers_data['Referer'] = _headers['Referer']
    return _mtbs_base_url, _mtbs_db_list_url, _headers, _headers_data

class Mtbs:
    def __init__(self, env: str = "prd", cookie_file_path: str = None):
        if env is None or ["dev", "preprod", "prd"].count(env) == 0:
            raise ValueError("env must be one of 'dev', 'preprod', 'prd'")
        self.env = env
        
        if cookie_file_path is None:
            mtbs_base_url, mtbs_db_list_url, _headers, _headers_data = read_metabase_config_from_browser(env)
            self.mtbs_base_url = mtbs_base_url
            self.mtbs_db_list_url = mtbs_db_list_url
            self.headers = _headers
            self.headers_data = _headers_data
        else:
            cookie_file_path = Path(cookie_file_path)
            print(f"Using cookie file: {cookie_file_path}")
            if not cookie_file_path.exists():
                raise FileNotFoundError(f"Cookie file {cookie_file_path} does not exist.")
            mtbs_base_url, mtbs_db_list_url, _headers, _headers_data = read_cookies(cookie_file_path)
            self.mtbs_base_url = mtbs_base_url
            self.mtbs_db_list_url = mtbs_db_list_url
            self.headers = _headers
            self.headers_data = _headers_data
        
        if not self.mtbs_base_url or not self.mtbs_db_list_url or not self.headers or not self.headers_data:
            raise ValueError("Failed to read Metabase configuration. Please check your browser cookies or cookie file.")
        
        
    def send_sql(self, query=None, database=None, raw=False, cache_enabled=False) -> str:
        #logger.debug(f"Sending SQL query to {url} for database {database} with query: \n {query}")
        empty = {"data": {"cols": [], "rows": []}} if raw else []
        if not self.mtbs_base_url or not query or not database:
            #logger.error("Url, Query and database must be provided.")
            return empty
        
        try:
            # Cache mechanism using diskcache
            cache_dir = Path(tempfile.gettempdir()) / "mtbs_query_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache = diskcache.Cache(str(cache_dir))
            cache_key = hashlib.sha256(f"{self.mtbs_base_url}|{database}|{query}".encode()).hexdigest()

            data = cache.get(cache_key) if cache_enabled else None
            if data is not None:
                pass
                #logger.debug(f"Cache hit for query: {query}")
            else:
                response = requests.post(self.mtbs_base_url, headers=self.headers, json=payload_template(query, database), timeout=240)
                response.raise_for_status()
                data = response.json()
                cache.set(cache_key, data)
            # response.raise_for_status()
            # data = response.json()
        except requests.exceptions.Timeout:
            #logger.error("The request timed out.")
            return empty
        except Exception as e:
            # logger.error(f"Error while retrieving or decoding JSON: {e}")
            # logger.error("Raw response content: %s", getattr(response, 'text', '')[:500])
            return empty
        if raw:
            return data
            # return json.dumps(data, ensure_ascii=False)
        
        results = raw_to_object(data)
        return json.dumps(results, ensure_ascii=False)
    
    def recursive_sql(self, query, database, limit=2000, offset=0, write_header=True, output_file=None, results: List[Dict] = None, cache_enabled: bool = False) -> list:
        current_offset = offset
        first_batch = True
        returned_results = results if results is not None else []
        with alive_bar(title="Loading data", length=100, enrich_print=False) as bar:
            while True:
                query_limit = query + f" LIMIT {limit} OFFSET {current_offset};"
                result_raw = self.send_sql(query_limit, database, raw=True, cache_enabled=cache_enabled)
                if not result_raw or 'data' not in result_raw or 'rows' not in result_raw['data']:
                    # logger.error(f"Stop: no data for {query_limit}")
                    break
                headers = [col['name'] for col in result_raw['data']['cols']]
                result = result_raw['data']['rows']

                returned_results.extend([dict(zip(headers, row)) for row in result_raw['data']['rows']])
                # if not result:
                #     # logger.error(f"Stop: no rows for {query_limit}")
                #     break
                # # logger.info(f"Result: {result}")

                if output_file is not None:
                    with open(output_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if (write_header or first_batch) and len(headers) > 0:
                            writer.writerow([str(item) if item is not None else "None" for item in headers])
                            first_batch = False
                        for i in result:
                            writer.writerow([str(item) if item is not None else "None" for item in i])

                bar()
                bar.text = f"Offset: {current_offset}, Rows: {len(result)}, Total: {len(returned_results)}"
                if len(result) < limit:
                    break
                current_offset += limit
            bar.title = f"{len(returned_results)} rows loaded"
        return json.dumps(returned_results, ensure_ascii=False)

    def databases_list(self) -> List[Dict]:
        cache_dir = Path(tempfile.gettempdir()) / "mtbs_databases_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache = diskcache.Cache(str(cache_dir))
        cache_key = hashlib.sha256(f"{mtbs_base_url}".encode()).hexdigest()

        if cache_key in cache:
            return cache[cache_key]

        response = requests.get(self.mtbs_db_list_url, headers=self.headers, timeout=240)
        response.raise_for_status()

        data = {db['name']: db['id'] for db in response.json()['data']}
        cache[cache_key] = data

        # response = requests.get(mtbs_db_list_url, headers=headers, timeout=240)
        # response.raise_for_status()

        # data = {db['name']: db['id'] for db in response.json()['data']}
        return data
        #return json.dumps(data, ensure_ascii=False)