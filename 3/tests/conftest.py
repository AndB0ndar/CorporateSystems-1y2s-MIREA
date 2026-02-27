import asyncio
import logging
import pytest_asyncio

from server.core import run_server


logging.disable(logging.CRITICAL)


@pytest_asyncio.fixture
async def server_fixture(unused_tcp_port_factory, tmp_path):
    """
    Starts the server on a random port
    and returns a tuple (host, port, upload_dir, result_file).
    The server stops automatically after the test is completed.
    """
    host = "127.0.0.1"
    port = unused_tcp_port_factory()
    upload_dir = tmp_path / "uploads"
    result_file = tmp_path / "analysis_result.txt"

    server_task = asyncio.create_task(
        run_server(
            host=host,
            port=port,
            upload_dir=str(upload_dir),
            result_file=str(result_file),
        )
    )

    await asyncio.sleep(0.1)

    yield host, port, upload_dir, result_file

    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
