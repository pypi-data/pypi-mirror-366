# Theme 153957

[![PyPI](https://img.shields.io/pypi/v/153957-theme)](https://pypi.org/project/153957-theme/)
[![License](https://img.shields.io/github/license/153957/153957-theme)](LICENSE)
[![Build](https://github.com/153957/153957-theme/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/153957/153957-theme/actions)

[View demo album here](https://153957.github.io/153957-theme/)


## Photo gallery template

Web photo gallery templates adapted to my personal preferences.


## Usage

This section describes how to install and use this theme.


### Installation

Install the `153597-theme` package:

    $ pip install 153957-theme


### Configure

In `sigal.conf.py` configuration for an album the `theme` setting should be
a path to a theme directory. However, since this theme is provided as a Python
package its location might be harder to get. Two options are available for
configuration:

The theme can be configured as a plugin or you can get the path by importing
the package. By setting is as plugin the theme is automatically set.

Set `theme` to an empty string and add the theme and menu plugins:

    theme = ''
    plugins = ['theme_153957.theme', 'theme_153957.full_menu', …]

The alternative:

    from theme_153957 import theme
    theme = theme.get_path()
    plugins = ['theme_153957.full_menu', …]


### Wrapping album

Use the settings `head`, `body_prefix`, and `body_suffix` to add additional
code to the templates. The value of `head` is appended to the `head` element,
the `body` settings are placed just after the body opening tag (`prefix`) and
just before the closing body tag (`suffix`). This allows embedding the album
in your own website.
