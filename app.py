import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Correlação e Distribuição das Reservas de Hotel",
    layout="wide",
)

st.title("Correlação e Distribuição das Reservas de Hotel")

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
    st.header("Filtros")

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

st.caption(f"{len(df_filtrado):,} de {len(df):,} reservas dentro dos intervalos escolhidos.".replace(",", "."))

# Dashboard 1: correlação (heatmap) à esquerda, distribuição (histograma) à direita
col_correlacao, col_distribuicao = st.columns([1, 1.5])

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

# TODO: Dashboard 2 — KPIs (Aula 22)
