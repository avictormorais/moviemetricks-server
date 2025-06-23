# moviemetricks-server

Este projeto é um servidor backend para o MovieMetricks, uma aplicação de gerenciamento e recomendação de filmes, séries e playlists. Ele fornece uma API RESTful para manipulação de usuários, pessoas, comentários, notificações, playlists e integração com a API do TMDB.

## Funcionalidades
- Cadastro e autenticação de usuários
- Gerenciamento de pessoas (atores, diretores, etc.)
- Criação e manipulação de playlists
- Comentários em mídias
- Notificações para usuários
- Integração com a API do TMDB para informações de filmes e séries

## Estrutura do Projeto
```
app.py                # Arquivo principal da aplicação
requirements.txt      # Dependências do projeto
vercel.json           # Configuração para deploy no Vercel
assets/               # Arquivos HTML estáticos
controller/           # Lógica dos controladores das rotas
middleware/           # Middlewares para autenticação e outras funções
models/               # Modelos das entidades do sistema
routes/               # Definição das rotas da API
```

## Requisitos
- Python 3.12+
- (Opcional) Conta no TMDB para integração

## Instalação
1. Clone o repositório:
   ```sh
   git clone https://github.com/seu-usuario/moviemetricks-server.git
   cd moviemetricks-server
   ```
2. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente no arquivo `.env` (exemplo: chaves de API, configurações do banco de dados).

## Executando o servidor
```sh
python app.py
```
O servidor estará disponível em `http://localhost:5000` (ou porta configurada).

## Deploy
Este projeto pode ser facilmente implantado no Vercel usando o arquivo `vercel.json`.

