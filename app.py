import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Painel de Reservas de Hotel",
    layout="wide",
)

st.title("Painel de Reservas de Hotel")

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = [
    "lead_time",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "booking_changes",
    "days_in_waiting_list",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
]

# Seleção inicial: as variáveis com mais variação (nas demais, quase todas as reservas têm valor 0)
VARS_PADRAO = [
    "lead_time",
    "adr",
    "stays_in_week_nights",
    "stays_in_weekend_nights",
    "total_of_special_requests",
]

# Sidebar: filtros (variáveis + intervalo)
with st.sidebar:
    st.header("Filtros do Dashboard 1")

    variaveis = st.multiselect(
        "Variáveis Quantitativas",
        options=VARS_QUANT,
        default=VARS_PADRAO,
        help="Selecione as variáveis quantitativas que deseja analisar no dashboard.",
    )

    separar_por_status = st.toggle(
        "Distinguir por Status",
        value=False,
        help="Colore a distribuição pelo status da reserva (status_reserva: Não cancelada ou Cancelada).",
    )

    # Um slider de intervalo para cada variável selecionada
    intervalos = {}
    for var in variaveis:
        # children é float no CSV (por causa dos ausentes tratados na EDA), mas só tem valores inteiros
        if (df[var] % 1 == 0).all():
            minimo, maximo, passo = int(df[var].min()), int(df[var].max()), 1
        else:
            minimo, maximo, passo = float(df[var].min()), float(df[var].max()), 0.1
        intervalos[var] = st.slider(
            f"Intervalo de {var}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            key=f"intervalo_{var}",
        )

# Mantém só as reservas dentro de todos os intervalos escolhidos
df_filtrado = df
for var, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim)]

# Cores da EDA: azul para a distribuição geral, verde-azulado e coral para os status
COR_HISTOGRAMA = "#5271A3"
COR_NAO_CANCELADA = "#2A9D8F"
COR_CANCELADA = "#E76F51"
CORES_STATUS = alt.Scale(
    domain=["Não cancelada", "Cancelada"], range=[COR_NAO_CANCELADA, COR_CANCELADA]
)

# Legenda dos status em texto, para caber no espaço livre da grade de histogramas
LEGENDA_STATUS = (
    f"**Status**  \n"
    f":color[■]{{foreground=\"{COR_NAO_CANCELADA}\"}} Não cancelada  \n"
    f":color[■]{{foreground=\"{COR_CANCELADA}\"}} Cancelada"
)


def histograma_agregado(dados, var, separar):
    """Conta as reservas por faixa no pandas: o Altair recebe ~20 linhas em vez de dezenas de milhares."""
    # Até 20 faixas de mesma largura (menos quando a variável tem poucos valores distintos)
    bordas = np.histogram_bin_edges(dados[var], bins=20 if dados[var].nunique() > 20 else dados[var].nunique())
    faixa = pd.cut(dados[var], bordas, include_lowest=True)
    grupos = [faixa, "status_reserva"] if separar else [faixa]
    contagem = dados.groupby(grupos, observed=True).size().rename("reservas").reset_index()
    contagem["inicio"] = contagem[var].map(lambda intervalo: intervalo.left)
    contagem["fim"] = contagem[var].map(lambda intervalo: intervalo.right)
    return contagem.drop(columns=var)


# Dashboard 2: faixas de antecedência (lead_time agrupado) e meses de chegada, na ordem do calendário
FAIXAS_ANTECEDENCIA = [-1, 7, 30, 90, 180, np.inf]
ROTULOS_ANTECEDENCIA = ["0–7 dias", "8–30 dias", "31–90 dias", "91–180 dias", "> 180 dias"]
MESES = {
    "January": "Jan", "February": "Fev", "March": "Mar", "April": "Abr", "May": "Mai", "June": "Jun",
    "July": "Jul", "August": "Ago", "September": "Set", "October": "Out", "November": "Nov", "December": "Dez",
}


