# 💰 Controle de Finanças Pessoais

App web em Python (Streamlit) para controlar receitas, despesas e orçamento
mensal, com gráficos e backup em CSV/Excel.

## O que o app faz

- **Painel**: resumo do mês (receitas, despesas, saldo), gráfico de pizza por
  categoria e evolução dos últimos 6 meses.
- **Lançamentos**: cadastrar, editar e excluir receitas/despesas, com data,
  categoria, forma de pagamento e status.
- **Orçamento**: definir um limite mensal por categoria e comparar com o
  gasto real.
- **Categorias**: personalizar as categorias de receita/despesa.
- **Exportar**: baixar backup em CSV/Excel e importar lançamentos de um CSV.

Os dados ficam num arquivo local `financas.db` (SQLite) — não é enviado a
nenhum servidor externo além de onde você hospedar o app.

---

## 1) Rodar no seu computador

Pré-requisito: [Python 3.10+](https://www.python.org/downloads/) instalado.

```bash
# 1. Entre na pasta do projeto
cd finance-app

# 2. (Recomendado) crie um ambiente virtual
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o app
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

---

## 2) Publicar de graça na internet (Streamlit Community Cloud)

Essa é a forma mais simples de ter um link público e gratuito para o app.
Limites do plano gratuito (2026): ~1 GB de RAM, o app "dorme" após 12h sem
acesso (acorda sozinho no próximo acesso, em alguns segundos), apps públicos
ilimitados (só 1 app privado), sem domínio próprio. Mais que suficiente para
uso pessoal.

### Passo a passo

1. **Crie uma conta gratuita no GitHub**: https://github.com/signup (se
   ainda não tiver).
2. **Crie um repositório novo** (pode ser público ou privado) e envie esta
   pasta `finance-app` para ele. O jeito mais fácil, sem usar linha de
   comando, é:
   - No GitHub, clique em **New repository**, dê um nome (ex:
     `minhas-financas`), e crie.
   - Na página do repositório, clique em **Add file → Upload files** e
     arraste todos os arquivos e pastas desta pasta (`app.py`, `db.py`,
     `common.py`, `requirements.txt`, `.streamlit/`, `pages/`).
   - Clique em **Commit changes**.
3. **Crie uma conta gratuita no Streamlit Community Cloud**:
   https://share.streamlit.io — entre com sua conta do GitHub.
4. Clique em **Create app / New app**, escolha o repositório que você
   acabou de criar, o branch `main` e o arquivo principal `app.py`.
5. Clique em **Deploy**. Em 1–2 minutos seu app estará no ar com um link
   como `https://seu-usuario-minhas-financas.streamlit.app`.

Pronto — esse link pode ser acessado de qualquer navegador, celular incluso,
de graça.

### ⚠️ Sobre a persistência dos dados na nuvem

O SQLite grava num arquivo dentro do próprio servidor gratuito. Isso
funciona bem no dia a dia, mas **não é um banco de dados permanente
garantido**: se você atualizar o código (novo `git push`) ou a Streamlit
Cloud reiniciar o contêiner por manutenção, o arquivo pode ser resetado.
Por isso o app tem a página **Exportar**, pensada exatamente para isso:

- Baixe um backup em CSV ou Excel sempre que fizer lançamentos importantes.
- Se os dados forem resetados, use **Importar lançamentos de um CSV** na
  mesma página para trazer tudo de volta.

Se no futuro você quiser um banco 100% permanente (ex: usar de vários
dispositivos com sincronia garantida), a evolução natural é trocar o SQLite
por um banco gratuito na nuvem, como o Postgres grátis do
[Supabase](https://supabase.com) — posso te ajudar a fazer essa migração
quando quiser.

---

## 3) Estrutura dos arquivos

```
finance-app/
├── app.py                       # Painel principal (Dashboard)
├── common.py                    # Barra lateral e seletor de período (compartilhado)
├── db.py                        # Toda a lógica de banco de dados (SQLite)
├── requirements.txt             # Dependências para instalar/hospedar
├── .streamlit/config.toml       # Tema visual
└── pages/
    ├── 1_📝_Lançamentos.py       # Cadastrar/editar/excluir transações
    ├── 2_💰_Orçamento.py         # Orçamento mensal por categoria
    ├── 3_🏷️_Categorias.py        # Gerenciar categorias
    └── 4_📤_Exportar.py          # Backup CSV/Excel + importação
```

## 4) Personalizar

- **Categorias padrão**: edite a lista `CATEGORIAS_PADRAO` em `db.py` (só
  vale para uma instalação nova, sem banco ainda; categorias já existentes
  você edita pela própria página **Categorias** do app).
- **Cores/tema**: edite `.streamlit/config.toml`.
- **Formas de pagamento**: edite a lista `FORMAS_PAGAMENTO` em `db.py`.
