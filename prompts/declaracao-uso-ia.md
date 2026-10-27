# Declaração de Uso de IA

**Nome:** Ricardo Machado
**Data:** 27/10/2026

## Ferramenta

Claude Code (Anthropic), usado no terminal dentro do repositório, com a skill `developing-with-streamlit` instalada pelo `streamlit skills`.

## Como a IA foi usada

Usei a IA como assistente de execução, em etapas curtas. Eu defini o escopo, as regras do repositório e a ordem do trabalho. A IA lia os arquivos, propunha cada etapa e preparava as alterações.

## Prompts usados

Os prompts abaixo resumem, em formato estruturado, os pedidos que fiz em cada etapa.

### Prompt 1: instalar as skills do Streamlit

- **Objetivo:** instalar as Agent Skills do Streamlit no projeto.
- **Contexto:** slide 19 da Aula 21 e a documentação oficial (`docs.streamlit.io/develop/api-reference/cli/skills`).
- **Pedido:** rodar `streamlit skills` na raiz do repositório e confirmar onde os `SKILL.md` foram criados.
- **Resultado:** a skill foi instalada. No meu Windows, sem symlinks, ela ficou na pasta do usuário.

### Prompt 2: planejar a entrega da Aula 21

- **Objetivo:** montar um roteiro passo a passo de tudo o que a Aula 21 pede.
- **Contexto:** o PDF da Aula 21, o meu EDA da Aula 11, o `README.md` e o `ROTEIRO.md`.
- **Restrições:**
  - Commits só na `main` do meu fork.
  - A entrega dividida em 2 a 5 commits.
- **Formato de saída:** um roteiro com os arquivos e a verificação de cada commit, sem implementar nada ainda.
- **Resultado:** um roteiro em 5 commits, que eu revisei antes de começar.

### Prompt 3: definir como executar o roteiro

- **Objetivo:** responder às dúvidas do roteiro e definir o fluxo de trabalho.
- **Decisões que passei à IA:**
  - Fazer uma etapa por vez, parando antes de cada commit para eu revisar e aprovar.
  - Adiantar na Aula 21 os gráficos do Dashboard 1, que o modelo da professora já trazia.
  - Fazer o rascunho do layout em formato digital.
  - Citar a ferramenta na declaração de uso de IA.

### Prompt 4: exportar os dados (commit 2)

- **Objetivo:** gerar o dataset tratado em `data/clean/`.
- **Restrições:**
  - Usar o `eda-com-downloads.ipynb` como base, conforme o ROTEIRO.
  - Manter o `eda.ipynb` 100% original.
- **Correção pedida:** a IA apontou uma divergência no texto da EDA (181 registros removidos, quando o código remove 167). Pedi que a correção fosse feita apenas no notebook alterado.

### Prompt 5: rascunho e prompt do esqueleto (commit 3)

- **Objetivo:** produzir o rascunho do Dashboard 1 e preencher o template de prompt.
- **Entrada:** o layout pedido na aula (sidebar com filtros, correlação e distribuição) e as colunas do meu dataset.
- **Prompt do esqueleto:** [layout-skeleton-prompt.md](layout-skeleton-prompt.md), com o rascunho [entregas/rascunho-dashboard1.png](../entregas/rascunho-dashboard1.png).

### Prompt 6: adaptar o app (commit 4)

- **Objetivo:** adaptar o `app.py` do modelo ao meu dataset de reservas de hotel.
- **Restrições:**
  - Pelo menos 1 seletor de variáveis e 1 slider de intervalo.
  - Dados carregados por `src/data_loader.py`.
  - Testar os casos de borda antes do commit.
- **Resultado:** revisei o app rodando localmente e o print antes de aprovar.

## O que foi aceito, modificado ou rejeitado e por quê

### Decisões tomadas por mim

- Usar a EDA de reservas de hotel da Aula 11 como base. Mantive o `eda.ipynb` sem alterações e limitei as mudanças ao `eda-com-downloads.ipynb`.
- Fazer commits só na `main`, em etapas curtas e com a minha revisão antes de cada commit.
- Dividir a entrega em 5 commits, depois de revisar o roteiro proposto.
- Adiantar os gráficos do Dashboard 1 na Aula 21.
- Aceitar o rascunho em formato digital, já que o exemplo da professora também é digital.
- Corrigir o número de registros removidos (181 para 167) só no notebook alterado.

### Sugestões da IA que aceitei após revisar

