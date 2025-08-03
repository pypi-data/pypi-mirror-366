import sys
import asyncio
import threading
import mimetypes
import re
import json
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.parse
import websockets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jsmin import jsmin
from cssmin import cssmin
from syqlorix import *

class C:
    PRIMARY = '\033[38;5;51m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    INFO = '\033[94m'
    MUTED = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

_context_stack = []

LIVE_RELOAD_SCRIPT = """
<script>
    (function() {{
        const socket = new WebSocket("ws://{host}:{port}");
        socket.onmessage = (event) => {{ if (event.data === 'reload') window.location.reload(); }};
        socket.onclose = () => {{ console.log('Syqlorix: Live-reload disconnected. Manual refresh required.'); }};
        socket.onerror = (error) => {{ console.error('Syqlorix: WebSocket error:', error); }};
    }})();
</script>
"""

class Node:
    _SELF_CLOSING_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, *children, **attributes):
        self.tag_name = self.__class__.__name__.lower()
        if self.tag_name in ("component", "comment"):
            self.tag_name = ""
        self.attributes = {k.rstrip('_'): v for k, v in attributes.items()}
        self.children = list(children)
        if _context_stack:
            _context_stack[-1].children.append(self)

    def __truediv__(self, other):
        if isinstance(other, Node):
            self.children.append(other)
        else:
            self.children.append(str(other))
        return self

    def __enter__(self):
        _context_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _context_stack.pop()

    def _format_attrs(self):
        if not self.attributes:
            return ""
        parts = []
        for key, value in self.attributes.items():
            if isinstance(value, bool):
                if value:
                    parts.append(key)
            elif value is not None:
                parts.append(f'{key}="{value}"')
        return " " + " ".join(parts)

    def render(self, indent=0, pretty=True):
        pad = "  " * indent if pretty else ""
        attrs = self._format_attrs()
        if not self.tag_name:
            return "".join(c.render(indent, pretty) if isinstance(c, Node) else (f"{pad}{c}\n" if pretty else str(c)) for c in self.children)
        if self.tag_name in self._SELF_CLOSING_TAGS:
            return f"{pad}<{self.tag_name}{attrs}>" + ("\n" if pretty else "")
        nl, inner_pad = ("\n", "  " * (indent + 1)) if pretty else ("", "")
        html = f"{pad}<{self.tag_name}{attrs}>{nl}"
        for child in self.children:
            if isinstance(child, Node):
                html += child.render(indent + 1, pretty)
            else:
                html += f"{inner_pad}{child}{nl}"
        html += f"{pad}</{self.tag_name}>{nl}"
        return html

class Component(Node):
    pass

class Comment(Node):
    def render(self, indent=0, pretty=True):
        pad = "  " * indent if pretty else ""
        content = "".join(str(c) for c in self.children)
        return f"{pad}<!-- {content} -->" + ("\n" if pretty else "")

class head(Node):
    pass

class body(Node):
    pass

class style(Node):
    def __init__(self, css_content, **attributes):
        super().__init__(css_content, **attributes)

    def render(self, indent=0, pretty=True):
        content = str(self.children[0])
        if not pretty and cssmin:
            try:
                content = cssmin(content)
            except Exception as e:
                print(f"{C.WARNING}Could not minify CSS: {e}{C.END}")
        self.children = [content]
        return super().render(indent, pretty)

class script(Node):
    def __init__(self, js_content="", src=None, type="text/javascript", **attributes):
        if src:
            attributes['src'] = src
            super().__init__(**attributes)
        else:
            super().__init__(js_content, **attributes)
        attributes['type'] = type

    def render(self, indent=0, pretty=True):
        if not pretty and not self.attributes.get('src') and jsmin and self.children:
            content = str(self.children[0])
            try:
                content = jsmin(content)
            except Exception as e:
                print(f"{C.WARNING}Could not minify JS: {e}{C.END}")
            self.children = [content]
        return super().render(indent, pretty)

