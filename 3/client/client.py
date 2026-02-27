import os
import click
import struct
import logging
import asyncio


logger = logging.getLogger("client")


async def send_request(
    writer: asyncio.StreamWriter, filename: str, file_content: str
):
    # Send filename length (4 bytes)
    name_len = len(filename.encode("utf-8"))
    writer.write(struct.pack("!I", name_len))

    # Send filename
    writer.write(filename.encode("utf-8"))

    # Send content length (8 bytes)
    content_len = len(file_content)
    writer.write(struct.pack("!Q", content_len))

    # Send file content
    writer.write(file_content)
    await writer.drain()
    logger.debug(f"File {filename} sent, waiting for response...")


async def send_file(host: str, port: int, filepath: str):
    """Connect to the server and send the specified file."""
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist.")
        return

    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_content = f.read()

    try:
        reader, writer = await asyncio.open_connection(host, port)
    except Exception as e:
        logger.error(f"Could not connect to server {host}:{port}: {e}")
        return

    try:
        await send_request(writer, filename, file_content)

        # Receive server response
        response = await reader.read(4096)
        print("Server response:")
        print(response.decode("utf-8"))

    except Exception as e:
        logger.error(f"Error during communication: {e}")

    finally:
        writer.close()
        await writer.wait_closed()
        logger.debug("Connection closed")


def setup_logging(level):
    """Configure logging with the given level."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s [%(levelname)s] %(message)s'
    )


@click.command()
@click.argument(
    'filepath',
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '--host',
    default='127.0.0.1',
    show_default=True,
    help='Server address'
)
@click.option(
    '--port',
    default=8888,
    show_default=True,
    help='Server port'
)
@click.option(
    '--log-level',
    default='INFO',
    show_default=True,
    type=click.Choice(
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        case_sensitive=False
    ),
    help='Logging level'
)
def main(filepath, host, port, log_level):
    """Send a file to the analysis server and display the result."""
    setup_logging(log_level)
    asyncio.run(send_file(host, port, filepath))


if __name__ == '__main__':
    main()

