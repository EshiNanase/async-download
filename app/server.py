import aiohttp.web_exceptions
from aiohttp import web
import asyncio
import aiofiles
import os
import logging
import argparse

INTERVAL_SECS = 1
CHUNK_SIZE = 102400


async def handle_archive_page(request):
    archive_hash = request.match_info['archive_hash']

    photos_path = app.args.folder
    files_path = os.path.join(photos_path, archive_hash)

    if not os.path.exists(files_path):
        raise aiohttp.web_exceptions.HTTPNotFound(text='Файл не найден или был удален!')

    process = await asyncio.create_subprocess_exec(
        'zip', '-r', '-', '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=files_path
    )

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename="photos.zip"'

    await response.prepare(request)

    try:
        while not process.stdout.at_eof():
            chunk = await process.stdout.read(n=CHUNK_SIZE)
            logging.info('Отправляю чанк...')
            await response.write(chunk)
            if app.args.delay:
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        logging.info('Загрузка отменена :(')
        raise

    finally:
        if not process.returncode:
            process.kill()
            await process.communicate()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r', encoding='utf-8') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()

    parser = argparse.ArgumentParser(
        prog='Фоткоскачиватель',
        description='Скачивает фотки',
        epilog='Фоткачивает скачки')
    parser.add_argument('-l', '--logging', action='store_true', help='включить/выключить логирование')
    parser.add_argument('-d', '--delay', action='store_true', help='включить/выключить задержку скачивания')
    parser.add_argument('-f', '--folder', action='append', help='указать директорию')
    app.args = parser.parse_args()

    if app.args.logging:
        logging.basicConfig(level=logging.INFO)

    if not app.args.folder:
        app.args.folder = 'test_photos'

    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', handle_archive_page),
    ])
    web.run_app(app)