def numero_br(valor, casas=1):
    """Formata com vírgula decimal e ponto de milhar (ex.: 11.484,0)."""
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def valor_curto(valor):
    """Resume valores grandes para caber no cartão de KPI (ex.: 11,5 mi)."""
    if valor >= 1_000_000:
        return f"{numero_br(valor / 1_000_000)} mi"
    if valor >= 1_000:
        return f"{numero_br(valor / 1_000)} mil"
    return numero_br(valor, 0)


def kpis(dados):
    """As 4 métricas da justificativa (entregas/justificativa-metricas.md), testadas em notebooks/metricas-dashboard2.ipynb."""
    cancelada = dados["status_reserva"].eq("Cancelada")
    noites = dados["stays_in_week_nights"] + dados["stays_in_weekend_nights"]
    return {
        "taxa": cancelada.mean(),
        "receita_perdida": (dados["adr"] * noites)[cancelada].sum(),
        "lead_canceladas": dados.loc[cancelada, "lead_time"].median(),
        "lead_nao_canceladas": dados.loc[~cancelada, "lead_time"].median(),
        "adr_nao_canceladas": dados.loc[~cancelada, "adr"].mean(),
    }


def dias(valor):
    # Recorte só com canceladas (ou só com não canceladas) deixa a mediana do outro grupo vazia
    return "—" if pd.isna(valor) else f"{valor:.0f}"


aba_dashboard1, aba_dashboard2 = st.tabs(["Dashboard 1: Correlação e Distribuição", "Dashboard 2: KPIs"])

with aba_dashboard1:
    st.caption(f"{len(df_filtrado):,} de {len(df):,} reservas dentro dos intervalos escolhidos.".replace(",", "."))

    # Dashboard 1: correlação (heatmap) à esquerda, distribuição (histograma) à direita
    col_correlacao, col_distribuicao = st.columns([1, 1.5])

    with col_correlacao:
        st.subheader("Correlação (Spearman)")

        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
        elif len(df_filtrado) < 30:
            st.warning("Poucas reservas nos intervalos escolhidos para calcular a correlação.")
        else:
            # Matriz de correlação de Spearman das variáveis selecionadas, em formato longo (uma linha por célula)
            corr = (
                df_filtrado[variaveis]
                .corr(method="spearman")
                .rename_axis(index="var_y", columns="var_x")
                .stack(future_stack=True)
                .rename("correlacao")
                .reset_index()
            )
            # Só o triângulo inferior, sem a diagonal (sempre 1): a matriz é simétrica, o resto é repetição
            ordem = {var: i for i, var in enumerate(variaveis)}
            corr = corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]

            base = alt.Chart(corr).encode(
                x=alt.X(
                    "var_x:N",
                    title=None,
                    sort=variaveis[:-1],  # a última variável só aparece nas linhas
                    axis=alt.Axis(labelAngle=-30, labelFontSize=12, labelLimit=220),
                ),
                y=alt.Y("var_y:N", title=None, sort=variaveis[1:], axis=alt.Axis(labelFontSize=12, labelLimit=220)),  # a primeira só nas colunas
            )
            heatmap = base.mark_rect().encode(
                color=alt.Color(
                    "correlacao:Q",
                    title="Spearman",
                    scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
                    legend=alt.Legend(titleFontSize=14, labelFontSize=13),
                ),
                tooltip=["var_x", "var_y", alt.Tooltip("correlacao:Q", format=".2f")],
            )
            valores = base.mark_text(fontSize=14).encode(
                text=alt.Text("correlacao:Q", format=".2f"),
                color=alt.condition(
                    "abs(datum.correlacao) > 0.5", alt.value("white"), alt.value("black")
                ),
            )

            st.altair_chart(
                (heatmap + valores).properties(height=380),
                width="stretch",
                alt="Mapa de calor (triângulo inferior, sem a diagonal) da correlação de Spearman entre as variáveis quantitativas selecionadas",
            )

    with col_distribuicao:
        st.subheader("Distribuição")

        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma reserva dentro dos intervalos escolhidos.")
        else:
            # Com número par de variáveis não sobra espaço na grade: a legenda vai acima dela
            if separar_por_status and len(variaveis) % 2 == 0:
                st.markdown(LEGENDA_STATUS)

            # Um histograma por variável selecionada, em grade de 2 colunas (cada um com a sua escala)
            for inicio in range(0, len(variaveis), 2):
                colunas = st.columns(2)
                for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                    histograma = (
                        alt.Chart(histograma_agregado(df_filtrado, var, separar_por_status))
                        .mark_bar()
                        .encode(
                            x=alt.X("inicio:Q", bin="binned", title=var),  # faixas já calculadas no pandas
                            x2="fim:Q",
                            y=alt.Y("reservas:Q", title="Reservas"),
                            tooltip=[
                                alt.Tooltip("inicio:Q", title="De"),
                                alt.Tooltip("fim:Q", title="Até"),
                                alt.Tooltip("reservas:Q", title="Reservas"),
                            ],
                        )
                        .properties(height=200)
                    )
                    if separar_por_status:
                        histograma = histograma.encode(
                            color=alt.Color(
                                "status_reserva:N",
                                title="Status",
                                scale=CORES_STATUS,
                                legend=None,
                            ),
                            tooltip=[
                                "status_reserva",
                                alt.Tooltip("inicio:Q", title="De"),
                                alt.Tooltip("fim:Q", title="Até"),
                                alt.Tooltip("reservas:Q", title="Reservas"),
                            ],
                        )
                    else:
                        histograma = histograma.mark_bar(color=COR_HISTOGRAMA)

                    with coluna:
                        st.altair_chart(histograma, width="stretch", alt=f"Histograma da variável {var}")

                # Número ímpar de variáveis: a legenda ocupa o espaço que sobrou na última linha
                if separar_por_status and len(colunas) == 2 and len(variaveis[inicio : inicio + 2]) == 1:
                    colunas[1].markdown(LEGENDA_STATUS)

