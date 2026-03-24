# Analise de Dados - LH Nautical

Projeto de analise de dados de vendas para a empresa LH Nautical, abrangendo exploracao de dados, normalizacao, modelagem financeira, segmentacao de clientes, previsao de demanda e sistema de recomendacao.

---

## Estrutura do Projeto

```
lh_nautical/
├── README.md
├── RESPOSTAS.md                           # RESPOSTAS PRONTAS PARA SUBMISSAO
├── .gitignore
├── datasets/                              # Dados originais
│   ├── vendas_2023_2024.csv               # Transacoes de vendas (9.895 registros)
│   ├── produtos_raw.csv                   # Catalogo de produtos (157 registros, 150 unicos)
│   ├── custos_importacao.json             # Historico de custos em USD (150 produtos)
│   └── clientes_crm.json                 # Cadastro de clientes (49 clientes)
├── notebooks/                             # Analises (1 por questao)
│   ├── 01_eda.ipynb                       # Questao 1: Analise Exploratoria
│   ├── 02_normalizacao_produtos.ipynb     # Questao 2: Normalizacao de Produtos
│   ├── 03_custos_importacao.ipynb         # Questao 3: Estruturacao de Custos
│   ├── 04_analise_prejuizo.ipynb          # Questao 4: Analise de Prejuizo
│   ├── 05_clientes_fieis.ipynb            # Questao 5: Clientes Fieis
│   ├── 06_dimensao_calendario.ipynb       # Questao 6: Dimensao de Calendario
│   ├── 07_previsao_demanda.ipynb          # Questao 7: Previsao de Demanda
│   └── 08_sistema_recomendacao.ipynb      # Questao 8: Sistema de Recomendacao
├── scripts/
│   ├── __init__.py
│   └── utils.py                           # Funcoes auxiliares reutilizaveis
└── outputs/
    ├── graficos/                          # Visualizacoes geradas
    ├── relatorios/
    └── dados_processados/                 # CSVs intermediarios
```

---

## Pre-requisitos

```bash
pip install pandas numpy scikit-learn matplotlib requests
```

Para executar os notebooks:
```bash
cd lh_nautical
jupyter notebook
```

Os notebooks devem ser executados na ordem numerica (01 a 08), pois alguns dependem de outputs anteriores.

---

## Resumo das Questoes e Principais Resultados

### Questao 1 - Analise Exploratoria (EDA)

**Notebook:** `01_eda.ipynb`

Avaliacao da confiabilidade do dataset `vendas_2023_2024.csv` para tomada de decisao.

| Metrica                   | Valor              |
|---------------------------|--------------------|
| Total de linhas           | 9.895              |
| Total de colunas          | 6                  |
| Periodo analisado         | 01/01/2023 a 31/12/2024 (730 dias) |
| Valor minimo (total)      | R$ 294,50          |
| Valor maximo (total)      | R$ 2.222.973,00    |
| Valor medio (total)       | R$ 263.797,83      |
| Valores nulos             | 0                  |
| Duplicatas                | 0                  |
| Outliers (metodo IQR)     | 1.018 (10,3%)      |

**Diagnostico:** O dataset esta pronto para analises. Nao apresenta valores nulos, duplicatas ou inconsistencias criticas. Os outliers identificados representam transacoes legitimas de alto valor (produtos de propulsao com quantidades elevadas). A distribuicao e assimetrica a direita, o que e esperado para dados de vendas. As datas possuem dois formatos distintos (YYYY-MM-DD e DD-MM-YYYY), mas foram convertidas com sucesso.

---

### Questao 2 - Normalizacao de Produtos

**Notebook:** `02_normalizacao_produtos.ipynb`

Padronizacao do catalogo de produtos a partir de `produtos_raw.csv`.

**Processo:**
1. **Categorias:** 39 variacoes de escrita mapeadas para 3 categorias padrao (eletronicos, propulsao, ancoragem) utilizando remocao de acentos, espacos e correspondencia por substring
2. **Precos:** Conversao de texto ("R$ 33122.52") para tipo numerico (float)
3. **Duplicatas:** Remocao de registros duplicados pela coluna `code`

