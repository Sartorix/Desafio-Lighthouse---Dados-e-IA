# Respostas - Processo Seletivo LH Nautical

Documento com todas as respostas objetivas, textos de interpretacao e codigos SQL prontos para submissao na plataforma.

---

## Questao 1 - EDA

### 1.1 - Codigo SQL

```sql
SELECT
    COUNT(*) AS total_linhas,
    (SELECT COUNT(*) FROM pragma_table_info('vendas')) AS total_colunas,
    MIN(sale_date) AS data_minima,
    MAX(sale_date) AS data_maxima,
    MIN(total) AS valor_minimo,
    MAX(total) AS valor_maximo,
    ROUND(AVG(total), 2) AS valor_medio
FROM vendas_2023_2024;
```

### 1.2 - Validacao

**Qual e o valor maximo registrado na coluna "total"?**

> R$ 2.222.973,00

### 1.3 - Interpretacao

O dataset `vendas_2023_2024.csv` apresenta 9.895 registros distribuidos ao longo de 730 dias (01/01/2023 a 31/12/2024), abrangendo 6 colunas (id, id_client, id_product, qtd, total, sale_date).

**Outliers na coluna "total":** Pelo metodo IQR (Interquartile Range), foram identificados 1.018 registros (10,3%) acima do limite superior de R$ 813.028,95. Esses valores correspondem a vendas legitimas de produtos de alto valor (principalmente motores de popa) em grandes quantidades. Nao ha evidencia de erros de registro.

**Qualidade dos dados:** Nenhum valor nulo foi encontrado em qualquer coluna. Nao ha registros duplicados nem valores negativos. A unica inconsistencia observada e a coexistencia de dois formatos de data (YYYY-MM-DD e DD-MM-YYYY), que e tratavel programaticamente.

**Conclusao:** O dataset esta pronto para analises futuras sem necessidade de tratamento previo critico. A distribuicao e assimetrica a direita (media R$ 263.797,83 significativamente superior a mediana R$ 82.225,00), o que e esperado em dados de vendas com amplitude de valores entre R$ 294,50 e R$ 2.222.973,00.

---

## Questao 2 - Normalizacao de Produtos

### 2.1 - Codigo Python

Arquivo: `notebooks/02_normalizacao_produtos.ipynb`

### 2.2 - Validacao

**Quantos produtos duplicados foram removidos?**

> 7

---

## Questao 3 - Custos de Importacao

### 3.1 - Codigo Python

Arquivo: `notebooks/03_custos_importacao.ipynb`

### 3.2 - Validacao

**Quantas entradas de importacao o CSV recebeu ao todo apos a normalizacao?**

> 1.260

---

## Questao 4 - Analise de Prejuizo (Dados Publicos)

### 4.1 - Codigo SQL

```sql
WITH custos_aplicaveis AS (
    SELECT
        v.id AS id_venda,
        v.id_product,
        v.qtd,
        v.total AS receita_brl,
        v.sale_date,
        c.usd_price,
        cb.taxa_cambio,
        (c.usd_price * cb.taxa_cambio * v.qtd) AS custo_total_brl,
        CASE
            WHEN v.total < (c.usd_price * cb.taxa_cambio * v.qtd)
            THEN (c.usd_price * cb.taxa_cambio * v.qtd) - v.total
            ELSE 0
        END AS prejuizo
    FROM vendas v
    INNER JOIN custos_importacao c
        ON v.id_product = c.product_id
    INNER JOIN cambio cb
        ON v.sale_date = cb.data
    WHERE c.start_date = (
        SELECT MAX(c2.start_date)
        FROM custos_importacao c2
        WHERE c2.product_id = v.id_product
        AND c2.start_date <= v.sale_date
    )
)
SELECT
    id_product,
    SUM(receita_brl) AS receita_total,
    SUM(prejuizo) AS prejuizo_total,
    ROUND(SUM(prejuizo) / NULLIF(SUM(receita_brl), 0) * 100, 2) AS percentual_perda
FROM custos_aplicaveis
GROUP BY id_product
ORDER BY prejuizo_total DESC;
```

### 4.2 - Validacao

**Qual e o id_produto que apresentou a maior porcentagem de perda financeira relativa?**

> id_product = 72 (percentual de perda: 63,15%)

### 4.3 - Interpretacao

1. **Data de cambio utilizada:** Utilizou-se a media da cotacao de venda PTAX do dia da transacao, obtida da API publica do Banco Central do Brasil. Para dias sem cotacao (fins de semana e feriados), aplicou-se a cotacao do ultimo dia util anterior (forward fill).

