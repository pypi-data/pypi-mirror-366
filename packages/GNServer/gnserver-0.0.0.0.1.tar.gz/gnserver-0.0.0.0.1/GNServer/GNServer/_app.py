


import re
import uuid
import anyio
import decimal
import asyncio
import inspect
import traceback
import datetime
import KeyisBClient
from typing import Any, Awaitable, Callable, Dict, List, Optional, Pattern, Tuple, Union, AsyncGenerator
from dataclasses import dataclass
from aioquic.asyncio.server import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from typing import Any, AsyncGenerator, Union, get_origin, get_args
from urllib.parse import parse_qs

from KeyisBClient import gn

import sys

try:
    if not sys.platform.startswith("win"):
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print("uvloop не установлен")





import logging

logger = logging.getLogger("GNServer")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("[GNServer] %(name)s: %(levelname)s: %(message)s"))



@dataclass
class Route:
    method: str
    path_expr: str
    regex: Pattern[str]
    param_types: dict[str, Callable[[str], Any]]
    handler: Callable[..., Any]
    name: str

_PARAM_REGEX: dict[str, str] = {
    "str":   r"[^/]+",
    "path":  r".+",
    "int":   r"\d+",
    "float": r"[+-]?\d+(?:\.\d+)?",
    "bool":  r"(?:true|false|1|0)",
    "uuid":  r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
             r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
             r"[0-9a-fA-F]{12}",
    "datetime": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?",
    "date":     r"\d{4}-\d{2}-\d{2}",
    "time":     r"\d{2}:\d{2}:\d{2}(?:\.\d+)?",
    "decimal":  r"[+-]?\d+(?:\.\d+)?",
}

_CONVERTER_FUNC: dict[str, Callable[[str], Any]] = {
    "int":     int,
    "float":   float,
    "bool":    lambda s: s.lower() in {"1","true","yes","on"},
    "uuid":    uuid.UUID,
    "decimal": decimal.Decimal,
    "datetime": datetime.datetime.fromisoformat,
    "date":     datetime.date.fromisoformat,
    "time":     datetime.time.fromisoformat,
}

def _compile_path(path: str) -> tuple[Pattern[str], dict[str, Callable[[str], Any]]]:
    param_types: dict[str, Callable[[str], Any]] = {}
    rx_parts: list[str] = ["^"]
    i = 0
    while i < len(path):
        if path[i] != "{":
            rx_parts.append(re.escape(path[i]))
            i += 1
            continue
        j = path.index("}", i)
        spec = path[i+1:j]
        i = j + 1

        if ":" in spec:
            name, conv = spec.split(":", 1)
        else:
            name, conv = spec, "str"

        if conv.startswith("^"):
            rx = f"(?P<{name}>{conv})"
            typ = str
        else:
            rx = f"(?P<{name}>{_PARAM_REGEX.get(conv, _PARAM_REGEX['str'])})"
            typ = _CONVERTER_FUNC.get(conv, str)

        rx_parts.append(rx)
        param_types[name] = typ

    rx_parts.append("$")
    return re.compile("".join(rx_parts)), param_types

def _convert_value(raw: str | list[str], ann: Any, fallback: Callable[[str], Any]) -> Any:
    origin = get_origin(ann)
    args   = get_args(ann)

    if isinstance(raw, list) or origin is list:
        subtype = args[0] if (origin is list and args) else str
        if not isinstance(raw, list):
            raw = [raw]
        return [_convert_value(r, subtype, fallback) for r in raw]

    conv = _CONVERTER_FUNC.get(ann, ann) if ann is not inspect._empty else fallback
    return conv(raw) if callable(conv) else raw

def _ensure_async(fn: Callable[..., Any]) -> Callable[..., Any]:
    if inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn):
        return fn
    async def wrapper(*args, **kw):
        return fn(*args, **kw)
    return wrapper

