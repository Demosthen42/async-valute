import asyncio
import aiohttp
from valute import Currency
import json
import logging
import argparse
from aiohttp import web
import sys
from sys import stdout

LOGGER_FORMAT = '%(asctime)s %(message)s'
URL = 'https://www.cbr-xml-daily.ru/daily_json.js'

parser = argparse.ArgumentParser()
parser.add_argument('--rub', type=float, default=100)
parser.add_argument('--eur', type=float, default=200)
parser.add_argument('--usd', type=float, default=300)
parser.add_argument('--period', type=int, default=600)
parser.add_argument('--debug', required=False, default=1)

logging.basicConfig(stream=stdout, format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
logger = logging.getLogger()
#logFormatter = logging.Formatter\
#("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
#consoleHandler = logging.Handler(stdout)
#consoleHandler.setLevel(logging.DEBUG)
#consoleHandler.setFormatter(logFormatter)
##consoleHandler.flush = sys.stdout.flush
#logger.addHandler(consoleHandler)


class Val(Currency):
    def __init__(self, name, amount, rate):
        super().__init__(name, amount, rate)


class Handler:
    def __init__(self):
        pass

    async def get_usd(self, request):
        logger.debug(await request.text())
        response_obj = {'name': USD.name, 'amount': to_fixed(USD.amount, 2), 'rate': to_fixed(USD.rate, 2)}
        logger.debug(response_obj)
        return web.Response(text=json.dumps(response_obj), status=200, content_type='text/plain')

    async def get_rub(self, request):
        logger.debug(await request.text())
        response_obj = {'name': RUB.name, 'amount': to_fixed(RUB.amount, 2), 'rate': to_fixed(RUB.rate, 2)}
        logger.debug(response_obj)
        return web.Response(text=json.dumps(response_obj), status=200, content_type='text/plain')

    async def get_eur(self, request):
        logger.debug(await request.text())
        response_obj = {'name': EUR.name, 'amount': to_fixed(EUR.amount, 2), 'rate': to_fixed(EUR.rate, 2)}
        logger.debug(response_obj)
        return web.Response(text=json.dumps(response_obj), status=200, content_type='text/plain')

    async def get_amount(self, request):
        logger.debug(await request.text())
        response_obj = print_valute()
        logger.debug(response_obj)
        return web.Response(text=response_obj, status=200, content_type='text/plain')

    async def post_amount_set(self, request):
        try:
            text = await request.text()
            logger.debug(text)
            media = json.loads(text)
            if 'rub' in media:
                RUB.amount = float(media['rub'])
            if 'usd' in media:
                USD.amount = float(media['usd'])
            if 'eur' in media:
                EUR.amount = float(media['eur'])
            response_obj = {'status': 'success'}
            logger.debug(response_obj)
            return web.Response(text=json.dumps(response_obj), status=200, content_type='text/plain')
        except Exception as e:
            response_obj = {'status': 'failed', 'message': str(e)}
            return web.Response(text=json.dumps(response_obj), status=500, content_type='text/plain')

    async def post_modify(self, request):
        try:
            text = await request.text()
            logger.debug(text)
            media = json.loads(text)
            if 'rub' in media:
                RUB.amount += float(media['rub'])
            if 'usd' in media:
                USD.amount += float(media['usd'])
            if 'eur' in media:
                EUR.amount += float(media['eur'])
            response_obj = {'status': 'success'}
            logger.debug(response_obj)
            return web.Response(text=json.dumps(response_obj), status=200, content_type='text/plain')
        except Exception as e:
            response_obj = {'status': 'failed', 'message': str(e)}
            return web.Response(text=json.dumps(response_obj), status=500, content_type='text/plain')


def to_fixed(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


def print_valute():
    sum_in_rub = RUB.amount + USD.amount * USD.rate + EUR.amount * EUR.rate
    sum_in_usd = sum_in_rub / USD.rate
    sum_in_eur = sum_in_rub / EUR.rate
    return f'rub: {to_fixed(RUB.amount, 2)}' + '\n' \
           + f'usd: {to_fixed(USD.amount, 2)}' + '\n' \
           + f'eur: {to_fixed(EUR.amount, 2)}' + '\n\n' \
           + f'rub-usd: {to_fixed(USD.rate, 2)}' + '\n' \
           + f'rub-eur: {to_fixed(EUR.rate, 2)}' + '\n' \
           + f'usd-eur: {to_fixed(EUR.rate / USD.rate, 2)}' + '\n\n' \
           + f'sum: {to_fixed(sum_in_rub, 2)} rub / {to_fixed(sum_in_usd, 2)} usd / {to_fixed(sum_in_eur, 2)} eur'


async def print_somewhat():
    logger = logging.getLogger()
    temp_valute = [0, 0, 0, 0, 0]
    while True:
        temp_bool = 0
        for i, j in zip(temp_valute, [RUB.amount, USD.amount, EUR.amount, USD.rate, EUR.rate]):
            if i != j:
                temp_bool = 1
        if temp_bool:
            temp_valute = [RUB.amount, USD.amount, EUR.amount, USD.rate, EUR.rate]
            logger.info(print_valute())
            #logger.handlers[0].flush()
            #sys.stdout.flush()

            print('flush was here')
        await asyncio.sleep(60)


async def sleep_for_timeout(timeout):
    while True:
        task = asyncio.create_task(get_valute())
        await asyncio.sleep(timeout)


async def get_valute():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL)
        try:
            media = json.loads(html)
            USD.rate = media['Valute'][USD.name]['Value']
            EUR.rate = media['Valute'][EUR.name]['Value']
        except Exception:
            logger.exception("bad data in response")


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            logger.info('request responded successfully')
        return await response.text()


if __name__ == '__main__':
    print('hello')
    args = parser.parse_args()
    if args.debug in ('1', 1, 'true', True, 'y', 'Y'):
        logger.setLevel(logging.DEBUG)

    elif args.debug in ('0', 0, 'false', False, 'n', 'N'):
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    logger.critical('it seems to be loaded')
    timeout = args.period
    RUB = Val('RUB', args.rub, 1)
    USD = Val('USD', args.usd, 75)
    EUR = Val('EUR', args.eur, 85)

    app = web.Application()
    handler = Handler()
    app.add_routes([web.get('/usd/get', handler.get_usd),
                    web.get('/rub/get', handler.get_rub),
                    web.get('/eur/get', handler.get_eur),
                    web.get('/amount/get', handler.get_amount),
                    web.post('/amount/set', handler.post_amount_set),
                    web.post('/modify', handler.post_modify)])

    ioloop = asyncio.get_event_loop()

    runner = web.AppRunner(app)
    ioloop.run_until_complete(runner.setup())
    site = web.TCPSite(runner)
    ioloop.run_until_complete(site.start())

    ioloop.create_task(sleep_for_timeout(timeout))
    ioloop.create_task(print_somewhat())
    try:
        ioloop.run_forever()
    except KeyboardInterrupt:
        pass
    ioloop.close()
