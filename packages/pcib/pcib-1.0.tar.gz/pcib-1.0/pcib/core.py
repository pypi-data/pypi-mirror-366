import sys
import json
import argparse
import asyncio
import aiohttp
from typing import Optional, Dict, Union, List

class PCIBError(Exception):
    """Base exception for pcib library"""
    pass

class PCIBTimeoutError(PCIBError):
    """Raised when request times out"""
    pass

class PCIBConnectionError(PCIBError):
    """Raised when connection fails"""
    pass

class PCIB:
    """
    Асинхронная Python cURL-like библиотека (pcib) на aiohttp
    Версия 1.1 by flamecode
    """
    
    def __init__(self):
        self.method = 'GET'
        self.headers: Dict[str, str] = {}
        self.data: Optional[Union[Dict, str, bytes]] = None
        self.json_data: Optional[Union[Dict, List]] = None
        self.params: Optional[Dict[str, str]] = None
        self.timeout = 30
        self.verify_ssl = True
        self.allow_redirects = True
        self.response: Optional[aiohttp.ClientResponse] = None
        self.response_data: Optional[dict] = None
    
    def set_method(self, method: str) -> None:
        """Установка HTTP метода"""
        self.method = method.upper()
    
    def set_header(self, key: str, value: str) -> None:
        """Установка заголовка"""
        self.headers[key] = value
    
    def set_data(self, data: Union[Dict, str, bytes]) -> None:
        """Установка данных для отправки (form-data)"""
        self.data = data
    
    def set_json(self, json_data: Union[Dict, List]) -> None:
        """Установка JSON данных для отправки"""
        self.json_data = json_data
    
    def set_params(self, params: Dict[str, str]) -> None:
        """Установка query параметров"""
        self.params = params
    
    def set_timeout(self, timeout: int) -> None:
        """Установка таймаута"""
        self.timeout = timeout
    
    def set_verify_ssl(self, verify: bool) -> None:
        """Включение/выключение проверки SSL"""
        self.verify_ssl = verify
    
    def set_allow_redirects(self, allow: bool) -> None:
        """Разрешение/запрет редиректов"""
        self.allow_redirects = allow
    
    async def _process_response(self, response: aiohttp.ClientResponse) -> dict:
        """Обрабатывает ответ и возвращает словарь с данными"""
        result = {
            'status': response.status,
            'headers': dict(response.headers),
            'content_type': response.content_type
        }
        
        try:
            if response.content_type == 'application/json':
                result['data'] = await response.json()
            else:
                result['data'] = await response.text()
        except json.JSONDecodeError:
            raise PCIBError("Failed to decode JSON response")
        
        return result
    
    async def request(self, url: str) -> bool:
        """Выполнение асинхронного HTTP запроса"""
        if not url.startswith(('http://', 'https://')):
            raise PCIBError(f"Invalid URL: {url}")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            ) as session:
                async with session.request(
                    method=self.method,
                    url=url,
                    data=self.data,
                    json=self.json_data,
                    params=self.params,
                    allow_redirects=self.allow_redirects
                ) as response:
                    await response.read()
                    self.response = response
                    self.response_data = await self._process_response(response)
                    return True
                    
        except asyncio.TimeoutError:
            raise PCIBTimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise PCIBConnectionError(f"Connection error: {str(e)}")
        except Exception as e:
            raise PCIBError(f"Unexpected error: {str(e)}")
    
    def get_response(self) -> Optional[dict]:
        """Получение данных ответа"""
        return self.response_data
    
    def print_response(self, show_headers: bool = False) -> None:
        """Вывод ответа на экран"""
        if not self.response_data:
            print("No response available", file=sys.stderr)
            return
        
        if show_headers:
            print(f"HTTP/1.1 {self.response.status} {self.response.reason}")
            for key, value in self.response.headers.items():
                print(f"{key}: {value}")
            print()
        
        data = self.response_data.get('data', '')
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(data)

class CLI:
    """
    Интерфейс командной строки для pcib
    """
    
    @staticmethod
    def parse_args(args=None):
        """Разбор аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='pcib - Async Python cURL-like tool. Version 1.1 by flamecode',
            epilog='Примеры:\n'
                   '  pcib http://example.com\n'
                   '  pcib -X POST -d \'{"key":"value"}\' http://example.com/api\n'
                   '  pcib -H "Content-Type: application/json" http://example.com',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        parser.add_argument('url', help='URL для запроса')
        parser.add_argument('-X', '--request', dest='method', default='GET',
                          help='Указание HTTP метода (GET, POST, PUT, DELETE и т.д.)')
        parser.add_argument('-H', '--header', action='append', dest='headers',
                          help='Добавление HTTP заголовка (можно использовать несколько раз)')
        parser.add_argument('-d', '--data', help='Данные для отправки в теле запроса')
        parser.add_argument('-j', '--json', help='JSON данные для отправки в теле запроса')
        parser.add_argument('-p', '--params', action='append', dest='params',
                          help='Query параметры URL (key=value)')
        parser.add_argument('--timeout', type=float, default=30,
                          help='Таймаут запроса в секундах (по умолчанию: 30)')
        parser.add_argument('-k', '--insecure', action='store_false', dest='verify_ssl',
                          help='Отключить проверку SSL сертификатов')
        parser.add_argument('--no-redirect', action='store_false', dest='allow_redirects',
                          help='Запретить следование редиректам')
        parser.add_argument('-i', '--include', action='store_true',
                          help='Показать заголовки ответа в выводе')
        
        return parser.parse_args(args)
    
    @staticmethod
    async def async_run(args=None):
        """Асинхронный запуск CLI интерфейса"""
        args = CLI.parse_args(args)
        pcib = PCIB()
        pcib.set_method(args.method)
        
        # Обработка заголовков
        if args.headers:
            for header in args.headers:
                if ':' in header:
                    key, value = header.split(':', 1)
                    pcib.set_header(key.strip(), value.strip())
        
        # Обработка данных
        if args.data:
            pcib.set_data(args.data)
        
        # Обработка JSON
        if args.json:
            try:
                json_data = json.loads(args.json)
                pcib.set_json(json_data)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Обработка query параметров
        if args.params:
            params = {}
            for param in args.params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            if params:
                pcib.set_params(params)
        
        # Установка дополнительных параметров
        pcib.set_timeout(args.timeout)
        pcib.set_verify_ssl(args.verify_ssl)
        pcib.set_allow_redirects(args.allow_redirects)
        
        # Выполнение запроса
        try:
            if await pcib.request(args.url):
                pcib.print_response(show_headers=args.include)
            else:
                sys.exit(1)
        except PCIBError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Точка входа для консольной команды"""
    asyncio.run(CLI.async_run())

if __name__ == '__main__':
    main()