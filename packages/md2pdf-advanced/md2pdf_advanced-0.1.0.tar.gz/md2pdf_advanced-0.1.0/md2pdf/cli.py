import typer
from .converter import convert_markdown
from .gui import launch_gui

app = typer.Typer()

@app.command()
def convert(file: str, style: str = "default", summarize: bool = False):
    convert_markdown(file, style=style, summarize=summarize)

@app.command()
def gui():
    launch_gui()

if __name__ == "__main__":
    app()