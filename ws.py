# -*- coding: utf-8 -*-
#!/usr/bin/python3.5

from aiohttp import web
import sqlalchemy as sa
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
    async with create_engine(dsn) as engine:
        async with engine.acquire() as conn:
            await conn.execute(tbl.insert().values(slovo=val, ch_g=len([i for i in val if i in g]),
                                                   ch_s=len([i for i in val if i in s])))
            query = (sa.select([sa.func.sum(tbl.c.ch_g), sa.func.sum(tbl.c.ch_s)]).select_from(tbl))
            async for i in conn.execute(query):
                sum_list = i
    return web.Response(text='Current: Vowels: %s, Consonants: %s \n '
                             'Total: Vowels: %s, Consonants: %s' %
                             (len([i for i in val if i in g]), len([i for i in val if i in s]),
                              sum_list[0], sum_list[1]))


if __name__ == "__main__":
    app = web.Application()
    app.router.add_route('GET', '/', handler)
    web.run_app(app)

