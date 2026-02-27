import os
import asyncio
import logging
import tempfile

import pytest

import client


@pytest.mark.asyncio
async def test_send_file(server_fixture):
    """Sending the file to the server and checking the results."""
    host, port, upload_dir, result_file = server_fixture

    content = "Hello world\nThis is a test file.\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        tmp_path = f.name

    try:
        await client.send_file(host, port, tmp_path)

        saved_files = list(upload_dir.glob("*.txt"))
        assert len(saved_files) > 0

        assert result_file.exists()
        with open(result_file, "r", encoding="utf-8") as res_f:
            lines = res_f.readlines()
        assert len(lines) > 0

        last_line = lines[-1]
        assert "lines=2" in last_line
        assert "words=7" in last_line
        assert "characters=33" in last_line

    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_nonexistent_file(server_fixture, caplog):
    """An attempt to send a non-existent file."""
    host, port, _, _ = server_fixture
    caplog.set_level(logging.ERROR)

    await client.send_file(host, port, "nonexistent_file_123.txt")

    assert any("does not exist" in record.message for record in caplog.records)