- Exportar o bruto para `data/raw/` (fora do git) e o tratado para `data/clean/`, seguindo o README.
- Abrir o app com 5 variáveis pré-selecionadas (`lead_time`, `adr`, `stays_in_week_nights`, `stays_in_weekend_nights`, `total_of_special_requests`). Nas outras, quase todas as reservas têm valor 0.
- Agregar os histogramas no pandas, porque o Altair não aceita as 87 mil linhas direto.
- Usar `@st.cache_data` no `load_data` e as cores da minha EDA no tema e nos gráficos.

### Modificado

- O rascunho do Dashboard 1 é um wireframe digital, e não um desenho à mão.
- O texto do `eda-com-downloads.ipynb` foi corrigido para os números que o código de fato produz.

### Rejeitado

- Versionar as pastas `.claude/skills/` e `.agents/skills/`. O README define que cada pessoa roda `streamlit skills` no próprio clone, então apaguei a branch dessa tentativa e as skills ficaram só na minha máquina.

## Aula 22 — Streamlit, parte 2

### Prompt 7: planejar a entrega da Aula 22

- **Objetivo:** montar o roteiro de tudo o que a Aula 22 pede, no mesmo formato da Aula 21.
- **Contexto:** o PDF da Aula 22, o meu EDA, o `README.md`, o `ROTEIRO.md` e o `ALTAIR-CROSSFILTER.md`.
- **Restrições:**
  - Commits só na `main`, de 3 a 4 etapas, com revisão antes de cada commit.
  - Sem implementar nada antes de eu aprovar o roteiro.
- **Formato de saída:** um roteiro com os arquivos e a verificação de cada commit, mais uma proposta de público, KPIs, widgets e visuais para o Dashboard 2.
- **Resultado:** um roteiro em 4 commits, que eu aprovei junto com a proposta do Dashboard 2.

### Prompt 8: identidade visual e abas (commit 1)

- **Objetivo:** aplicar a identidade visual em `.streamlit/config.toml` e separar os dashboards com `st.tabs`.
- **Entrada:** duas opções de paleta derivadas das cores da minha EDA.
- **Decisão:** escolhi a opção B (coral `#E76F51` sobre fundos quentes, ligada ao tema hotelaria e cancelamento).

### Prompt 9: métricas, justificativa e rascunho (commit 2)

- **Objetivo:** testar os KPIs em notebook antes do app (slide 15), escrever a justificativa e desenhar o rascunho do Dashboard 2.
- **Restrições:** os 6 campos do modelo para cada métrica e de 3 a 5 KPIs (slides 13 e 14).
- **Resultado:** [notebooks/metricas-dashboard2.ipynb](../notebooks/metricas-dashboard2.ipynb), [entregas/justificativa-metricas.md](../entregas/justificativa-metricas.md) e [entregas/rascunho-dashboard2.png](../entregas/rascunho-dashboard2.png).

### Prompt 10: implementar o Dashboard 2 (commit 3)

- **Objetivo:** levar os KPIs para o `app.py` com `st.metric` e visuais em Altair.
- **Restrições:**
  - Widgets definidos antes do código (hotel, ano de chegada e segmento de mercado).
  - Seleção cruzada conforme o exemplo 3 do `ALTAIR-CROSSFILTER.md` (`on_select`).
  - Testar filtros que esvaziam os dados e o Dashboard 1 de novo antes do commit.
- **Resultado:** revisei o app rodando localmente e o print com a seleção antes de aprovar.

### Decisões tomadas por mim

- Aprovar o tema (impacto dos cancelamentos), o público-alvo (gerência de reservas e de receita) e os 4 KPIs: taxa de cancelamento, receita perdida estimada, antecedência mediana e tarifa média das não canceladas.
- Aprovar os widgets (hotel, ano de chegada e segmento) e os dois visuais (barras por faixa de antecedência e linha por mês).
- Escolher a paleta B entre as duas opções de identidade visual.
- Dividir a entrega em 4 commits e revisar cada um antes de aprovar.

### Sugestões da IA que aceitei após revisar

- Deixar os filtros do Dashboard 2 numa barra no topo da aba, já que a sidebar é do Dashboard 1.
- Mostrar a diferença em pontos percentuais da taxa de cancelamento quando uma faixa é clicada, e "—" nos KPIs quando um grupo fica vazio.
- Trocar o título geral do app para "Painel de Reservas de Hotel", que vale para as duas abas.
- Usar a mediana na antecedência, por causa da assimetria de `lead_time` vista na EDA.

### Modificado

- O rascunho do Dashboard 2 também é um wireframe digital, no mesmo estilo do Dashboard 1.
