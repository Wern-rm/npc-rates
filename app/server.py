# -*- coding: utf-8 -*-
"""
    NCP Rates  Test Job
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2022 by Roman Morozov.
    :license: MIT, see LICENSE for more details.
"""
from manager import create_app

if __name__ == "__main__":
    create_app().run(host='127.0.0.1', port=8080)