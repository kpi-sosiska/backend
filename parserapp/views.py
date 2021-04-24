import os

# from django_async_stream import AsyncStreamingHttpResponse
from .parser import parser


async def parse(req):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    async def parse_():
        async for i, cnt in parser.main():
            yield f'Обработано: {i:> 4}/{cnt}<br>'
    # todo check async queue

    return AsyncStreamingHttpResponse(parse_())
