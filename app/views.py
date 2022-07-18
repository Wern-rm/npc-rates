# -*- coding: utf-8 -*-
"""
    NCP Rates  Test Job
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2022 by Roman Morozov.
    :license: MIT, see LICENSE for more details.
"""
from flask import Blueprint, jsonify, make_response, request, Response
from extensions import db
import logging
import requests
from dateutil.parser import parse
from models import Rates
from datetime import timedelta
import zlib

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@bp.get('/')
def index():
    return make_response(jsonify(status=200, message='The system for obtaining the exchange rate for the National Bank of the Republic of Belarus'), 200)


@bp.get('/create/db')
def create_db():
    try:
        db.create_all()
        return make_response(jsonify(status=200, message='Success create DB.'), 200)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify(status=500, message='Error create DB.'), 500)


@bp.get('/update/rates')
def update_rates():
    """
    date format = 2022-7-18
    :return:
    """
    date = request.args.get('date', type=str, default=None)
    if date is None:
        logger.error('The <date> parameter was not found.')
        data = jsonify(status=400, message='The <date> parameter was not found.')
        return send_response(data=data.json, status_code=400)

    try:
        param_date = parse(date).date()
    except Exception as e:
        logger.error(e)
        data = jsonify(status=400, message='The <date> parameter was not found.')
        return send_response(data=data.json, status_code=400)

    response = requests.get(url=f'https://www.nbrb.by/api/exrates/rates?ondate={param_date}&periodicity=0')
    if response.status_code != 200:
        logger.error('The NC RB API is not available.')
        data = jsonify(status=400, message='The NC RB API is not available.')
        return send_response(data=data.json, status_code=400)

    for i in response.json():
        found = Rates.query.filter(Rates.date == parse(i['Date']).date(), Rates.currency_id == int(i['Cur_ID'])).first()
        if not found:
            new_rates = Rates(name=i['Cur_Name'],
                              iso=i['Cur_Abbreviation'],
                              currency_id=i['Cur_ID'],
                              scale=i['Cur_Scale'],
                              rate=i['Cur_OfficialRate'],
                              date=parse(i['Date']).date())
            db.session.add(new_rates)
            db.session.commit()
            logger.info(f'INSERT Rates - {i}')
        else:
            if found.rate != i['Cur_OfficialRate']:
                Rates.query.filter(Rates.id == found.id).update({
                    'rate': i['Cur_OfficialRate']
                })
                db.session.commit()
                logger.info(f'UPDATE Rates - {i}')
            else:
                logger.info(f'Rates is found - {i}')

    data = jsonify(status=200, message=f'Success update rates for {param_date}.')
    return send_response(data=data.json, status_code=200)


@bp.get('/rate')
def rate():
    date = request.args.get('date', type=str, default=None)
    currency_id = request.args.get('currency_id', type=int, default=0)
    if date is None:
        logger.error('The <date> parameter was not found.')
        data = jsonify(status=400, message='The <date> parameter was not found.', result=None)
        return send_response(data=data.json, status_code=400)

    if currency_id == 0:
        logger.error('The <currency_id> parameter was not found.')
        data = jsonify(status=400, message='The <currency_id> parameter was not found.', result=None)
        return send_response(data=data.json, status_code=400)

    try:
        param_date = parse(date).date()
    except Exception as e:
        logger.error(e)
        data = jsonify(status=400, message='The <date> parameter was not found.', result=None)
        return send_response(data=data.json, status_code=400)

    query_rate = Rates.query.filter(Rates.date == param_date, Rates.currency_id == currency_id).first()
    if not query_rate:
        logger.error('No data found.')
        data = jsonify(status=400, message='No data found.', result=None)
        return send_response(data=data.json, status_code=400)

    last_day_date = param_date - timedelta(days=1)
    query_last_day_rate = Rates.query.filter(Rates.date == last_day_date, Rates.currency_id == currency_id).first()
    if query_last_day_rate:
        data = jsonify(status=200,
                       message='Data received successfully.',
                       result=jsonify(currency_id=currency_id,
                                      iso=query_rate.iso,
                                      rate=query_rate.rate,
                                      date=param_date.strftime('%Y-%m-%d'),
                                      course_change=round(query_rate.rate - query_last_day_rate.rate, 3)).json)
        return send_response(data=data.json, status_code=200)
    else:
        data = jsonify(status=200,
                       message='Data received successfully.',
                       result=jsonify(currency_id=currency_id, iso=query_rate.iso, rate=query_rate.rate, date=param_date.strftime('%Y-%m-%d')).json)
        return send_response(data=data.json, status_code=200)


def send_response(data: dict, status_code: int) -> Response:
    _response = make_response(data, status_code)
    _response.headers['CRC32'] = zlib.crc32(bytes(str(data), 'utf-8'))
    return _response