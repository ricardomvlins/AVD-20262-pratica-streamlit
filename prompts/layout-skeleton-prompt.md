# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

Sou aluno da disciplina Análise e Visualização de Dados (Cesar School, 2026.2) e estou construindo o Dashboard 1 em Streamlit a partir da minha EDA da Aula 11. O dataset é o Hotel Booking Demand (Kaggle, `jessemostipak/hotel-booking-demand`): reservas de um hotel urbano e de um resort, com a variável-alvo `status_reserva` (Cancelada ou Não cancelada). O objetivo do Dashboard 1 é mostrar a correlação e a distribuição das variáveis quantitativas.

Estrutura do repositório: `app.py` na raiz, `src/data_loader.py` com a função `load_data()`, dado tratado em `data/clean/dataset.csv`, notebooks em `notebooks/` e rascunhos em `entregas/`.

## Entrada

Rascunho anexado: `entregas/rascunho-dashboard1.png`.

Colunas de `data/clean/dataset.csv` (87.229 reservas, sem nulos): hotel, lead_time, arrival_date_year, arrival_date_month, arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights, stays_in_week_nights, adults, children, babies, meal, country, market_segment, distribution_channel, is_repeated_guest, previous_cancellations, previous_bookings_not_canceled, reserved_room_type, assigned_room_type, booking_changes, deposit_type, agent, company, days_in_waiting_list, customer_type, adr, required_car_parking_spaces, total_of_special_requests, reservation_status, reservation_status_date, status_reserva, adr_log.

Variáveis quantitativas (lista `VARS_QUANT` da EDA): lead_time, stays_in_weekend_nights, stays_in_week_nights, adults, children, babies, previous_cancellations, previous_bookings_not_canceled, booking_changes, days_in_waiting_list, adr, required_car_parking_spaces, total_of_special_requests.

Perguntas que o dashboard deve responder:
- Quais variáveis quantitativas se relacionam entre si (correlação de Spearman)?
- Como cada variável se distribui, e essa distribuição muda entre reservas canceladas e não canceladas?
- A correlação e a distribuição mudam quando excluo valores extremos?

Layout: sidebar à esquerda com seleção múltipla das variáveis, um toggle para distinguir por status e um slider de intervalo por variável; no topo, título e uma legenda com quantas reservas ficaram dentro dos intervalos; abaixo, heatmap de correlação à esquerda e grade de histogramas (2 colunas) à direita.

## Restrições

- Editar só o `app.py`, carregando os dados por `src/data_loader.py` (`load_data()`).
- Usar só Streamlit, pandas e Altair; nada de HTML/CSS customizado.
- Pelo menos 1 seletor de variáveis (`st.multiselect`) e 1 slider de intervalo (`st.slider`) na sidebar.
- Nos espaços dos gráficos, usar placeholders (`st.empty()` ou `st.info`) com comentário `# TODO`: os gráficos entram na Aula 22.
- Não alterar o dataset nem recalcular a EDA dentro do app.

## Formato de saída

Um único `app.py` completo, pronto para `streamlit run app.py`, com comentários curtos em português explicando cada seção (configuração da página, sidebar, filtro dos dados, colunas de correlação e distribuição).
