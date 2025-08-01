import typer

from e621_content_collector.downloader.download import run_download

tool = typer.Typer()
tool.command()(run_download)

if __name__ == "__main__":
    tool()