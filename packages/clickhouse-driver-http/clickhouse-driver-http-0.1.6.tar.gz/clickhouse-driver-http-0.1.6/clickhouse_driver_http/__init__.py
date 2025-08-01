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
        port: Union[int, str],
        user: str,
        password: str,
        database: str = "default",
        timeout: int = 300,
        verify_ssl: bool = False,
        use_compression: bool = False,
        max_retries: int = 3,
        retry_delay: int = 5,
        secure: bool = False
    ):
        self.base_url = f"https://{host}:{port}/"
        self.database = database
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.use_compression = use_compression
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.secure = secure
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
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        external_tables: Optional[List[Dict[str, Any]]] = None,
        with_column_types: bool = False
    ) -> Union[List[Tuple], Tuple[List[Tuple], List[Tuple[str, str]]]]:
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                clean_query = self._clean_query(query)
                url = f"{self.base_url}?query={quote(clean_query)}&default_format=JSON"
                
                if external_tables:
                    return self._execute_with_external_tables(clean_query, external_tables, with_column_types)
                
                response = self.session.post(
                    url,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
                
                return self._process_response(response, with_column_types)
                
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                last_exception = e
                time.sleep(self.retry_delay)
                continue
                
        raise ConnectionError(f"Request failed after {self.max_retries} attempts: {str(last_exception)}")

    def insert_dataframe(
        self,
        query: str,
        df: pd.DataFrame,
        settings: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None
    ) -> None:
        """
        Вставляет DataFrame в ClickHouse, сохраняя совместимость с существующим кодом
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be Pandas DataFrame")
        

        table_match = re.search(r'INSERT\s+INTO\s+([^\s(]+)', query, re.IGNORECASE)
        if not table_match:
            raise ValueError("Could not extract table name from INSERT query")
        
        table_name = table_match.group(1)
        
        def convert_datetime(value):
            if isinstance(value, (datetime, pd.Timestamp)):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            return value
        
        data = []
        for record in df.to_dict('records'):
            converted = {k: convert_datetime(v) for k, v in record.items()}
            data.append(json.dumps(converted, ensure_ascii=False))
        

        base_url = f"{self.base_url}?query={quote(f'INSERT INTO {table_name} FORMAT JSONEachRow')}"
        

        for chunk in self._chunk_data(data, chunk_size or len(data)):
            response = self.session.post(
                base_url,
                data='\n'.join(chunk).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            
            if not response.ok:
                raise ConnectionError(f"HTTP Error {response.status_code}: {response.text[:500]}")
    
    def _chunk_data(self, data: List[str], chunk_size: int) -> List[List[str]]:
        """Разбивает данные на чанки"""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def _execute_insert(self, query: str, data: str) -> None:
        response = self.session.post(
            f"{self.base_url}?query={quote(query)}",
            data=data.encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            verify=self.verify_ssl,
            timeout=self.timeout
        )
        
        if not response.ok:
            raise ConnectionError(f"HTTP Error {response.status_code}: {response.reason}")

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
            files[table['name']] = (f"{table['name']}.tsv", table_data, 'text/tab-separated-values')

        response = self.session.post(url, files=files, verify=self.verify_ssl, timeout=self.timeout)
        return self._process_response(response, with_column_types)

    def _convert_table_data(self, table: Dict[str, Any]) -> str:
        rows = []
        for row in table["data"]:
            if isinstance(row, dict):
                values = [self._format_value(row.get(col_name), col_type) for col_name, col_type in table["structure"]]
            elif isinstance(row, (list, tuple)):
                values = [self._format_value(value, table["structure"][i][1]) for i, value in enumerate(row)]
            elif len(table["structure"]) == 1:
                values = [self._format_value(row, table["structure"][0][1])]
            else:
                raise ValueError(f"Unsupported data format: {type(row)}")
            rows.append("\t".join(values))
        return "\n".join(rows)

    def _format_value(self, value: Any, col_type: str = "String") -> str:
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
        
        if isinstance(value, bool):
            return str(int(value))
        
        return str(value).replace('\t', '\\t').replace('\n', '\\n').replace('\\', '\\\\')

    def _process_response(
        self,
        response: requests.Response,
        with_column_types: bool
    ) -> Union[List[Tuple], Tuple[List[Tuple], List[Tuple[str, str]]]]:
        if not response.ok:
            raise ConnectionError(f"HTTP Error {response.status_code}: {response.reason}")

        content = response.content
        if self.use_compression and response.headers.get('Content-Encoding') == 'gzip':
            content = zlib.decompress(content, 16+zlib.MAX_WBITS)
        elif self.use_compression and response.headers.get('Content-Encoding') == 'deflate':
            content = zlib.decompress(content)
        
        if not content:
            return []
        
        json_data = json.loads(content.decode('utf-8'))
        
        if "data" not in json_data:
            raise ValueError(f"Unexpected response format: {json_data.keys()}")
        
        result = [tuple(row.values()) for row in json_data["data"]]
        
        if with_column_types:
            columns = [(col["name"], col["type"]) for col in json_data["meta"]] if "meta" in json_data else [(f"column_{i}", "String") for i in range(len(result[0]))]
            return result, columns
            
        return result

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
                
            safe_settings = "SETTINGS max_memory_usage=4000000000,max_bytes_before_external_group_by=2000000000,max_bytes_before_external_sort=2000000000,receive_timeout=3600,send_timeout=3600" if memory_safe else ""

            data, columns = self.execute(
                f"{self._clean_query(query)} {safe_settings}",
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
                return self.query_dataframe(query, params, external_tables, 50000, True)
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
        
        try:
            total_count = self.execute(f"SELECT count() FROM ({base_query})")[0][0]
        except:
            total_count = None
        
        while True:
            if is_select:
                batch_query = f"{base_query} LIMIT {batch_size} OFFSET {offset} SETTINGS max_memory_usage={4000000000 if memory_safe else 2000000000},max_threads=2,receive_timeout=3600,send_timeout=3600"
            else:
                batch_query = base_query
                
            try:
                batch = self.query_dataframe(batch_query, params, external_tables, None, memory_safe)
                
                if not is_select:
                    return batch
                    
                if batch.empty:
                    break
                    
                final_df = pd.concat([final_df, batch], ignore_index=True)
                offset += len(batch)
                    
            except Exception as e:
                if not is_select:
                    raise
                batch_size = max(int(batch_size * 0.5), 1000)
                time.sleep(5)
                
        return final_df

    def _clean_query(self, query: str) -> str:
        return query.split('SETTINGS')[0].rstrip('; \n\t')

    def check_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}?query=SELECT%201", timeout=5, verify=self.verify_ssl)
            return response.ok
        except Exception:
            return False