2. **Definicao de prejuizo:** Uma transacao e classificada como prejuizo quando o custo total em BRL (custo unitario USD multiplicado pela taxa de cambio do dia e pela quantidade vendida) supera a receita da venda. O prejuizo e calculado como a diferenca positiva entre custo e receita.

3. **Premissas relevantes:** O custo aplicavel a cada venda e determinado pela entrada mais recente do historico de custos com data de inicio anterior ou igual a data da venda (merge temporal retroativo). A analise nao considera impostos, frete ou custos operacionais adicionais, o que pode subestimar o prejuizo real.

---

## Questao 5 - Clientes Fieis

### 5.1 - Codigo SQL

```sql
WITH produtos_limpos AS (
    SELECT
        code AS product_id,
        name,
        CASE
            WHEN LOWER(REPLACE(actual_category, ' ', '')) LIKE '%eletr%'
                THEN 'eletrônicos'
            WHEN LOWER(REPLACE(actual_category, ' ', '')) LIKE '%prop%'
                THEN 'propulsão'
            WHEN LOWER(REPLACE(actual_category, ' ', '')) LIKE '%ancor%'
                OR LOWER(REPLACE(actual_category, ' ', '')) LIKE '%encor%'
                THEN 'ancoragem'
            ELSE LOWER(TRIM(actual_category))
        END AS categoria
    FROM produtos_raw
    GROUP BY code, name, actual_category
),

metricas_cliente AS (
    SELECT
        v.id_client,
        SUM(v.total) AS faturamento_total,
        COUNT(DISTINCT v.id) AS frequencia,
        ROUND(SUM(v.total) / COUNT(DISTINCT v.id), 2) AS ticket_medio,
        COUNT(DISTINCT p.categoria) AS diversidade_categorias
    FROM vendas v
    LEFT JOIN produtos_limpos p ON v.id_product = p.product_id
    GROUP BY v.id_client
    HAVING COUNT(DISTINCT p.categoria) >= 3
),

top_10 AS (
    SELECT id_client
    FROM metricas_cliente
    ORDER BY ticket_medio DESC, id_client ASC
    LIMIT 10
)

SELECT
    p.categoria,
    SUM(v.qtd) AS total_itens
FROM vendas v
INNER JOIN top_10 t ON v.id_client = t.id_client
LEFT JOIN produtos_limpos p ON v.id_product = p.product_id
GROUP BY p.categoria
ORDER BY total_itens DESC;
```

### 5.2 - Validacao

**Qual foi a categoria de produtos mais vendida para os Top 10 (maior quantidade total de itens)?**

> propulsao (6.030 itens)

Top 10 clientes: 47, 42, 9, 22, 2, 28, 46, 38, 36, 5

### 5.3 - Explicacao

1. **Limpeza de categorias:** Removemos todos os espacos internos da string, convertemos para minusculo e removemos acentos e diacriticos. Em seguida, classificamos por correspondencia de substring: se contem "eletr" e mapeado para eletronicos; se contem "prop", para propulsao; se contem "ancor" ou "encor", para ancoragem. Essa abordagem e robusta a variacoes ortograficas, de caixa e de acentuacao.

2. **Filtro de diversidade minima:** Apos a limpeza das categorias, agrupamos as vendas por id_client e contamos o numero de categorias distintas compradas (COUNT DISTINCT). Somente clientes com 3 ou mais categorias distintas foram considerados no ranking.

3. **Contagem restrita aos Top 10:** Primeiro identificamos os 10 clientes com maior ticket medio entre os qualificados. Em seguida, filtramos o dataset de vendas mantendo apenas transacoes desses 10 clientes (INNER JOIN) e, sobre esse subconjunto, calculamos a soma de itens por categoria.

---

## Questao 6 - Dimensao de Calendario

### 6.1 - Codigo SQL

```sql
WITH vendas_tratadas AS (
    SELECT
        CAST(sale_date AS DATE) AS data,
        total AS valor_venda
    FROM vendas
),

dimensao_datas AS (
    SELECT
        data,
        CASE DAYNAME(data)
            WHEN 'Monday' THEN 'Segunda-feira'
            WHEN 'Tuesday' THEN 'Terça-feira'
            WHEN 'Wednesday' THEN 'Quarta-feira'
            WHEN 'Thursday' THEN 'Quinta-feira'
            WHEN 'Friday' THEN 'Sexta-feira'
            WHEN 'Saturday' THEN 'Sábado'
            WHEN 'Sunday' THEN 'Domingo'
        END AS dia_semana
    FROM generate_series(
        (SELECT MIN(data) FROM vendas_tratadas),
        (SELECT MAX(data) FROM vendas_tratadas),
        INTERVAL 1 DAY
    ) AS t(data)
),

vendas_por_dia AS (
    SELECT
        data,
        SUM(valor_venda) AS total_vendas
    FROM vendas_tratadas
    GROUP BY data
)

SELECT
    d.dia_semana,
    COUNT(*) AS total_dias,
    SUM(COALESCE(v.total_vendas, 0)) AS soma_vendas,
    ROUND(AVG(COALESCE(v.total_vendas, 0)), 2) AS media_vendas
FROM dimensao_datas d
LEFT JOIN vendas_por_dia v ON d.data = v.data
GROUP BY d.dia_semana
ORDER BY media_vendas ASC;
```

