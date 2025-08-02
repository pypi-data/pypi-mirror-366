from pathlib import Path

from ..config import *
from .helpers import criar_pasta, copiar_arquivo, copiar_pasta_inteira

def criar_flask():
    criar_pasta('app')
    criar_pasta('app/templates')
    criar_pasta('app/static')
    
    criar_requirements()
    copiar_arquivo('rodar.py', 'rodar.py')
    copiar_pasta_inteira('app', 'app')
    copiar_pasta_inteira('templates', 'app/templates')


def criar_requirements():
    arquivo = 'requirements.txt'
    arquivo_origem = PASTA_ORIGEM / arquivo
    conteudo = Path.read_text(arquivo_origem)
    conteudo += f'{APP}=={VERSAO}'

    arquivo_final = Path(arquivo)
    if arquivo_final.exists():
        print(
            f'Arquivo {COR_VERMELHO}{arquivo}{COR_FIM} já existe, não foi criado')
    else:
        arquivo_final.write_text(conteudo, encoding='utf-8')
        print(f'Arquivo {COR_AMARELO}{arquivo}{COR_FIM} criado')
