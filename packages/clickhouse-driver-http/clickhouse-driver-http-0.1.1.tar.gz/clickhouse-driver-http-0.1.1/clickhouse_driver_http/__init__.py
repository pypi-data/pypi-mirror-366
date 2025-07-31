import requests
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Union, Optional, Tuple
from urllib.parse import quote
import json
import warnings
import zlib
from io import BytesIO
import time
import re

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Client:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str = "default",
        timeout: int = 300,
        verify_ssl: bool = False,
        use_compression: bool = False,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        self.base_url = f"https://{host}:{port}/"
        self.database = database
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.use_compression = use_compression
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        headers = {
            "X-ClickHouse-User": user,
            "X-ClickHouse-Key": password or "",
            "X-ClickHouse-Database": database,
            "Accept": "application/json"
        }
        
        if self.use_compression:
            headers["Accept-Encoding"] = "gzip, deflate"
            
        self.session.headers.update(headers)

    def _is_select_query(self, query: str) -> bool:
        clean_query = re.sub(r'--.*?$|/\*.*?\*/', '', query, flags=re.MULTILINE | re.DOTALL)
        clean_query = ' '.join(clean_query.split()).upper()
        return (
            clean_query.startswith(('SELECT ', 'WITH ')) or 
            ' FROM ' in clean_query or
            ('SELECT' in clean_query and not clean_query.startswith(('INSERT', 'ALTER', 'DESCRIBE', 'SHOW', 'EXISTS')))
        )

    def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        external_tables: Optional[List[Dict[str, Any]]] = None,
        with_column_types: bool = False
    ) -> Union[List[Tuple], Tuple[List[Tuple], List[Tuple[str, str]]]]:
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                clean_query = self._clean_query(query)
                url = f"{self.base_url}?query={quote(clean_query)}&default_format=JSON"
                
                if external_tables:
                    if not isinstance(external_tables, list):
                        raise TypeError("external_tables должен быть списком словарей")
                    for table in external_tables:
                        if not isinstance(table, dict):
                            raise TypeError("Каждый элемент external_tables должен быть словарём")
                        if not all(k in table for k in ('name', 'structure', 'data')):
                            raise ValueError("Таблица должна содержать ключи: name, structure, data")
                    return self._execute_with_external_tables(clean_query, external_tables, with_column_types)
                
                response = self.session.post(
                    url,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
                
                return self._process_response(response, with_column_types)
                
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                last_exception = e
                print(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                continue
                
        raise ConnectionError(f"Request failed after {self.max_retries} attempts: {str(last_exception)}")

    def _execute_with_external_tables(
        self,
        query: str,
        external_tables: List[Dict[str, Any]],
        with_column_types: bool
    ) -> Union[List[Tuple], Tuple[List[Tuple], List[Tuple[str, str]]]]:
        url = f"{self.base_url}?query={quote(query)}&default_format=JSON"
        files = {}
        
        for table in external_tables:
            structure = ",".join([f"{name} {typ}" for name, typ in table["structure"]])
            url += f"&{table['name']}_structure={quote(structure)}"
            
            table_data = self._convert_table_data(table)
            files[table['name']] = (
                f"{table['name']}.tsv",
                table_data,
                'text/tab-separated-values'
            )

        response = self.session.post(
            url,
            files=files,
            verify=self.verify_ssl,
            timeout=self.timeout
        )
        
        return self._process_response(response, with_column_types)

    def _convert_table_data(self, table: Dict[str, Any]]) -> str:
        rows = []
        for row in table["data"]:
            if isinstance(row, dict):
                values = []
                for col_name, col_type in table["structure"]:
                    value = row.get(col_name)
                    values.append(self._format_value(value, col_type))
                rows.append("\t".join(values))
            elif isinstance(row, (list, tuple)):
                if len(row) != len(table["structure"]):
                    raise ValueError("Количество элементов в строке не соответствует структуре таблицы")
                values = []
                for i, value in enumerate(row):
                    col_type = table["structure"][i][1]
                    values.append(self._format_value(value, col_type))
                rows.append("\t".join(values))
            elif len(table["structure"]) == 1:
                values = [self._format_value(row, table["structure"][0][1])]
                rows.append("\t".join(values))
            else:
                raise ValueError(f"Неподдерживаемый формат данных: {type(row)}")
        return "\n".join(rows)

    def _format_value(self, value: Any, col_type: str) -> str:
        if value is None:
            return "\\N"
        
        if col_type.startswith(('Int', 'UInt', 'Float')):
            try:
                value = int(value) if 'Int' in col_type else float(value)
            except (ValueError, TypeError):
                return "\\N"
        
        if isinstance(value, (datetime, date)):
            if "DateTime" in col_type:
                return value.strftime('%Y-%m-%d %H:%M:%S')
            elif "Date" in col_type:
                return value.strftime('%Y-%m-%d')
        
        return str(value).replace('\t', '\\t').replace('\n', '\\n').replace('\\', '\\\\')

    def _process_response(
        self,
        response: requests.Response,
        with_column_types: bool
    ) -> Union[List[Tuple], Tuple[List[Tuple], List[Tuple[str, str]]]]:
        if not response.ok:
            raise ConnectionError(
                f"HTTP Error {response.status_code}: {response.reason}\n"
                f"Response: {response.text[:500]}"
            )
        
        try:
            content = response.content
            if self.use_compression and response.headers.get('Content-Encoding') == 'gzip':
                content = zlib.decompress(content, 16+zlib.MAX_WBITS)
            elif self.use_compression and response.headers.get('Content-Encoding') == 'deflate':
                content = zlib.decompress(content)
            
            json_data = json.loads(content.decode('utf-8'))
            
            if "data" not in json_data:
                raise ValueError(f"Unexpected response format: {json_data.keys()}")
            
            result = [tuple(row.values()) for row in json_data["data"]]
            
            if with_column_types:
                if "meta" in json_data:
                    columns = [(col["name"], col["type"]) for col in json_data["meta"]]
                else:
                    columns = [(f"column_{i}", "String") for i in range(len(result[0]))]
                return result, columns
                
            return result
            
        except Exception as e:
            raise ConnectionError(f"Failed to process response: {str(e)}") from e

    def query_dataframe(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        external_tables: Optional[List[Dict[str, Any]]] = None,
        batch_size: Optional[int] = None,
        memory_safe: bool = True
    ) -> pd.DataFrame:
        try:
            if batch_size or (self._is_select_query(query) and "LIMIT" not in query.upper()):
                return self._batched_query(query, params, external_tables, batch_size or 50000, memory_safe)
                
            safe_settings = """
            SETTINGS
                max_memory_usage = 4000000000,
                max_bytes_before_external_group_by = 2000000000,
                max_bytes_before_external_sort = 2000000000,
                receive_timeout=3600,
                send_timeout=3600
            """ if memory_safe else ""

            full_query = self._clean_query(query) + safe_settings

            data, columns = self.execute(
                full_query,
                params=params,
                external_tables=external_tables,
                with_column_types=True
            )
            
            df = pd.DataFrame(data, columns=[col[0] for col in columns])
            
            for col_name, col_type in columns:
                if 'DateTime' in col_type:
                    df[col_name] = pd.to_datetime(df[col_name])
                elif 'Date' in col_type:
                    df[col_name] = pd.to_datetime(df[col_name]).dt.date
            
            return df
            
        except Exception as e:
            if "MEMORY_LIMIT_EXCEEDED" in str(e):
                return self.query_dataframe(
                    query,
                    params=params,
                    external_tables=external_tables,
                    batch_size=50000,
                    memory_safe=True
                )
            raise ConnectionError(f"Failed to create DataFrame: {str(e)}") from e

    def _batched_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]],
        external_tables: Optional[List[Dict[str, Any]]],
        batch_size: int,
        memory_safe: bool = True
    ) -> pd.DataFrame:
        base_query = self._clean_query(query)
        is_select = self._is_select_query(base_query)
        final_df = pd.DataFrame()
        offset = 0
        
        count_query = f"SELECT count() FROM ({base_query})"
        try:
            total_count = self.execute(count_query)[0][0]
        except:
            total_count = None
        
        while True:
            if is_select:
                batch_query = f"""
                {base_query}
                LIMIT {batch_size}
                OFFSET {offset}
                SETTINGS
                    max_memory_usage = {4000000000 if memory_safe else 2000000000},
                    max_threads = 2,
                    receive_timeout=3600,
                    send_timeout=3600
                """
            else:
                batch_query = base_query
                
            try:
                start_time = time.time()
                batch = self.query_dataframe(
                    batch_query,
                    params=params,
                    external_tables=external_tables,
                    batch_size=None,
                    memory_safe=memory_safe
                )
                
                if not is_select:
                    return batch
                    
                if batch.empty:
                    break
                    
                final_df = pd.concat([final_df, batch], ignore_index=True)
                offset += len(batch)
                processing_time = time.time() - start_time
                
                progress = f"{offset}/{total_count}" if total_count else str(offset)
                print(f"Loaded {len(batch)} rows (total: {progress}), took {processing_time:.2f}s")
                
                if processing_time > 15:
                    batch_size = max(int(batch_size * 0.7), 1000)
                    print(f"Reducing batch size to {batch_size}")
                elif processing_time < 5 and batch_size < 100000:
                    batch_size = min(int(batch_size * 1.3), 100000)
                    
            except Exception as e:
                if not is_select:
                    raise
                    
                print(f"Error loading batch: {str(e)}")
                batch_size = max(int(batch_size * 0.5), 1000)
                print(f"Retrying with reduced batch size: {batch_size}")
                time.sleep(5)
                
        return final_df

    def _clean_query(self, query: str) -> str:
        return query.split('SETTINGS')[0].rstrip('; \n\t')

    def check_connection(self) -> bool:
        try:
            response = self.session.get(
                f"{self.base_url}?query=SELECT%201",
                timeout=5,
                verify=self.verify_ssl
            )
            return response.ok
        except Exception:
            return False