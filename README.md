# Django Bounty Hunter

**Integrantes:** Alisson Felipe e Kevin Aparecido

## Tema

Painel de caçador de recompensas inspirado no clima "velho oeste" de
Django Livre. 4 models interligados — `Bando`, `Procurado`, `Cartaz` e
`Cacador` — e um **dashboard** que cruza os quatro com agregações do ORM
(soma, contagem agrupada, top N, últimas baixas), em vez de só listar
registros crus.

`Python 3.10+` `Django <6.0` `Pillow` `SQLite` `projeto: core` `app: recompensas`

## Modelagem

```
Bando (1) ───< (N) Procurado (1) ───< (N) Cartaz (N) >─── (1) Cacador
```

| Model | Campo | Tipo | Descrição |
|---|---|---|---|
| **Bando** | `nome` | CharField | Nome da gangue |
| | `area_atuacao` | CharField | Região onde atua |
| **Procurado** | `nome` | CharField | Nome do foragido |
| | `apelido` | CharField | Opcional |
| | `nivel_periculosidade` | IntegerField (choices 1–5) | Baixo → Lenda |
| | `bando` | FK → Bando | Opcional (nem todo foragido tem gangue) |
| | `foto` | ImageField | Opcional |
| **Cartaz** | `procurado` | FK → Procurado | 1 procurado pode ter vários cartazes |
| | `valor_recompensa` | DecimalField | Em US$ |
| | `data_emissao` | DateField (automático) | |
| | `status` | CharField (choices) | Ativo / Capturado / Abatido |
| | `cacador` | FK → Cacador | Preenchido só quando resolvido |
| **Cacador** | `nome` | CharField | |
| | `reputacao` | PositiveIntegerField | Pontos acumulados |

Vem com dados fictícios de exemplo já carregados (3 bandos, 2 caçadores,
5 procurados, 6 cartazes em status variados) pra o dashboard não começar
vazio.

> O CRUD completo (criar/editar/excluir) pros 4 models novos ainda não
> existe — por enquanto, o cadastro de dados é feito pelo `/admin/`.

## Rodando o projeto

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata dados_exemplo
python manage.py runserver
```

- `http://127.0.0.1:8000/` — dashboard (painel do xerife)
- `http://127.0.0.1:8000/admin/` — painel administrativo (cadastro dos 4 models)

Para acessar o `/admin/`, crie um superusuário:

```powershell
python manage.py createsuperuser
```

## Recriar o banco do zero

```powershell
del db.sqlite3
python manage.py migrate
python manage.py loaddata dados_exemplo
```

## Estrutura

```
manage.py
core/settings.py, core/urls.py       ← projeto
recompensas/
  models.py, views.py, urls.py, admin.py
  fixtures/dados_exemplo.json
  templates/recompensas/base.html, dashboard.html
```