with aba_dashboard2:
    # Filtros do Dashboard 2 numa barra no topo da aba (a sidebar é do Dashboard 1)
    col_hotel, col_ano, col_segmento = st.columns([1, 1, 1.4])
    with col_hotel:
        hoteis = st.pills(
            "Hotel",
            options=["City Hotel", "Resort Hotel"],
            selection_mode="multi",
            default=["City Hotel", "Resort Hotel"],
        )
    with col_ano:
        anos = sorted(df["arrival_date_year"].unique())
        ano_inicio, ano_fim = st.select_slider(
            "Ano de chegada", options=anos, value=(anos[0], anos[-1])
        )
    with col_segmento:
        segmentos_ordem = df["market_segment"].value_counts().index.tolist()
        segmentos = st.multiselect(
            "Segmento de mercado",
            options=segmentos_ordem,
            default=segmentos_ordem,
            help="Canal pelo qual a reserva foi feita (ex.: Online TA = agência de viagens online).",
        )

    df_kpi = df[
        df["hotel"].isin(hoteis)
        & df["arrival_date_year"].between(ano_inicio, ano_fim)
        & df["market_segment"].isin(segmentos)
    ].assign(
        faixa_antecedencia=lambda d: pd.cut(d["lead_time"], FAIXAS_ANTECEDENCIA, labels=ROTULOS_ANTECEDENCIA),
        cancelada=lambda d: d["status_reserva"].eq("Cancelada"),
    )

    if df_kpi.empty:
        st.warning("Nenhuma reserva com esses filtros. Selecione pelo menos um hotel e um segmento.")
    else:
        kpis_container = st.container()

        # Barras: taxa de cancelamento por faixa de antecedência (sempre do recorte inteiro, para comparar as faixas)
        por_faixa = (
            df_kpi.groupby("faixa_antecedencia", observed=True)["cancelada"]
            .agg(reservas="size", taxa="mean")
            .reset_index()
        )
        taxa_recorte = df_kpi["cancelada"].mean()

        clique = alt.selection_point(name="faixa", fields=["faixa_antecedencia"])
        barras = (
            alt.Chart(por_faixa)
            .mark_bar(color=COR_CANCELADA)
            .encode(
                x=alt.X("faixa_antecedencia:N", sort=ROTULOS_ANTECEDENCIA, title="Antecedência da reserva",
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("taxa:Q", title="Taxa de cancelamento", axis=alt.Axis(format=".0%")),
                opacity=alt.condition(clique, alt.value(1), alt.value(0.35)),
                tooltip=[
                    alt.Tooltip("faixa_antecedencia:N", title="Faixa"),
                    alt.Tooltip("taxa:Q", title="Taxa", format=".1%"),
                    alt.Tooltip("reservas:Q", title="Reservas", format=","),
                ],
            )
            .add_params(clique)
        )
        linha_geral = (
            alt.Chart(pd.DataFrame({"taxa": [taxa_recorte]}))
            .mark_rule(color="gray", strokeDash=[4, 4])
            .encode(y="taxa:Q")
        )

        # A seleção da faixa volta para o Python e recalcula os KPIs e a linha por mês
        col_barras, col_linha = st.columns(2)
        with col_barras:
            st.subheader("Cancelamento por antecedência")
            evento = st.altair_chart(
                (barras + linha_geral).properties(height=300),
                key="barras_antecedencia",
                on_select="rerun",
                width="stretch",
            )
            st.caption("Clique numa faixa para recalcular os KPIs e a linha por mês (shift + clique seleciona mais de uma). "
                       "A linha tracejada é a taxa do recorte.")

        faixas_clicadas = [item["faixa_antecedencia"] for item in evento.selection.get("faixa", [])]
        df_selecao = df_kpi[df_kpi["faixa_antecedencia"].isin(faixas_clicadas)] if faixas_clicadas else df_kpi

        # Linha: taxa de cancelamento por mês de chegada
        por_mes = (
            df_selecao.groupby("arrival_date_month")["cancelada"]
            .agg(reservas="size", taxa="mean")
            .reindex(list(MESES))
            .dropna()
            .rename(index=MESES)
            .rename_axis("mes")
            .reset_index()
        )
        with col_linha:
            st.subheader("Cancelamento por mês")
            linha = (
                alt.Chart(por_mes)
                .mark_line(point=alt.OverlayMarkDef(color=COR_CANCELADA), color=COR_CANCELADA)
                .encode(
                    x=alt.X("mes:N", sort=list(MESES.values()), title="Mês de chegada", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("taxa:Q", title="Taxa de cancelamento", axis=alt.Axis(format=".0%")),
                    tooltip=[
                        alt.Tooltip("mes:N", title="Mês"),
                        alt.Tooltip("taxa:Q", title="Taxa", format=".1%"),
                        alt.Tooltip("reservas:Q", title="Reservas", format=","),
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(linha, width="stretch")

        # KPIs acima dos gráficos (container reservado antes, preenchido depois da seleção)
        with kpis_container:
            selecao = kpis(df_selecao)
            recorte = kpis(df_kpi)
            descricao = ", ".join(faixas_clicadas) if faixas_clicadas else "todas as faixas de antecedência"
            st.caption(f"{numero_br(len(df_selecao), 0)} reservas no recorte ({descricao}).")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(
                "Taxa de cancelamento",
                f"{numero_br(selecao['taxa'] * 100)}%",
                # Com faixa clicada, compara com o recorte inteiro (subir é ruim, por isso a cor invertida)
                delta=f"{numero_br((selecao['taxa'] - recorte['taxa']) * 100)} p.p." if faixas_clicadas else None,
                delta_color="inverse",
                border=True,
            )
            col2.metric(
                "Receita perdida estimada",
                valor_curto(selecao["receita_perdida"]),
                help="Tarifa média diária (adr) × noites das reservas canceladas. O dataset não informa a moeda.",
                border=True,
            )
            col3.metric(
                "Antecedência mediana (dias)",
                f"{dias(selecao['lead_canceladas'])} × {dias(selecao['lead_nao_canceladas'])}",
                help="Canceladas × não canceladas.",
                border=True,
            )
            col4.metric(
                "Tarifa média (não canceladas)",
                "—" if pd.isna(selecao["adr_nao_canceladas"]) else numero_br(selecao["adr_nao_canceladas"]),
                help="Média de adr das reservas que se concretizaram.",
                border=True,
            )
