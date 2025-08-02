import argparse

from . import comandos
from .config import *

descricao = f"{NOME}: estrutura de front-end para Flask. Versão: {VERSAO}"

def criar_flask():
    comandos.criar_flask()

def main():
    parser = argparse.ArgumentParser(description=descricao)
    subparsers = parser.add_subparsers(dest='comando')

    flask = subparsers.add_parser(
        'flask',
        help=f'Cria a estrutura padrão para app de Flask. Inclui o comando de instalação'
    )

    args = parser.parse_args()
    match args.comando:
        case 'flask': criar_flask()
        case _: parser.print_help()

if __name__ == "__main__":
    main()
    