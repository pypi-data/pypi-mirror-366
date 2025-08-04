# Bullfinch

Bullfinch — это простой Python-фреймворк для создания веб-приложений с помощью аннотаций (`@site`) и шаблонов.

## Пример

```python
from bullfinch import Bullfinch, site, file_template, start, password, name

app = Bullfinch('super duper')
app.app.config['instance'] = app

password(app.app) = "my_secret"
name(app.app) = "admin_user"

@site('/')
def Home():
    return file_template("index.html")

@start()
def run():
    app.run()
```

## Авторизация

Доступна по `/login` с логином `admin_user` и паролем `my_secret`.