class App:
    def __init__(self):
        self._routes: List[Route] = []

    def route(self, method: str, path: str, *, name: str | None = None):
        def decorator(fn: Callable[..., Any]):
            regex, param_types = _compile_path(path)
            self._routes.append(
                Route(
                    method.upper(),
                    path,
                    regex,
                    param_types,
                    _ensure_async(fn),
                    name or fn.__name__,
                )
            )
            return fn
        return decorator

    def get(self, path: str, *, name: str | None = None):
        return self.route("GET", path, name=name)

    def post(self, path: str, *, name: str | None = None):
        return self.route("POST", path, name=name)

    def put(self, path: str, *, name: str | None = None):
        return self.route("PUT", path, name=name)

    def delete(self, path: str, *, name: str | None = None):
        return self.route("DELETE", path, name=name)

    def custom(self, method: str, path: str, *, name: str | None = None):
        return self.route(method, path, name=name)


    async def dispatch(
        self, request: gn.GNRequest
    ) -> Union[gn.GNResponse, AsyncGenerator[gn.GNResponse, None]]:
        path    = request.url.path
        method  = request.method.upper()
        cand    = {path, path.rstrip("/") or "/", f"{path}/"}
        allowed = set()

        for r in self._routes:
            m = next((r.regex.fullmatch(p) for p in cand if r.regex.fullmatch(p)), None)
            if not m:
                continue

            allowed.add(r.method)
            if r.method != method:
                continue

            sig = inspect.signature(r.handler)
            def _ann(name: str):
                param = sig.parameters.get(name)
                return param.annotation if param else inspect._empty

            kw: dict[str, Any] = {
                name: _convert_value(val, _ann(name), r.param_types.get(name, str))
                for name, val in m.groupdict().items()
            }

            for qn, qvals in parse_qs(request.url.query, keep_blank_values=True).items():
                if qn in kw:
                    continue
                raw = qvals if len(qvals) > 1 else qvals[0]
                kw[qn] = _convert_value(raw, _ann(qn), str)

            if "request" in sig.parameters:
                kw["request"] = request

            if inspect.isasyncgenfunction(r.handler):
                return r.handler(**kw)

            result = await r.handler(**kw)
            if isinstance(result, gn.GNResponse):
                return result
            raise TypeError(
                f"{r.handler.__name__} returned {type(result)}; GNResponse expected"
            )

        if allowed:
            return gn.GNResponse("gn:origin:405", {'error': 'Method Not Allowed'})
        return gn.GNResponse("gn:origin:404", {'error': 'Not Found'})


    class _ServerProto(QuicConnectionProtocol):
        def __init__(self, *a, api: "App", **kw):
            super().__init__(*a, **kw)
            self._api = api
            self._buffer: Dict[int, bytearray] = {}
            self._streams: Dict[int, Tuple[asyncio.Queue[Optional[gn.GNRequest]], bool]] = {}

        def quic_event_received(self, event: QuicEvent):
            if isinstance(event, StreamDataReceived):
                buf = self._buffer.setdefault(event.stream_id, bytearray())
                buf.extend(event.data)

                # пока не знаем, это стрим или нет

                if len(buf) < 8: # не дошел даже frame пакета
                    logger.debug(f'Пакет отклонен: {buf} < 8. Не доставлен фрейм')
                    return
                
                    
                # получаем длинну пакета
                mode, stream, lenght = gn.GNRequest.type(buf)

                if mode != 2: # не наш пакет
                    logger.debug(f'Пакет отклонен: mode пакета {mode}. Разрешен 2')
                    return
                
                if not stream: # если не стрим, то ждем конец quic стрима и запускаем обработку ответа
                    if event.end_stream:
                        request = gn.GNRequest.deserialize(buf, 2)
                        # request.stream_id = event.stream_id
                        # loop = asyncio.get_event_loop()
                        # request.fut = loop.create_future()
                        
                        request.stream_id = event.stream_id
                        asyncio.create_task(self._handle_request(request))
                        logger.debug(f'Отправлена задача разрешения пакета {request} route -> {request.route}')

                        self._buffer.pop(event.stream_id, None)
                    return
                
                # если стрим, то смотрим сколько пришло данных
                if len(buf) < lenght: # если пакет не весь пришел, пропускаем
                    return

                # первый в буфере пакет пришел полностью
        
                # берем пакет
                data = buf[:lenght]

                # удаляем его из буфера
                del buf[:lenght]

                # формируем запрос
                request = gn.GNRequest.deserialize(data, 2)

                logger.debug(request, f'event.stream_id -> {event.stream_id}')

                request.stream_id = event.stream_id

                queue, inapi = self._streams.setdefault(event.stream_id, (asyncio.Queue(), False))

                if request.method == 'gn:end-stream':
                    if event.stream_id in self._streams:
                        _ = self._streams.get(event.stream_id)
                        if _ is not None:
                            queue, inapi = _
                            if inapi:
                                queue.put_nowait(None)
                                self._buffer.pop(event.stream_id)
                                self._streams.pop(event.stream_id)
                                logger.debug(f'Закрываем стрим [{event.stream_id}]')
                                return




                queue.put_nowait(request)

                # отдаем очередь в интерфейс
                if not inapi:
                    self._streams[event.stream_id] = (queue, True)

                    async def w():
                        while True:
                            chunk = await queue.get()
                            if chunk is None:
                                break
                            yield chunk

                    request._stream = w
                    asyncio.create_task(self._handle_request(request))

        async def _handle_request(self, request: gn.GNRequest):
            try:
                
                response = await self._api.dispatch(request)
                
                response = await self.resolve_extra_response(response)


                if inspect.isasyncgen(response):
                    async for chunk in response:  # type: ignore[misc]
                        chunk._stream = True
                        self._quic.send_stream_data(request.stream_id, chunk.serialize(3), end_stream=False)
                        self.transmit()
                        
                    l = gn.GNResponse('gn:end-stream')
                    l._stream = True
                    self._quic.send_stream_data(request.stream_id, l.serialize(3), end_stream=True)
                    self.transmit()
                    return


                self._quic.send_stream_data(request.stream_id, response.serialize(3), end_stream=True)
                logger.debug(f'Отправлен на сервер ответ -> {response.command()} {response.payload if len(response.payload) < 200 else ''}')
                self.transmit()
            except Exception as e:
                logger.error('GNServer: error\n'  + traceback.format_exc())

                response = gn.GNResponse('gn:origin:500:Internal Server Error')
                self._quic.send_stream_data(request.stream_id, response.serialize(3), end_stream=True)
                self.transmit()
        
        async def resolve_extra_response(self, response: Union[gn.GNResponse, AsyncGenerator[gn.GNResponse, None]]) -> Union[gn.GNResponse, AsyncGenerator[gn.GNResponse, None]]:

            file_types = (
                'html',
                'css',
                'js',
                'svg'
            )

            if isinstance(response, gn.GNResponse):
                payload = response.payload
                if payload is not None:
                    for ext_file in file_types:
                        ext_file_ = payload.get(ext_file)
                        if ext_file_ is not None:
                            if isinstance(ext_file_, str):
                                if ext_file_.startswith('/') or ext_file_.startswith('./'):
                                    try:
                                        async with await anyio.open_file(ext_file_, mode="rb") as file:
                                            payload[ext_file] = await file.read()
                                    except Exception as e:
                                        payload['html'] = f'GNServer error: {e}'
                                        logger.debug(f'error resolving extra response -> {traceback.format_exc()}')

                        

            return response



    def run(
        self,
        host: str,
        port: int,
        cert_path: str,
        key_path: str,
        *,
        idle_timeout: float = 20.0,
        wait: bool = True
    ):
        cfg = QuicConfiguration(
            alpn_protocols=["gn:backend"], is_client=False, idle_timeout=idle_timeout
        )
        cfg.load_cert_chain(cert_path, key_path)

        async def _main():
            await serve(
                host,
                port,
                configuration=cfg,
                create_protocol=lambda *a, **kw: App._ServerProto(*a, api=self, **kw),
                retry=False,
            )
            if wait:
                await asyncio.Event().wait()

        asyncio.run(_main())
