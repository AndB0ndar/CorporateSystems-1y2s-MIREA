import os
import time
import struct
import logging
import asyncio


async def read_request(reader: asyncio.StreamReader):
    # 1. Read filename length (4 bytes)
    name_len_data = await reader.readexactly(4)
    name_len = struct.unpack("!I", name_len_data)[0]

    # 2. Read filename
    filename_bytes = await reader.readexactly(name_len)
    filename = filename_bytes.decode("utf-8")

    # 3. Read content length (8 bytes)
    content_len_data = await reader.readexactly(8)
    content_len = struct.unpack("!Q", content_len_data)[0]

    # 4. Read file content
    content = await reader.readexactly(content_len)

    return filename, content


def analyze_text(text: str) -> tuple[int, int, int]:
    lines = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
    words = len(text.split())
    chars = len(text)
    return lines, words, chars


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    upload_dir: str,
    result_file: str,
):
    """
    Handle a single client connection:
    receive file, analyze, save results, and respond.
    """
    peername = writer.get_extra_info("peername")
    logger = logging.getLogger(':'.join(map(str, peername)))
    logger.info(f"Client connected")

    try:
        filename, file_content = await read_request(reader)

        saved_path = os.path.join(upload_dir, saved_filename(filename))
        with open(saved_path, "wb") as f:
            f.write(file_content)
        logger.debug(f"File saved as {saved_path}")

        text = file_content.decode("utf-8", errors="replace")
        lines, words, chars = analyze_text(text)

        # Append analysis result to the result file
        result_line = (
            f"{saved_filename}: "
            f"lines={lines}, words={words}, characters={chars}\n"
        )
        with open(result_file, "a", encoding="utf-8") as res_f:
            res_f.write(result_line)
        logger.info(f"Result for {filename} written to {result_file}")

        # Send response to client
        response = (
            f"File name: {filename}\n"
            f"Lines: {lines}, Words: {words}, Chars: {chars}\n"
        )
        writer.write(response.encode("utf-8"))
        await writer.drain()

        logger.info(f"Processed file {filename}")

    except (
        asyncio.IncompleteReadError, ConnectionResetError, struct.error
    ) as e:
        logger.error(f"Error receiving data from {peername}: {e}")
        try:
            writer.write(f"Server error: {e}".encode("utf-8"))
            await writer.drain()
        except:
            pass

    except Exception as e:
        logger.exception(f"Unexpected error handling {peername}: {e}")

    finally:
        writer.close()
        await writer.wait_closed()
        logger.debug(f"Connection with {peername} closed")


def saved_filename(filename: str) -> str:
    """Generates a unique file name based on the source and timestamp."""
    base, ext = os.path.splitext(filename)
    timestamp = int(time.time() * 1000)
    return f"{base}_{timestamp}{ext}"


