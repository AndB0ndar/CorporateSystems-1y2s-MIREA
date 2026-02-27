import asyncio
import logging

from pathlib import Path

from .handler import handle_client


async def run_server(host: str, port: int, upload_dir: str, result_file: str):
    """Start the server with the given parameters."""
    logger = logging.getLogger("server")

    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {upload_dir}")
    logger.info(f"Result file: {result_file}")

    async def client_connected(reader, writer):
        await handle_client(reader, writer, upload_dir, result_file)

    server = await asyncio.start_server(client_connected, host, port)
    logger.info(f"Server started on {host}:{port}")
    async with server:
        await server.serve_forever()