### 6.2 - Validacao

**Qual dia da semana apresenta a menor media de vendas historica, e qual o valor?**

> Domingo, media de R$ 3.319.503,57

### 6.3 - Explicacao

1. **Por que usar uma tabela de datas:** Ao agrupar diretamente a tabela de vendas por dia da semana, apenas os dias em que ocorreram vendas entram no calculo. Dias em que a loja esteve aberta mas nao registrou nenhuma venda sao ignorados, o que infla a media. A dimensao de datas garante que todos os 731 dias do periodo (incluindo os sem venda) sejam contabilizados com valor zero.

2. **Impacto dos dias sem venda:** Se um dia da semana tiver muitos dias sem venda registrada, a media calculada sem a dimensao sera artificialmente elevada — pois o denominador (quantidade de dias) sera menor que o real. Com a dimensao de datas, esses dias entram no calculo com valor zero, resultando em uma media mais baixa e representativa da realidade operacional.

---

## Questao 7 - Previsao de Demanda

### 7.1 - Codigo Python

Arquivo: `notebooks/07_previsao_demanda.ipynb`

### 7.2 - Validacao

**Soma total da previsao de vendas para a primeira semana de Janeiro 2024 (01/01 a 07/01)?**

> 0 (zero unidades)

### 7.3 - Explicacao

1. **Construcao do baseline:** Para cada dia T de janeiro de 2024, a previsao e calculada como a media aritmetica das vendas reais dos 7 dias anteriores (T-7 a T-1). Um calendario completo foi criado de 01/01/2023 a 31/01/2024, preenchendo dias sem venda com zero para garantir continuidade na janela movel.

2. **Prevencao de data leakage:** O conjunto de treino utiliza exclusivamente dados ate 31/12/2023. A previsao de cada dia T considera apenas valores reais dos dias T-7 a T-1 — nenhum dado do proprio dia T ou de dias futuros entra no calculo. A janela movel e recalculada diariamente.

3. **Limitacao:** O produto "Motor de Popa Yamaha Evo Dash 155HP" apresenta demanda intermitente — registrou vendas em apenas 28 dos 365 dias de treino. A media movel de 7 dias retorna zero na maior parte do tempo, pois a janela raramente contem alguma venda. O modelo nao antecipa a demanda, apenas reage a ela com atraso de ate 7 dias. Para este perfil de demanda esparsa, metodos especificos como o modelo de Croston seriam mais adequados.

---

## Questao 8 - Sistema de Recomendacao

### 8.1 - Codigo Python

Arquivo: `notebooks/08_sistema_recomendacao.ipynb`

### 8.2 - Validacao

**Qual e o id_produto com MAIOR similaridade ao "GPS Garmin Vortex Mare Drift"?**

> id_product = 94 (similaridade: 0,8696)

### 8.3 - Explicacao

1. **Construcao da matriz:** Uma matriz binaria foi construida onde as linhas representam clientes (49) e as colunas representam produtos (150). O valor da celula e 1 se o cliente comprou o produto ao menos uma vez, e 0 caso contrario. A quantidade adquirida foi desconsiderada — apenas a relacao de presenca ou ausencia de compra.

2. **Significado da similaridade de cosseno:** A similaridade de cosseno mede o angulo entre os vetores de dois produtos no espaco dos clientes. Quando dois produtos possuem alta similaridade, significa que eles tendem a ser comprados pelo mesmo conjunto de clientes. Um valor proximo de 1 indica padroes de compra quase identicos; proximo de 0, nenhuma sobreposicao.

3. **Limitacao:** O metodo considera apenas presenca ou ausencia de compra, ignorando quantidade e frequencia. Produtos novos ou com poucas compras possuem vetores esparsos, o que reduz a confiabilidade da similaridade calculada (problema de cold start). Alem disso, o modelo nao incorpora fatores contextuais como sazonalidade, preco ou categoria do produto.
