from pathlib import Path

from ..config import *


def criar_pasta(pasta):
    pasta = Path(pasta)

    if not pasta.exists():
        pasta.mkdir()
        print(f'Pasta {COR_AMARELO}{pasta}{COR_FIM} criada')

def copiar_arquivo(origem, destino):
    arquivo_origem = PASTA_ORIGEM / origem
    conteudo = Path.read_text(arquivo_origem)

    arquivo_final = Path(destino)
    if arquivo_final.exists():
        print(
            f'Arquivo {COR_VERMELHO}{destino}{COR_FIM} já existe e não foi recriado')
    else:
        arquivo_final.write_text(conteudo, encoding='utf-8')
        print(f'Arquivo {COR_AMARELO}{destino}{COR_FIM} criado')

def copiar_pasta_inteira(origem, destino):
    pasta_origem = PASTA_ORIGEM / origem
    arquivos = list(pasta_origem.glob('*'))

    for arquivo in arquivos:
        copiar_arquivo(
            f"{origem}/{str(arquivo.name)}", 
            f'{destino}/{str(arquivo.name)}')


