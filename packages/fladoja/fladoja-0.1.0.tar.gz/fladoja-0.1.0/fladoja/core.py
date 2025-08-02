import os
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

class Fladoja:
    def __init__(self, name: str):
        self.name = name
        self.routes = {}
        self.templates_dir = "templates"
        self.plugins = {}
        self.admin_enabled = False
        self.admin_password = None

    def site(self, path: str):
        def decorator(handler):
            self.routes[path] = handler
            return handler
        return decorator

    def plagen(self, name: str, plugin_type: str):
        def decorator(plugin_func):
            self.plugins[name] = {
                'type': plugin_type,
                'func': plugin_func
            }
            return plugin_func
        return decorator

    def file_template(self, filename: str, context: dict = None) -> str:
        try:
            with open(f"{self.templates_dir}/{filename}", "r", encoding="utf-8") as f:
                content = f.read()
                if context:
                    for key, value in context.items():
                        content = content.replace(f"{{{{ {key} }}}}", str(value))
                return content
        except FileNotFoundError:
            return f"Template {filename} not found"

    def enable_admin(self, initial_password: str = None):
        self.admin_enabled = True
        if initial_password:
            self.admin_password = self._hash_password(initial_password)
        self._setup_admin_routes()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _check_auth(self, input_password: str) -> bool:
        if not self.admin_password:
            return False
        return self._hash_password(input_password) == self.admin_password

    def _setup_admin_routes(self):
        @self.site('/admin/')
        def admin_panel(params):
            if not self._check_auth(params.get('password', '')):
                return self._login_form()
            
            files = [
                f for f in os.listdir(self.templates_dir) 
                if os.path.isfile(os.path.join(self.templates_dir, f))
            ]
            
            return self._render_admin_template('admin.html', {
                'files': files,
                'password': params.get('password', '')
            })

        @self.site('/admin/edit')
        def admin_edit(params):
            if not self._check_auth(params.get('password', '')):
                return self._login_form()
            
            filename = params.get('file')
            content = ""
            
            if filename:
                try:
                    with open(f"{self.templates_dir}/{filename}", "r", encoding="utf-8") as f:
                        content = f.read()
                except:
                    return "Error reading file"
            
            return self._render_admin_template('admin_edit.html', {
                'filename': filename,
                'content': content
            })

    def _render_admin_template(self, template_name: str, context: dict) -> str:
        """Рендеринг встроенных шаблонов админки"""
        templates = {
            'admin.html': """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Fladoja Admin</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .file-list { list-style: none; padding: 0; }
                    .file-list li { padding: 10px; border-bottom: 1px solid #eee; }
                    .file-list a { color: #0066cc; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Admin Panel</h1>
                    <ul class="file-list">
                        {% for file in files %}
                        <li>
                            {{ file }}
                            <a href="/admin/edit?file={{ file }}&password={{ password }}">Edit</a>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </body>
            </html>
            """,
            
            'admin_edit.html': """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Editing {{ filename }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .editor-container { max-width: 1000px; margin: 0 auto; }
                    textarea { width: 100%; height: 500px; font-family: monospace; }
                    button { padding: 8px 15px; background: #0066cc; color: white; border: none; }
                </style>
            </head>
            <body>
                <div class="editor-container">
                    <h1>Editing: {{ filename }}</h1>
                    <form action="/admin/save" method="post">
                        <input type="hidden" name="file" value="{{ filename }}">
                        <input type="hidden" name="password" value="{{ password }}">
                        <textarea name="content">{{ content }}</textarea>
                        <br>
                        <button type="submit">Save</button>
                    </form>
                </div>
            </body>
            </html>
            """
        }
        
        template = templates.get(template_name, '')
        for key, value in context.items():
            template = template.replace(f'{{{{ {key} }}}}', str(value))
            template = template.replace(f'%7B%7B%20{key}%20%7D%7D', str(value))  # URL encoded
        
        return template

    def _login_form(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fladoja Admin Login</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 50px; }
                .login-form { max-width: 400px; margin: 0 auto; }
                input, button { width: 100%; padding: 10px; margin: 5px 0; }
            </style>
        </head>
        <body>
            <div class="login-form">
                <h1>Admin Login</h1>
                <form method="get">
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        """

    def start(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        class FladojaHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.handle_request('GET')

            def do_POST(self):
                self.handle_request('POST')

            def handle_request(self, method: str):
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                params = parse_qs(parsed_path.query)
                params = {k: v[0] if v else '' for k, v in params.items()}

                if method == 'POST':
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length).decode()
                    post_params = parse_qs(post_data)
                    params.update({k: v[0] if v else '' for k, v in post_params.items()})

                if path in self.app.routes:
                    response = self.app.routes[path](params)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'404 Not Found')

        FladojaHandler.app = self
        
        print(f"Starting {self.name} on http://{host}:{port}")
        if debug:
            print("Debug mode: ON")
        
        server = HTTPServer((host, port), FladojaHandler)
        server.serve_forever()