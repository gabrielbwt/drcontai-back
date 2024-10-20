Este é o backend desenvolvido para o projeto modelo realizado para a StartUp Dr. Contaí. 

Para esse projeto, utilizou-se FastsAPI, SQLAlchemy, Alembic e PostgreSQL.

## Configurando o ambiente

Crie um arquivo .env na raiz do projeto com as variáveis de ambiente necessárias:

```bash
ENVIRONMENT=development
PLUGGY_CLIENT_ID=
PLUGGY_CLIENT_SECRET=
DATABASE_URL=
```

## Instale as dependências

Primeiramente, instale as dependências do projeto:

Pode ser utilizando o Makefile:

```bash
make install
```

Ou utilizando o comando:

```bash
pip install -r requirements.txt
```

## Iniciando o projeto

Em seguida, inicie o server de desenvolvimento:

Pode ser utilizando o Makefile:

```bash
make start
```

Ou utilizando o comando:

```bash
uvicorn app.main:app --reload
```

Por fim, o servidor estará respondendo requisições em [http://localhost:8000](http://localhost:8000).