class Request:
    def __init__(self, handler: BaseHTTPRequestHandler):
        self.method = handler.command
        self.path_full = handler.path
        parsed_url = urllib.parse.urlparse(handler.path)
        self.path = parsed_url.path
        self.query_params = {k: v[0] if len(v) == 1 else v for k, v in urllib.parse.parse_qs(parsed_url.query).items()}
        self.headers = dict(handler.headers)
        self.path_params = {}
        self.body = b''
        self.form_data = {}
        self.json_data = {}
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            self.body = handler.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            if 'application/x-www-form-urlencoded' in content_type:
                self.form_data = {k: v[0] if len(v) == 1 else v for k, v in urllib.parse.parse_qs(self.body.decode('utf-8')).items()}
            elif 'application/json' in content_type:
                try:
                    self.json_data = json.loads(self.body.decode('utf-8'))
                except json.JSONDecodeError:
                    print(f"{C.WARNING}Warning: Could not decode JSON body.{C.END}")

class RedirectResponse:
    """A special class to signify a redirect."""
    def __init__(self, location, status_code=302):
        self.location = location
        self.status_code = status_code

def redirect(location, status_code=302):
    """Returns a response object that triggers a browser redirect."""
    return RedirectResponse(location, status_code)

class TestResponse:
    """Holds the response from a test request."""
    def __init__(self, response_data, status_code, headers):
        self.status_code = status_code
        self.headers = headers
        
        if isinstance(response_data, Syqlorix):
            self.text = response_data.render(pretty=False)
        elif isinstance(response_data, Node):
            self.text = Syqlorix(head(), body(response_data)).render(pretty=False)
        else:
            self.text = str(response_data)

class TestClient:
    """A client to make test requests to the Syqlorix application."""
    def __init__(self, app):
        self.app = app

    def _make_request(self, method, path, form_data=None):
        
        class MockTestRequest:
            def __init__(self, method, path, path_params, form_data):
                self.method = method
                self.path = path
                self.path_full = path
                self.path_params = path_params
                self.form_data = form_data or {}
                self.query_params = {}
                self.headers = {}

        for route_regex, methods, handler_func in self.app._routes:
            match = route_regex.match(path)
            if match:
                if method not in methods:
                    return TestResponse("Method Not Allowed", 405, {})

                path_params = match.groupdict()
                
                import inspect
                sig = inspect.signature(handler_func)
                if len(sig.parameters) > 0:
                    request_obj = MockTestRequest(method, path, path_params, form_data)
                    response_data = handler_func(request_obj)
                else:
                    response_data = handler_func()

                status_code = 200
                headers = {}

                if isinstance(response_data, RedirectResponse):
                    status_code = response_data.status_code
                    headers['Location'] = response_data.location
                elif isinstance(response_data, tuple):
                    response_data, status_code = response_data

                return TestResponse(response_data, status_code, headers)

        # No route matched
        if 404 in self.app._error_handlers:
            response_data = self.app._error_handlers[404](None)
            return TestResponse(response_data, 404, {})
        
        return TestResponse("Not Found", 404, {})

    def get(self, path):
        return self._make_request('GET', path)

    def post(self, path, data=None):
        return self._make_request('POST', path, form_data=data)
    
class Blueprint:
    def __init__(self, name, url_prefix=""):
        self.name = name
        self.url_prefix = url_prefix.rstrip('/')
        self._routes = []

    def route(self, path, methods=['GET']):
        def decorator(handler_func):
            full_path = self.url_prefix + path
            path_regex = re.sub(r'<([^>]+)>', r'(?P<\1>[^/]+)', full_path) + '$'
            self._routes.append((re.compile(path_regex), set(m.upper() for m in methods), handler_func))
            return handler_func
        return decorator

