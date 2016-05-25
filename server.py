# -*- coding: utf-8 -*-
#!/usr/bin/python3.5

import asyncio
import sqlalchemy as sa
from aiohttp import web
from aiopg.sa import create_engine

metadata = sa.MetaData()
tbl = sa.Table('abc', metadata,
               sa.Column('key', sa.Integer, primary_key=True),
               sa.Column('slovo', sa.Text),
               sa.Column('ch_g', sa.Integer),
               sa.Column('ch_s', sa.Integer))

dsn = 'dbname=pg_abc user=postgres password=123 host=127.0.0.1'
g = 'AEIOU'
s = 'QWRTPSDFGHJKLZXCVBNM'

async def handler(request):
    val = request.GET.get('val', '').upper()
    async with request.app['engine'].acquire() as conn:
        await conn.execute(tbl.insert().values(slovo=val, ch_g=len([i for i in val if i in g]),
                                                   ch_s=len([i for i in val if i in s])))
        query = (sa.select([sa.func.sum(tbl.c.ch_g), sa.func.sum(tbl.c.ch_s)]).select_from(tbl))
        async for i in conn.execute(query):
            sum_list = i
    return web.Response(text='Current: Vowels: %s, Consonants: %s \n Total: Vowels: %s, Consonants: %s'
                             % (len([i for i in val if i in g]), len([i for i in val if i in s]),
                                sum_list[0], sum_list[1]))


async def finish_controller(app):
    print('closing engine')
    engine = app['engine']
    engine.close()
    await engine.wait_closed()


def app(loop=None):
    loop = loop or asyncio.get_event_loop()
    _app = web.Application(loop=loop)
    _app['engine'] = loop.run_until_complete(create_engine(dsn, loop=loop))
    _app.on_cleanup.append(finish_controller)
    _app.router.add_route('GET', '/', handler)
    return _app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    the_app = app(loop)
    handle = the_app.make_handler()
    f = loop.create_server(handle, '0.0.0.0', 8080)
    srv = loop.run_until_complete(f)
    print('serving on', srv.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(handler.finish_connections(1.0))
        loop.run_until_complete(the_app.cleanup())
        loop.close()
