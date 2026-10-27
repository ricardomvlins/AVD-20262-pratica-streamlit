# Justificativa das métricas — Dashboard 2

**Tema:** impacto dos cancelamentos nas reservas de hotel.
**Público-alvo:** gerência de reservas e de receita do hotel (City Hotel e Resort Hotel).
**Base:** `data/clean/dataset.csv` (87.229 reservas). Os cálculos foram testados em [`notebooks/metricas-dashboard2.ipynb`](../notebooks/metricas-dashboard2.ipynb). No app, todas as métricas são recalculadas com os filtros de hotel, ano de chegada e segmento de mercado, e com a faixa de antecedência clicada no gráfico de barras.

## Métrica 1: Taxa de cancelamento
- **Variável:** `status_reserva` (Cancelada ou Não cancelada).
- **O que mede:** a proporção de reservas canceladas sobre o total de reservas do recorte. No dataset inteiro, é 27,5% (City Hotel 30,1%, Resort Hotel 23,5%).
- **Por que foi escolhida:** é o indicador central do tema e responde à pergunta da EDA sobre o que diferencia reservas canceladas de não canceladas.
- **Público-alvo:** gerência de reservas.
- **Qual decisão pode ser apoiada por essa métrica?** Em quais hotéis, segmentos ou períodos apertar a política de cancelamento ou aumentar o overbooking.
- **O que comunica ao público-alvo:** "de cada 100 reservas, cerca de 27 não se concretizam", sem exigir leitura de tabela ou de gráfico.

## Métrica 2: Receita perdida estimada
- **Variáveis:** `adr` (tarifa média diária) × noites (`stays_in_week_nights` + `stays_in_weekend_nights`), somado só nas reservas canceladas.
- **O que mede:** quanto as reservas canceladas teriam gerado se tivessem se concretizado. No dataset inteiro, são cerca de 11,5 milhões, o que equivale a 33% do valor total reservado. O dataset não informa a moeda, então o valor aparece sem símbolo.
- **Por que foi escolhida:** traduz a taxa de cancelamento em dinheiro, que é a linguagem da gerência de receita.
- **Público-alvo:** gerência de receita.
- **Qual decisão pode ser apoiada por essa métrica?** Quanto vale investir para reduzir cancelamentos, por exemplo em depósito antecipado, lembretes ou tarifas não reembolsáveis.
- **O que comunica ao público-alvo:** o tamanho do problema em valor. É uma estimativa e não considera multas ou depósitos retidos.

## Métrica 3: Antecedência mediana das reservas canceladas × não canceladas
- **Variável:** `lead_time` (dias entre a reserva e a chegada).
- **O que mede:** a mediana de dias de antecedência em cada grupo. No dataset inteiro, são 80 dias nas canceladas e 38 nas não canceladas. A mediana foi usada porque `lead_time` tem assimetria forte à direita (EDA, princípio distribucional).
- **Por que foi escolhida:** a ECDF da EDA mostrou que as canceladas são feitas com mais antecedência. O gráfico de barras confirma: a taxa sobe de 8,4% (0 a 7 dias) para 39,7% (mais de 180 dias).
- **Público-alvo:** gerência de reservas.
- **Qual decisão pode ser apoiada por essa métrica?** A partir de quantos dias de antecedência exigir depósito ou uma confirmação extra.
- **O que comunica ao público-alvo:** "quem cancela costuma reservar com o dobro da antecedência de quem vem".

## Métrica 4: Tarifa média diária das reservas não canceladas
- **Variável:** `adr`, só nas reservas não canceladas.
- **O que mede:** o valor médio por diária das reservas que se concretizam. No dataset inteiro, é cerca de 102 (City Hotel 108,6, Resort Hotel 93,0).
- **Por que foi escolhida:** dá a referência de preço do recorte filtrado e ajuda a ler a receita perdida (um recorte pode perder mais porque cancela mais ou porque cobra mais caro).
- **Público-alvo:** gerência de receita.
- **Qual decisão pode ser apoiada por essa métrica?** Revisar tarifas em segmentos ou períodos com tarifa acima ou abaixo da média geral.
- **O que comunica ao público-alvo:** quanto vale, em média, uma diária efetivamente vendida no recorte escolhido.
