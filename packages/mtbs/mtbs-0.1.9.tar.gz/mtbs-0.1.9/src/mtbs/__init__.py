import csv
import json
import logging
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Dict, List
from alive_progress import alive_bar
import questionary
import requests
import hashlib
import diskcache
from opentelemetry import trace
from opentelemetry.trace import SpanKind
logger = logging.getLogger("mtbs")
match os.getenv('MTBS_LOG_LEVEL'):
    case 'CRITICAL':
        _LOG_LEVEL = logging.CRITICAL
    case 'FATAL':
        _LOG_LEVEL = logging.FATAL
    case 'INFO':
        _LOG_LEVEL = logging.INFO
    case 'DEBUG':
        _LOG_LEVEL = logging.DEBUG
    case 'WARNING':
        _LOG_LEVEL = logging.WARNING
    case 'ERROR':
        _LOG_LEVEL = logging.ERROR
    case _:
        _LOG_LEVEL = logging.ERROR
        
logging.basicConfig(
    level=_LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(),  # console display
        # logging.FileHandler("app.log")  # Save logs in a file
    ]
)
mtbs_db_list_url = "{base_url}/api/database"
mtbs_base_url = "{base_url}/api/dataset"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.'", 
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "{base_url}",
    "Connection": "keep-alive",
    "Referer": "{base_url}",
    "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin", "Priority": "u=0", "TE": "trailers", 
}
headers_data = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "{base_url}",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "{base_url}",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0"
}
def hello() -> str:
    return "Hello from mtbs!!"

def get_metabase_base_url() -> str:
    return mtbs_base_url

def read_metabase_config_from_browser(env: str = "prd") -> None:
    global mtbs_db_list_url,mtbs_base_url, headers, headers_data
    db_path = copy_firefox_cookies()
    if not db_path:
        print("No Firefox profile found or cookies.sqlite not available.")
        return
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT host, name, value FROM moz_cookies where host like '%metabase%{env}%';")
        cookies = cursor.fetchall()
        if not cookies:
            print(f"No cookies found for *metabase-{env}*.")
            return
        mtbs_db_list_url = mtbs_db_list_url.format(base_url=f"https://{cookies[0][0]}")
        mtbs_base_url = mtbs_base_url.format(base_url=f"https://{cookies[0][0]}")
        headers['Origin'] = headers['Origin'].format(base_url=f"https://{cookies[0][0]}")
        headers['Referer'] =  headers['Referer'].format(base_url=f"https://{cookies[0][0]}/question")
        headers['Cookie'] = ";".join([f'{name}={value}' for _, name, value in cookies])
        headers_data['Cookie'] = headers['Cookie']
        headers_data['Origin'] = headers['Origin']
        headers_data['Referer'] = headers['Referer']
        if (env == "preprod"):
            cursor.execute(f"SELECT host, name, value FROM moz_cookies where host like '.{env}.%';")
            cookies = cursor.fetchall()
            if not cookies:
                print(f"No cookies found for .{env}*.")
                return
            headers['Cookie'] =  headers['Cookie'] + ";" + ";".join([f'{name}={value}' for _, name, value in cookies])
            headers_data['Cookie'] = headers['Cookie']

def copy_firefox_cookies() -> Path:
    profile_path = next(Path.home().glob(".mozilla/firefox/*.default-release"), None)
    if not profile_path:
        return None
    source_file = profile_path / "cookies.sqlite"
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / "cookies_firefox.sqlite"
    shutil.copy2(source_file, temp_file)
    return temp_file

def payload_template(query, database) -> dict:
    return {
        "type":"native",
        "native":{
            "query":f"{query}",
            "template-tags":{}
        },
        "database":database,
        "parameters":[]
    }

def read_cookies(cookie_file='cookies.json'):
    global mtbs_base_url, headers, headers_data
    with open(cookie_file, 'r') as file:
        data = json.load(file)
    
    mtbs_db_list_url = mtbs_db_list_url.format(base_url=f"{data[0]['Host raw']}")
    mtbs_base_url = mtbs_base_url.format(base_url=f"{data[0]['Host raw']}")
    headers['Origin'] = headers['Origin'].format(base_url=data[0]['Host raw'])
    headers['Referer'] = headers['Referer'].format(base_url=f"{data[0]['Host raw']}question")
    headers['Cookie'] = ";".join([f'{item["Name raw"]}={item["Content raw"]}' for item in data])
    headers_data['Cookie'] = headers['Cookie']
    headers_data['Origin'] = headers['Origin']
    headers_data['Referer'] = headers['Referer']


