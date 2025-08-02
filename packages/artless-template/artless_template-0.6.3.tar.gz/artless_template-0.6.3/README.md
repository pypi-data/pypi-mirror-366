# artless-template

![PyPI Version](https://img.shields.io/pypi/v/artless-template)
![Development Status](https://img.shields.io/badge/status-3%20--%20Beta-blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/artless-template)
[![Downloads](https://static.pepy.tech/badge/artless-template)](https://pepy.tech/project/artless-template)
![PyPI - License](https://img.shields.io/pypi/l/artless-template)

The artless and minimalist templating for Python server-side rendering.

**artless-template** is a tiny (under 200 lines), dependency-free template engine, designed for generating HTML using either template files or native Python objects.

Perfect for modern, clean server-side rendering with a focus on simplicity, performance, and patterns like HTMX and No-JS.

## Why artless-template?

* 🪶 Tiny: Single module, no dependencies, no magic, no bloat
* ⚡ Fast & Small: Under 200 LOC, built for speed (see benchmarks)
* 🧹 Functional style: Mostly pure functions, no side effects, fully type-annotated
* 🐍 Modern: Python 3.11+ only
* ✅ Tested: 100% test coverage.
* 📚 Well-documented: With usage examples.

## Quickstart

### Installation

From PyPI:

``` console
$ pip install artless-template
```

From source:

``` console
$ git clone https://git.peterbro.su/peter/py3-artless-template
$ cd py3-artless-template
$ pip install .
```

### Template and tags usage

Create `templates/index.html` with contents:

``` html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>@title</title>
  </head>
  <body>
    <main>
        <section>
            <h1>@header</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                @users
            </table>
        </section>
    </main>
  </body>
</html>
```

``` python
from typing import final
from pathlib import Path
from random import randint
from dataclasses import dataclass
from artless_template import read_template, Tag as t

TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UserModel:
    name: str
    email: str
    is_admin: bool


users = [
    UserModel(
        name=f"User_{_}", email=f"user_{_}@gmail.com", is_admin=bool(randint(0, 1))
    )
    for _ in range(10_000)
]


users_markup = t(
    "tbody",
    [
        t(
            "tr",
            [
                t("td", user.name),
                t("td", user.email),
                t("td", "+" if user.is_admin else "-"),
            ],
        )
        for user in users
    ],
)

context = {
    "title": "Artless-template example",
    "header": "Users list",
    "users": users_markup,
}

template = read_template(TEMPLATES_DIR / "index.html").render(**context)
```

### Template and components usage

``` html
<!DOCTYPE html>
<html lang="en">
  ...
  <body>
    <main>
      @main
    </main>
  </body>
</html>
```

``` python
from artless_template import read_template, Component, Tag as t

...

class UsersTableComponent:
    def __init__(self, count: int):
        self.users = [
            UserModel(
                name=f"User_{_}", email=f"user_{_}@gmail.com", is_admin=bool(randint(0, 1))
            )
            for _ in range(count)
        ]

    def view(self):
        return t(
            "table",
            [
                t(
                    "thead",
                    [
                        t(
                            "tr",
                            [
                                t("th", "Name"),
                                t("th", "Email"),
                                t("th", "Admin"),
                            ]
                        )
                    ]
                ),
                t(
                    "tbody",
                    [
                        t(
                            "tr",
                            [
                                t("td", user.name),
                                t("td", user.email),
                                t("td", "+" if user.is_admin else "-"),
                            ],
                        )
                        for user in self.users
                    ]
                )
            ]
        )

template = read_template(TEMPLATES_DIR / "index.html").render(main=UsersTableComponent(100500))
```

### Asynchronous functions

The library provides async version of io-bound function - `read_template`. An asynchronous function has `a` prefix and called `aread_template`.

``` python
from artless_template import aread_template

template = await aread_template("some_template.html")
...
```

Read detailed reference **[documentation](https://pages.peterbro.su/py3-artless-template/reference.html)**.

## Performance

Performance comparison of the most popular template engines and artless-template library.
The benchmark render a HTML document with table of 10 thousand user models.

Run benchmark:

``` shellsession
$ python -m bemchmarks
```

Sorted results on i5 laptop (smaller is better):

``` python
{
    'mako': 0.05319607999990694,
    'jinja2': 0.27525966498069465,
    'artless': 0.5908581139810849,
    'dtl': 1.034598412021296,
    'fasthtml': 12.420113595988369
}
```

1. [Mako](https://www.makotemplates.org/) (0.05319 sec.)
2. [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) (0.27525 sec.)
3. **Artless-template (0.59085 sec.)**
4. [Django templates](https://docs.djangoproject.com/en/5.0/ref/templates/) (1.03459 sec.)
5. [FastHTML](https://github.com/AnswerDotAI/fasthtml/) (12.42011 sec.)

The performance of `artless-template` is better than the `Django template engine`, and much better than FastHTML, but worse than `Jinja2` and `Mako`.

## Roadmap

- [x] Simplify the Tag constructor.
- [x] Write detailed documentation with Sphinx.
- [x] Create async version of `read_template()` - `aread_template()`.
- [ ] Cythonize CPU/RAM-bound of code.

## Related projects

* [artless-core](https://pypi.org/project/artless-core/) - the artless and ultralight web framework for building minimal APIs and apps.