class Syqlorix(Node):
    def __init__(self, *children, **attributes):
        super().__init__(*children, **attributes)
        self.tag_name = "html"
        self._routes = []
        self._middleware = []
        self._error_handlers = {}

    def before_request(self, func):
        """A decorator to register a function to run before each request."""
        self._middleware.append(func)
        return func
    
    def error_handler(self, code):
        """A decorator to register a custom handler for an HTTP error code."""
        def decorator(func):
            self._error_handlers[code] = func
            return func
        return decorator

    def route(self, path, methods=['GET']):
        def decorator(handler_func):
            path_regex = re.sub(r'<([^>]+)>', r'(?P<\1>[^/]+)', path) + '$'
            self._routes.append((re.compile(path_regex), set(m.upper() for m in methods), handler_func))
            return handler_func
        return decorator
    
    def register_blueprint(self, blueprint):
        self._routes.extend(blueprint._routes)

    def test_client(self):
        """Creates a test client for this application."""
        return TestClient(self)

    def render(self, pretty=True, live_reload_port=None, live_reload_host=None):
        html_string = "<!DOCTYPE html>\n" + super().render(indent=0, pretty=pretty)
        if live_reload_port and pretty: # Only inject script in dev mode
            script_tag = LIVE_RELOAD_SCRIPT.format(host=live_reload_host, port=live_reload_port)
            html_string = html_string.replace("</body>", f"{script_tag}</body>")
        return html_string

    def _live_reload_manager(self, host, ws_port, watch_dirs):
        try:
            asyncio.run(self._async_live_reload(host, ws_port, watch_dirs))
        except KeyboardInterrupt:
            pass

    async def _async_live_reload(self, host, ws_port, watch_dirs):
        active_sockets = set()


        async def send_reload_to_all():
            """Gathers all send tasks and executes them."""
            if active_sockets:
                await asyncio.gather(*[ws.send("reload") for ws in active_sockets])

        stop_event = asyncio.Event()

        async def websocket_handler(websocket):
            active_sockets.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                active_sockets.remove(websocket)

        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, loop, sockets):
                self.loop = loop
                self.sockets = sockets

            def on_modified(self, event):
                if not event.is_directory:
                    print(f"✨ {C.WARNING}File changed ({event.src_path}). Triggering reload...{C.END}")
                    asyncio.run_coroutine_threadsafe(send_reload_to_all(), self.loop)

        server = await websockets.serve(websocket_handler, host, ws_port)
        print(f"🛰️  {C.INFO}Syqlorix Live-Reload server listening on {C.BOLD}ws://{host}:{ws_port}{C.END}")

        loop = asyncio.get_running_loop()

        observer = Observer()
        for watch_dir in watch_dirs:
            observer.schedule(ChangeHandler(loop, active_sockets), path=str(watch_dir), recursive=True)
            print(f"👀 {C.INFO}Watching for changes in {C.BOLD}'{watch_dir}' (recursively){C.END}")
        observer.start()

        try:
            await stop_event.wait()
        finally:
            observer.stop()
            observer.join()
            server.close()
            await server.wait_closed()

    def run(self, file_path, host="127.0.0.1", port=8000, live_reload=True, max_port_attempts=10):

        current_port = port
        http_server = None

        print(f"🔥 {C.PRIMARY}Starting server for {C.BOLD}{Path(file_path).name}{C.END}...")

        project_root = Path(file_path).parent.resolve()
        watch_dirs = [project_root]

        for attempt in range(max_port_attempts):
            try:
                
                class SyqlorixRequestHandler(BaseHTTPRequestHandler):
                    _app_instance = self

                    def handle_one_request(self):
                        try:
                            super().handle_one_request()
                        except (BrokenPipeError, ConnectionResetError):
                            pass

                    def _send_syqlorix_404(self, path):
                        error_page = Syqlorix(
                            head(
                                title("404 Not Found"),
                                style("""
                                    body { background-color: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; display: grid; place-content: center; height: 100vh; margin: 0; text-align: center; }
                                    .container { padding: 2rem 4rem; border-radius: 8px; background: #2a2a4a; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
                                    h1 { color: #ff5370; font-size: 5rem; margin: 0; }
                                    h2 { color: #00a8cc; margin-bottom: 1rem; }
                                    p { color: #aaa; margin-top: 0.5rem; }
                                    code { background-color: #333; padding: 0.2rem 0.4rem; border-radius: 4px; color: #ffcb6b; }
                                    a { color: #72d5ff; font-weight: bold; text-decoration: none; }
                                    a:hover { text-decoration: underline; }
                                """)
                            ),
                            body(
                                div(
                                    h1("404"),
                                    h2("Page Not Found"),
                                    p("The requested path ", code(path), " was not found on this server."),
                                    p(a("Return to Homepage", href="/")),
                                    class_="container"
                                )
                            )
                        )
                        error_html = error_page.render(pretty=True).encode('utf-8')
                        self.send_response(404)
                        self.send_header("Content-type", "text/html")
                        self.send_header("Content-length", str(len(error_html)))
                        self.end_headers()
                        self.wfile.write(error_html)

                def _handle_request(self, is_head=False):
                    request = Request(self)
                    syqlorix_app = self._app_instance
                    project_root = Path(sys.argv[0] if sys.argv[0] else '.').parent.resolve()
                    response_data = None
                    status_code = 200

                    try:
                        for func in syqlorix_app._middleware:
                            possible_response = func(request)
                            if possible_response is not None:
                                response_data = possible_response
                                break
                        
                        if response_data is None:
                            for route_regex, methods, handler_func in syqlorix_app._routes:
                                match = route_regex.match(request.path)
                                if match:
                                    if request.method not in methods:
                                        if 405 in syqlorix_app._error_handlers:
                                            response_data = syqlorix_app._error_handlers[405](request)
                                            status_code = 405
                                        else:
                                            self.send_error(405, "Method Not Allowed")
                                            return
                                        break
                                    
                                    request.path_params = match.groupdict()
                                    response_data = handler_func(request)
                                    break
                            else:
                                static_dir_abs = (project_root / 'static').resolve()
                                file_name = 'index.html' if request.path == '/' else request.path.lstrip('/')
                                try:
                                    static_file_path = (static_dir_abs / file_name).resolve(strict=True)
                                    if static_file_path.is_file() and static_file_path.is_relative_to(static_dir_abs):
                                        file_hash = hashlib.md5(static_file_path.read_bytes()).hexdigest()
                                        if request.headers.get('If-None-Match') == file_hash:
                                            self.send_response(304); self.end_headers(); return
                                        
                                        mime_type, _ = mimetypes.guess_type(static_file_path)
                                        self.send_response(200)
                                        self.send_header('Content-type', mime_type or 'application/octet-stream')
                                        self.send_header('ETag', file_hash)
                                        if not is_head: self.send_header("Content-length", str(static_file_path.stat().st_size))
                                        self.end_headers()
                                        if not is_head:
                                            with open(static_file_path, 'rb') as f: self.wfile.write(f.read())
                                        return
                                except (FileNotFoundError, ValueError, NotADirectoryError):
                                    pass

                        if response_data is None:
                            status_code = 404
                            if 404 in syqlorix_app._error_handlers:
                                response_data = syqlorix_app._error_handlers[404](request)
                            else:
                                self._send_syqlorix_404(request.path); return
                        
                        if isinstance(response_data, RedirectResponse):
                            self.send_response(response_data.status_code); self.send_header('Location', response_data.location); self.end_headers(); return
                        
                        if isinstance(response_data, tuple): response_data, status_code = response_data

                        content_type = "text/html"
                        if isinstance(response_data, (dict, list)):
                            content_type = "application/json"; html_bytes = json.dumps(response_data, indent=2).encode("utf-8")
                        elif isinstance(response_data, Syqlorix):
                            html_bytes = response_data.render(pretty=True, live_reload_port=self._app_instance._live_reload_ws_port, live_reload_host=self._app_instance._live_reload_host).encode("utf-8")
                        elif isinstance(response_data, Node):
                            temp_syqlorix = Syqlorix(head(), body(response_data)); html_bytes = temp_syqlorix.render(pretty=True, live_reload_port=self._app_instance._live_reload_ws_port, live_reload_host=self._app_instance._live_reload_host).encode("utf-8")
                        else:
                            html_bytes = str(response_data).encode("utf-8")
                        
                        self.send_response(status_code); self.send_header("Content-type", content_type); self.send_header("Content-length", str(len(html_bytes))); self.end_headers(); self.wfile.write(html_bytes)

                    except Exception as e:
                        print(f"{C.ERROR}Error processing request for '{request.path}': {e}{C.END}", file=sys.stderr)
                        status_code = 500
                        if 500 in syqlorix_app._error_handlers:
                            try:
                                response_data = syqlorix_app._error_handlers[500](e)
                                
                                html_bytes = str(response_data).encode("utf-8"); self.send_response(500); self.send_header("Content-type", "text/html"); self.send_header("Content-length", str(len(html_bytes))); self.end_headers(); self.wfile.write(html_bytes)
                            except Exception as inner_e:
                                print(f"{C.ERROR}CRITICAL: The custom 500 error handler failed: {inner_e}{C.END}", file=sys.stderr)
                                self.send_error(500, "Internal Server Error & Error in Error Handler")
                        else:
                            self.send_error(500, "Internal Server Error")

                    def do_GET(self): self._handle_request()
                    def do_POST(self): self._handle_request()
                    def do_PUT(self): self._handle_request()
                    def do_DELETE(self): self._handle_request()
                    def do_HEAD(self): self._handle_request(is_head=True)

                    def log_message(self, format, *args):
                        status_code = str(args[1])
                        color = C.WARNING
                        if status_code.startswith('2') or status_code == '304': color = C.SUCCESS
                        elif status_code.startswith('4') or status_code.startswith('5'): color = C.ERROR
                        print(f"↳  {C.MUTED}HTTP {self.command} {self.path} - {color}{status_code}{C.END}")

                http_server = HTTPServer((host, current_port), SyqlorixRequestHandler)
                break 
            except OSError as e:
                if e.errno == 98:
                    if attempt < max_port_attempts - 1:
                        print(f"{C.WARNING}Port {current_port} already in use. Trying {current_port + 2}...{C.END}")
                        current_port += 2
                    else:
                        print(f"\n{C.ERROR}ERROR: All attempts ({max_port_attempts}) to find an available port failed.{C.END}", file=sys.stderr)
                        sys.exit(1)
                else: raise

        self._live_reload_ws_port = current_port + 1
        self._live_reload_enabled = live_reload
        self._live_reload_host = host

        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        print(f"🚀 {C.SUCCESS}Syqlorix server running on {C.BOLD}http://{host}:{current_port}{C.END}")

        if live_reload:
            reload_thread = threading.Thread(target=self._live_reload_manager, args=(host, self._live_reload_ws_port, watch_dirs), daemon=True)
            reload_thread.start()
        
        if self._routes:
            route_paths = [path for regex, methods, func in self._routes for path in regex.pattern.split('$')[0:1]]
            print(f"🌍 {C.INFO}Routes discovered: {', '.join(sorted(route_paths))}{C.END}")
        else:
            print(f"ℹ️  {C.INFO}No routes defined. Serving default content for all requests.{C.END}")

        print(f"   {C.MUTED}Press Ctrl+C to stop.{C.END}")
        
        try:
            http_thread.join()
        except KeyboardInterrupt:
            print(f"\n🛑 {C.WARNING}Shutting down...{C.END}")
        finally:
            http_server.shutdown()
            http_server.server_close()
            print(f"   {C.SUCCESS}Server stopped.{C.END}")