| Metrica                     | Valor |
|-----------------------------|-------|
| Registros originais         | 157   |
| Registros finais            | 150   |
| **Duplicatas removidas**    | **7** |
| Categorias padronizadas     | 3     |

---

### Questao 3 - Custos de Importacao

**Notebook:** `03_custos_importacao.ipynb`

Transformacao do arquivo JSON aninhado em um CSV plano para facilitar analises.

**Estrutura de saida:**

| Coluna       | Tipo    | Descricao                   |
|--------------|---------|-----------------------------|
| product_id   | integer | Identificador do produto    |
| product_name | text    | Nome do produto             |
| category     | text    | Categoria padronizada       |
| start_date   | date    | Data de inicio da vigencia  |
| usd_price    | float   | Preco unitario em USD       |

| Metrica                          | Valor  |
|----------------------------------|--------|
| Produtos no JSON                 | 150    |
| **Total de entradas no CSV**     | **1.260** |

---

### Questao 4 - Analise de Prejuizo

**Notebook:** `04_analise_prejuizo.ipynb`

Identificacao de vendas realizadas abaixo do custo, cruzando valores em BRL (vendas) com custos em USD (importacao) e taxa de cambio diaria.

**Metodologia:**
- Taxa de cambio: media da cotacao de venda PTAX (Banco Central), obtida via API publica
- Custo em BRL por transacao: `custo_usd * taxa_cambio * quantidade`
- Prejuizo: diferenca positiva entre custo total e receita da venda
- Para dias sem cotacao (fins de semana/feriados): utilizada a cotacao do ultimo dia util anterior
- Associacao de custos: merge temporal retroativo (custo vigente na data da venda)

**Resultados:**
- Produto com maior prejuizo absoluto: id_product = 72 (R$ 39.821.041,68)
- Produto com maior percentual de perda: id_product = 72 (63,15%)
- O produto com maior prejuizo absoluto tambem possui o maior percentual de perda: **Sim**

---

### Questao 5 - Clientes Fieis

**Notebook:** `05_clientes_fieis.ipynb`

Identificacao dos 10 clientes com maior ticket medio entre aqueles que compraram em 3 ou mais categorias distintas.

**Definicoes:**
- Faturamento Total = soma da coluna `total` por cliente
- Frequencia = contagem de transacoes distintas por cliente
- Ticket Medio = Faturamento Total / Frequencia
- Diversidade = quantidade de categorias distintas compradas
- Desempate: id_client em ordem crescente

**Resultados:**

| Ranking | id_client | Ticket Medio   | Categorias |
|---------|-----------|----------------|------------|
| 1       | 47        | R$ 336.859,70  | 3          |
| 2       | 42        | R$ 325.168,33  | 3          |
| 3       | 9         | R$ 306.370,90  | 3          |
| 4       | 22        | R$ 300.916,16  | 3          |
| 5       | 2         | R$ 298.422,42  | 3          |
| 6       | 28        | R$ 298.170,77  | 3          |
| 7       | 46        | R$ 297.119,77  | 3          |
| 8       | 38        | R$ 292.786,31  | 3          |
| 9       | 36        | R$ 292.051,34  | 3          |
| 10      | 5         | R$ 290.063,38  | 3          |

**Categoria mais vendida (Top 10):** propulsao (6.030 itens)

---

### Questao 6 - Dimensao de Calendario

**Notebook:** `06_dimensao_calendario.ipynb`

Correcao do calculo de media de vendas por dia da semana, incluindo dias sem nenhuma venda registrada.

**Problema:** Um GROUP BY direto na tabela de vendas ignora dias em que a loja abriu mas nao vendeu nada, inflando a media.

**Solucao:** Criar uma dimensao de datas (calendario completo) e fazer LEFT JOIN com as vendas, preenchendo dias sem venda com R$ 0,00.

**Resultados:**

| Dia da Semana   | Total de Dias | Media de Vendas     |
|-----------------|---------------|---------------------|
| Domingo         | 105           | R$ 3.319.503,57     |
| Segunda-feira   | 105           | R$ 3.465.137,71     |
| Quarta-feira    | 104           | R$ 3.535.265,63     |
| Quinta-feira    | 104           | R$ 3.626.232,44     |
| Terca-feira     | 105           | R$ 3.627.045,76     |
| Sabado          | 104           | R$ 3.710.540,55     |
| Sexta-feira     | 104           | R$ 3.715.003,41     |

