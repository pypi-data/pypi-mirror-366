import typer

app = typer.Typer()

@app.command()
def main():
    typer.echo("🧬 bioai-seq CLI ready!")

if __name__ == "__main__":
    app()