_TAG_NAMES = [
    'a', 'abbr', 'address', 'article', 'aside', 'audio', 'b', 'bdi', 'bdo', 'blockquote', 'button', 'canvas', 
    'caption', 'cite', 'code', 'data', 'datalist', 'dd', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 
    'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'i', 
    'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark', 'meta', 'meter', 
    'nav', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'picture', 'pre', 'progress', 'q', 
    'rp', 'rt', 'ruby', 's', 'samp', 'section', 'select', 'small', 'source', 'span', 'strong', 'summary', 
    'sup', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'u', 
    'ul', 'var', 'video', 'br', 'hr'
]

for tag in _TAG_NAMES:
    if tag not in ['style', 'script', 'head', 'body']:
        globals()[tag] = type(tag, (Node,), {})

input_ = globals()['input']

doc = Syqlorix()

# I only use this when I want to add some customs that are requested
__all__ = [
    'Node', 'Syqlorix', 'Component', 'Comment', 'Request', 'Blueprint', 'redirect',
    'head', 'body', 'style', 'script',
    'doc',
    'input_',
    'a', 'abbr', 'address', 'article', 'aside', 'audio', 'b', 'bdi', 'bdo', 'blockquote', 'button', 'canvas', 
    'caption', 'cite', 'code', 'data', 'datalist', 'dd', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 
    'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'i', 
    'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark', 'meta', 'meter', 
    'nav', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'picture', 'pre', 'progress', 'q', 
    'rp', 'rt', 'ruby', 's', 'samp', 'section', 'select', 'small', 'source', 'span', 'strong', 'summary', 
    'sup', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'u', 
    'ul', 'var', 'video', 'br', 'hr'
]

__all__.extend(_TAG_NAMES)
