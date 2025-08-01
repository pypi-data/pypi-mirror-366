import os

import click

from name2gender import Name2Gender, load_model, download_model
from name2gender.model import __CACHE_DIR__


@click.group()
@click.version_option(version='0.0.4.alpha')
def main():
    ...


@main.command()
@click.argument('name', required=True)
@click.option('--threshold', '-t', default=.5, type=float, help='threshold for prediction')
@click.option('--model', '-m', default='small', type=str, help='name2gender model')
def predict(name: str, threshold: float, model: str):
    n2g = Name2Gender(load_model(model_name=model))
    gender, prob = n2g(name=name, return_probability=True, threshold=threshold)
    click.echo(f'"{name}" is <{gender.value.upper()}> with a probability of {prob * 100:.2f}%.')


@main.command()
@click.argument('model', default='name2gender-small', required=True)
def install(model: str):
    try:
        download_model(model_name=model)
        click.echo(f'Successfully installed model "{model}".')
    except FileNotFoundError as e:
        print(e)


@main.command()
@click.argument('model', required=True)
def uninstall(model: str):
    path = os.path.join(__CACHE_DIR__, model)
    if os.path.exists(path):
        os.remove(path)
        click.echo(f'Model \"{model}\" is uninstalled.')
    click.echo(f"Model \"{model}\" doesn't exists.")
