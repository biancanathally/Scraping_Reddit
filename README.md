# Reddit Scraper 🐍🤖

Este projeto é um web scraper automatizado desenvolvido em Python para extrair tópicos e discussões relevantes de subreddits específicos. Ele identifica palavras-chave relacionadas ao desenvolvimento e organiza os dados em formatos estruturados para análise posterior.

## 🚀 Funcionalidades

* **Extração seletiva**: Filtra títulos de posts baseados em palavras-chave.
* **Múltiplos formatos de saída**: Salva os dados automaticamente em `JSON` (para persistência de objetos) e `CSV` (para análise em planilhas ou Data Science).
* **Tratamento de erros**: Sistema robusto para lidar com falhas de conexão ou mudanças na estrutura do HTML.
* **Gestão de caminhos**: Utiliza a biblioteca `pathlib` para garantir que os arquivos sejam salvos corretamente em qualquer sistema operacional (macOS, Windows ou Linux).

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Requests**: Para realizar requisições HTTP de forma eficiente.
* **BeautifulSoup4**: Para o parsing e extração de dados do HTML.
* **Pathlib**: Para manipulação inteligente de diretórios.

## 📋 Pré-requisitos

Antes de rodar o script, você precisará instalar as dependências:

```bash
pip install requests beautifulsoup4
```

## 🔧 Como Usar

1. Clone este repositório ou baixe o arquivo `main.py`.
2. Abra o terminal na pasta do projeto.
3. Execute o script:

```bash
python3 main.py
```

Os arquivos `python_topics.json` e `python_topics.csv` serão gerados automaticamente na mesma pasta do script.

## 📊 Estrutura dos Dados

O scraper organiza as informações da seguinte forma:

* **Subreddit**: Origem do dado.
* **Type**: Categoria (se é um tópico principal ou uma discussão/comentário).
* **Title**: O texto extraído do post.
* **URL**: Link direto para a discussão (quando disponível).
* **Scraped_at**: Timestamp exato da coleta.

## ⚠️ Notas legais e éticas

Este projeto foi desenvolvido para fins acadêmicos e de estudo (Mestrado). Ao utilizá-lo, respeite os [Termos de Serviço do Reddit](https://www.redditinc.com/policies/data-api-terms) e utilize intervalos de tempo entre as requisições (`time.sleep`) para evitar sobrecarga nos servidores.
