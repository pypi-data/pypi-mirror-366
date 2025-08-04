from flask import Flask, render_template, request

_routes = {}

class Bullfinch:
    def __init__(self, name):
        self.app = Flask(name)
        self.name = name
        self.login = "admin"
        self.password = "1234"
        self.app.config['instance'] = self

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                user = request.form.get("username")
                pwd = request.form.get("password")
                if user == self.login and pwd == self.password:
                    return "Login successful!"
                return "Access Denied"
            return """
                <form method='post'>
                    Username: <input name='username'><br>
                    Password: <input name='password' type='password'><br>
                    <input type='submit'>
                </form>
            """

    def run(self, debug=True, host="0.0.0.0", port=8000):
        for route, view_func in _routes.items():
            self.app.route(route)(view_func)
        self.app.run(debug=debug, host=host, port=port)

def file_template(filename):
    return render_template(filename)

def password(flask_app):
    class PasswordSetter:
        def __eq__(self, value):
            flask_app.config['instance'].password = value
    return PasswordSetter()

def name(flask_app):
    class NameSetter:
        def __eq__(self, value):
            flask_app.config['instance'].login = value
    return NameSetter()
