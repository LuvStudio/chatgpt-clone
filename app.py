from json import load

import typer

from ourgpt import app

if __name__ == "__main__":
    config: dict = {}

    with open("config.json", "r") as f:
        config = load(f)
        site_config = config["site_config"]
        app.config["OPENAI_API_KEY"] = config["openai_key"]
        app.config["OPENAI_API_BASE"] = config["openai_api_base"]
        app.config["PROXY"] = config["proxy"]

    if config == {}:
        typer.echo("Config file not found")
        exit(1)

    from ourgpt.chat import bp as chat_bp
    from ourgpt.conversation import bp as conversation_bp

    app.register_blueprint(conversation_bp)
    app.register_blueprint(chat_bp)

    typer.echo(f"Running on port {site_config['port']}")
    app.run(**site_config)
    typer.echo(f"Closing port {site_config['port']}")
