import click
import logging
import asyncio

from . import run_server


def setup_logging(level):
    """Configure logging with the given level."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s | %(name)s | [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.command()
@click.option(
    '--host',
    default='127.0.0.1',
    show_default=True,
    help='Host to listen on')
@click.option(
    '--port',
    default=8888,
    show_default=True,
    help='Port to listen on')
@click.option(
    '--upload-dir',
    default='uploads',
    show_default=True,
    help='Directory to store received files')
@click.option(
    '--result-file',
    default='analysis_result.txt',
    show_default=True,
    help='File to append analysis results')
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
def main(host, port, upload_dir, result_file, log_level):
    """Launch the text file analysis server."""
    setup_logging(log_level)
    asyncio.run(run_server(host, port, upload_dir, result_file))


if __name__ == '__main__':
    main()

