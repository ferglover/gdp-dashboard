import math
import streamlit as st

st.set_page_config(page_title='Calculadora BI de Sensibilidad', page_icon='📊', layout='wide')

DEFAULTS = {
    'arrivals': 32514,
    'qs': 2845,
    'contracts': 484,
    'avg_price': 20576,
    'closing': 17.0,
    'penetration': 8.7,
    'vpg': 3511,
    'volume': 9980000,
}

fmt_int = lambda n: f"{int(round(float(n) if n is not None else 0)):,}"
fmt_money = lambda n: f"${int(round(float(n) if n is not None else 0)):,}"
fmt_pct = lambda n: f"{float(n):.1f}%"

if 'reset' not in st.session_state:
    st.session_state.reset = False


def do_reset():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.session_state.reset = True
    st.rerun()


st.title('Calculadora BI de Sensibilidad')
st.write('Edita la base o cualquiera de los KPIs clave y la calculadora resolverá automáticamente el resto.')

left, right = st.columns([1, 2], gap='large')

with left:
    st.subheader('Datos de entrada')
    st.button('Reset', use_container_width=True, on_click=do_reset)

    if 'arrivals' not in st.session_state:
        st.session_state.arrivals = DEFAULTS['arrivals']
    if 'qs' not in st.session_state:
        st.session_state.qs = DEFAULTS['qs']
    if 'contracts' not in st.session_state:
        st.session_state.contracts = DEFAULTS['contracts']
    if 'avg_price' not in st.session_state:
        st.session_state.avg_price = DEFAULTS['avg_price']
    if 'closing' not in st.session_state:
        st.session_state.closing = DEFAULTS['closing']
    if 'penetration' not in st.session_state:
        st.session_state.penetration = DEFAULTS['penetration']
    if 'vpg' not in st.session_state:
        st.session_state.vpg = DEFAULTS['vpg']
    if 'volume' not in st.session_state:
        st.session_state.volume = DEFAULTS['volume']

    arrivals = st.number_input('Arrivals', min_value=0, step=1, key='arrivals')
    qs = st.number_input("Q's", min_value=0, step=1, key='qs')
    contracts = st.number_input('Contracts', min_value=0, step=1, key='contracts')
    avg_price = st.number_input('Avg Price', min_value=0, step=1, key='avg_price')

with right:
    st.subheader('KPIs')
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7, c8 = st.columns(4)

    # Calculations
    arrivals = float(arrivals)
    qs = float(qs)
    contracts = float(contracts)
    avg_price = float(avg_price)

    closing = (contracts / qs * 100) if qs else 0.0
    penetration = (qs / arrivals * 100) if arrivals else 0.0
    volume = contracts * avg_price
    vpg = (volume / qs) if qs else 0.0

    with c1:
        st.metric('Arrivals', fmt_int(arrivals))
    with c2:
        st.metric("Q's", fmt_int(qs))
    with c3:
        st.metric('Contracts', fmt_int(contracts))
    with c4:
        st.metric('Avg Price', fmt_money(avg_price))
    with c5:
        st.metric('Closing', fmt_pct(closing))
    with c6:
        st.metric('Penetration', fmt_pct(penetration))
    with c7:
        st.metric('VPG', fmt_money(vpg))
    with c8:
        st.metric('Volume', fmt_money(volume))

    st.divider()
    st.subheader('Tabla de sensibilidad por +1 pp de penetración')

    rows = []
    previous_volume = None
    for i in range(9):
        p = penetration + i
        qs_row = arrivals * (p / 100)
        contracts_row = qs_row * (closing / 100)
        volume_row = contracts_row * avg_price
        vpg_row = volume_row / qs_row if qs_row else 0.0
        delta = None if previous_volume is None else volume_row - previous_volume
        rows.append({
            'Penetración': f'{p:.1f}%',
            "Q's": fmt_int(qs_row),
            'Contratos': fmt_int(contracts_row),
            'VPG': fmt_money(vpg_row),
            'Volumen': fmt_money(volume_row),
            'Incremento marginal': '—' if delta is None else fmt_money(delta),
        })
        previous_volume = volume_row

    st.dataframe(rows, use_container_width=True, hide_index=True)

    one_pp_volume = arrivals * 0.01 * (closing / 100) * avg_price
    st.info(
        f'Base cargada: {fmt_int(arrivals)} arrivals, {fmt_int(qs)} Q\'s, {fmt_int(contracts)} contratos y {fmt_money(volume)} de volumen. '
        f'Eso equivale a {fmt_pct(penetration)}, {fmt_pct(closing)} de closing, {fmt_money(avg_price)} de avg price y {fmt_money(vpg)} de VPG. '
        f'Cada +1 pp adicional de penetración agrega aproximadamente {fmt_int(arrivals / 100)} Q\'s, '
        f'{fmt_int((arrivals / 100) * (closing / 100))} contratos y {fmt_money(one_pp_volume)} de volumen, manteniendo constantes el closing y el precio promedio.'
    )
