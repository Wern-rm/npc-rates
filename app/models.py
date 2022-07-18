# -*- coding: utf-8 -*-
"""
    NCP Rates  Test Job
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2022 by Roman Morozov.
    :license: MIT, see LICENSE for more details.
"""
from extensions import db


class Rates(db.Model):
    __tablename__ = 'rates'

    id = db.Column(db.INTEGER(), primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    iso = db.Column(db.VARCHAR(3), nullable=False)
    currency_id = db.Column(db.INTEGER(), nullable=False)
    scale = db.Column(db.INTEGER(), nullable=False)
    rate = db.Column(db.FLOAT(), nullable=False)
    date = db.Column(db.DATE(), nullable=False)

    def __init__(self, name, iso, currency_id, scale, rate, date):
        self.name = name
        self.iso = iso
        self.currency_id = currency_id
        self.scale = scale
        self.rate = rate
        self.date = date