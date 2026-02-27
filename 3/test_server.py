import os
import asyncio
import logging
import tempfile

import pytest

import client


@pytest.mark.asyncio
async def test_multiple_clients(server_fixture):
    """Simultaneous sending of two files by different clients."""
    host, port, upload_dir, result_file = server_fixture

    content1 = "Line1\nLine2\n"
    content2 = "Single line file."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f2:
        f1.write(content1)
        f2.write(content2)
        path1, path2 = f1.name, f2.name

    try:
        await asyncio.gather(
            client.send_file(host, port, path1, logging.getLogger("test")),
            client.send_file(host, port, path2, logging.getLogger("test"))
        )

        with open(result_file, "r", encoding="utf-8") as res_f:
            all_results = res_f.readlines()
        assert len(all_results) == 2

    finally:
        os.unlink(path1)
        os.unlink(path2)


@pytest.mark.asyncio
async def test_invalid_protocol(server_fixture):
    """
    Sending incorrect data (not over the protocol)
    to check the server's error handling.
    """
    host, port, _, _ = server_fixture

    reader, writer = await asyncio.open_connection(host, port)

    writer.write(b"garbage")
    await writer.drain()

    await asyncio.sleep(0.5)
    writer.close()
    await writer.wait_closed()

    assert True


@pytest.mark.asyncio
async def test_server_continues_after_error(server_fixture):
    """
    After an erroneous connection,
    the server must continue to process new ones.
    """
    host, port, upload_dir, result_file = server_fixture

    reader, writer = await asyncio.open_connection(host, port)
    writer.write(b"trash")
    await writer.drain()
    writer.close()
    await writer.wait_closed()

    content = "Valid content"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        tmp_path = f.name

    try:
        await client.send_file(host, port, tmp_path, logging.getLogger("test"))

        saved_files = list(upload_dir.glob("*.txt"))
        assert len(saved_files) == 1
        with open(result_file, "r", encoding="utf-8") as res_f:
            lines = res_f.readlines()
        assert len(lines) == 1

    finally:
        os.unlink(tmp_path)