**Dia com menor media:** Domingo (R$ 3.319.503,57)

---

### Questao 7 - Previsao de Demanda

**Notebook:** `07_previsao_demanda.ipynb`

Modelo baseline de previsao diaria para o produto "Motor de Popa Yamaha Evo Dash 155HP" (id_product = 54).

**Configuracao:**
- Treino: ate 31/12/2023
- Teste: janeiro de 2024
- Modelo: media movel dos ultimos 7 dias
- Metrica: MAE (Mean Absolute Error)

**Resultados:**

| Metrica                                  | Valor    |
|------------------------------------------|----------|
| Dias de treino                           | 365      |
| Dias de teste                            | 31       |
| Dias com venda (treino)                  | ~28      |
| MAE                                      | ~1,00    |
| Soma previsao semana 1 (01-07/jan)       | **0**    |

**Avaliacao:** O baseline nao e adequado para este produto. O "Motor de Popa Yamaha Evo Dash 155HP" apresenta demanda intermitente (poucas vendas distribuidas em muitos dias). A media movel de 7 dias retorna zero na maioria dos casos, pois a janela raramente contem vendas. Para produtos com demanda intermitente, metodos como Croston seriam mais apropriados.

---

### Questao 8 - Sistema de Recomendacao

**Notebook:** `08_sistema_recomendacao.ipynb`

Motor de recomendacao baseado em similaridade de cosseno para o produto "GPS Garmin Vortex Mare Drift" (id_product = 27).

**Metodologia:**
1. Matriz binaria usuario-produto (49 clientes x 150 produtos)
2. Similaridade de cosseno entre vetores de produtos
3. Ranking dos 5 produtos mais similares

**Top 5 produtos similares:**

| Ranking | id_product | Similaridade |
|---------|------------|--------------|
| 1       | **94**     | 0,8696       |
| 2       | 11         | 0,8680       |
| 3       | 35         | 0,8539       |
| 4       | 115        | 0,8500       |
| 5       | 1          | 0,8500       |

**Produto com maior similaridade:** id_product = 94

---

## Respostas Consolidadas (Validacoes)

Todas as respostas, textos de interpretacao e codigos SQL estao no arquivo **[RESPOSTAS.md](RESPOSTAS.md)**, pronto para copiar e colar na plataforma de submissao.

| Questao | Pergunta | Resposta |
|---------|----------|----------|
| 1.2     | Valor maximo da coluna "total" | R$ 2.222.973,00 |
| 2.2     | Duplicatas removidas | 7 |
| 3.2     | Entradas apos normalizacao | 1.260 |
| 4.2     | Produto com maior % de perda | id_product = 72 (63,15%) |
| 5.2     | Categoria mais vendida (Top 10) | propulsao (6.030 itens) |
| 6.2     | Dia com menor media de vendas | Domingo (R$ 3.319.503,57) |
| 7.2     | Soma previsao semana 1 | 0 |
| 8.2     | Produto mais similar ao GPS | id_product = 94 |

---

## Tecnologias Utilizadas

- **Python 3** (pandas, numpy, matplotlib, scikit-learn, requests)
- **API Banco Central** (PTAX - cotacoes de cambio)
- **Jupyter Notebook** (ambiente de desenvolvimento)

---

## Observacoes Tecnicas

1. **Formato de datas:** O dataset de vendas possui datas em dois formatos (YYYY-MM-DD e DD-MM-YYYY). Todos os notebooks tratam essa inconsistencia automaticamente.

2. **Categorias de produtos:** O catalogo original contem 39 variacoes de escrita para 3 categorias. A normalizacao utiliza remocao de acentos e correspondencia por substring para classificacao robusta.

3. **Taxa de cambio:** Obtida da API publica do Banco Central (PTAX). Para dias sem cotacao, aplica-se forward fill (ultima cotacao disponivel).

4. **SQL de referencia:** Cada notebook que envolve consultas SQL inclui o codigo SQL equivalente em celulas markdown, pronto para ser utilizado em outras plataformas.