def send_sql(url, query=None, database=None, raw=False, cache_enabled=False) -> str:
    logger.debug(f"Sending SQL query to {url} for database {database} with query: \n {query}")
    empty = {"data": {"cols": [], "rows": []}} if raw else []
    if not url or not query or not database:
        logger.error("Url, Query and database must be provided.")
        return empty
    
    try:
        # Cache mechanism using diskcache
        cache_dir = Path(tempfile.gettempdir()) / "mtbs_query_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache = diskcache.Cache(str(cache_dir))
        cache_key = hashlib.sha256(f"{url}|{database}|{query}".encode()).hexdigest()

    #tracer = trace.get_tracer(__name__)
    #with tracer.start_as_current_span("send_sql", kind=SpanKind.CLIENT) as span:
    #    span.set_attribute("url", url)
    #    span.set_attribute("database", database)
    #    span.set_attribute("query", query)
    #    span.set_attribute("cache_enabled", cache_enabled)
            
        data = cache.get(cache_key) if cache_enabled else None
        if data is not None:
    #        span.set_attribute("cache_hit", True)
            logger.debug(f"Cache hit for query: {query}")
            # class DummyResponse:
            #     def raise_for_status(self): pass
            # response = DummyResponse()
        else:
    #        span.set_attribute("peer.service", "metabase")
            response = requests.post(url, headers=headers, json=payload_template(query, database), timeout=240)
            response.raise_for_status()
    #        span.set_attribute("http.status_code", response.status_code)
            data = response.json()
            cache.set(cache_key, data)
        # response.raise_for_status()
        # data = response.json()
    except requests.exceptions.Timeout:
        logger.error("The request timed out.")
        return empty
    except Exception as e:
        logger.error(f"Error while retrieving or decoding JSON: {e}")
        logger.error("Raw response content: %s", getattr(response, 'text', '')[:500])
        return empty
    if raw:
        return data
        # return json.dumps(data, ensure_ascii=False)
    
    results = raw_to_object(data)
    return json.dumps(results, ensure_ascii=False)

def raw_to_object(data):
    cols = [col['name'] for col in data['data']['cols']]
    rows = data['data']['rows']
    results = [dict(zip(cols, row)) for row in rows]
    return results

def recursive_sql(url, query, database, limit=2000, offset=0, write_header=True, output_file=None, results: List[Dict] = None, cache_enabled: bool = False) -> list:
    current_offset = offset
    first_batch = True
    returned_results = results if results is not None else []
    with alive_bar(title="Loading data", length=100, enrich_print=False) as bar:
        while True:
            query_limit = query + f" LIMIT {limit} OFFSET {current_offset};"
            result_raw = send_sql(url, query_limit, database, raw=True, cache_enabled=cache_enabled)
            if not result_raw or 'data' not in result_raw or 'rows' not in result_raw['data']:
                logger.error(f"Stop: no data for {query_limit}")
                break
            headers = [col['name'] for col in result_raw['data']['cols']]
            result = result_raw['data']['rows']

            returned_results.extend([dict(zip(headers, row)) for row in result_raw['data']['rows']])
            if not result:
                logger.error(f"Stop: no rows for {query_limit}")
                break
            logger.info(f"Result: {result}")

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


def load_json(json_file_path: str) -> List[Dict]:
    """Charge un fichier JSON avec validation."""
    try:
        absolute_path = Path(json_file_path)
        if not absolute_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {json_file_path}")
        
        with open(absolute_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Validation minimale du format
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("Format JSON invalide. Attend une liste de dictionnaires.")

            return data

    except json.JSONDecodeError:
        raise ValueError("Fichier JSON malformé")
    except Exception as e:
        raise RuntimeError(f"Erreur de chargement : {str(e)}")
    
def get_databases():
    try:
        _data = load_json("database_full_list.json")
        #data = sorted(_data, key=lambda x: x["name"].lower())
        _data.sort(key=lambda x: x["name"].lower())
        data = {item["name"]: item["id"] for item in _data}
        return data
    except Exception as e:
        print(f"❌ Critical error : {e}")
        return None
    
def databases_list() -> List[Dict]:
    cache_dir = Path(tempfile.gettempdir()) / "mtbs_databases_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = diskcache.Cache(str(cache_dir))
    cache_key = hashlib.sha256(f"{mtbs_base_url}".encode()).hexdigest()

    if cache_key in cache:
        return cache[cache_key]

    response = requests.get(mtbs_db_list_url, headers=headers, timeout=240)
    response.raise_for_status()

    data = {db['name']: db['id'] for db in response.json()['data']}
    cache[cache_key] = data

    # response = requests.get(mtbs_db_list_url, headers=headers, timeout=240)
    # response.raise_for_status()

    # data = {db['name']: db['id'] for db in response.json()['data']}
    return data
    #return json.dumps(data, ensure_ascii=False)

def menu_interactif(data: List[Dict]):
    """Affiche un menu Questionary à partir des données."""
    try:
        selected = questionary.select(
            "Select a database :",
            choices=[
                questionary.Choice(
                    title=f"{item.get('name', 'no name')} (ID: {item.get('id', '?')})",
                    value=item
                )
                for item in sorted(data, key=lambda x: x.get('id', 0))
            ],
            qmark="❓ ",  # Symbole personnalisé
            instruction="(Utilisez les flèches)",
            style=questionary.Style([
                ('selected', 'fg:#ffffff bg:#ff0000 bold'),
                ('answer', 'fg:#00ff00 bold')
            ])
        ).ask()
        
        return selected
        
    except Exception as e:
        print(f"Erreur dans le menu : {e}")
        return None