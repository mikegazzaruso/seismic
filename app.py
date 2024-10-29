import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configurazione iniziale della pagina
st.set_page_config(
    page_title="S.E.I.S.M.I.C.",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS per il layout e gli stili
st.markdown("""
<style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .title-container {
        flex-grow: 1;
    }
    .theme-container {
        text-align: right;
        padding-top: 1rem;
    }
    .copyright {
        font-size: 0.8em;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Header con titolo e informazioni
st.markdown("""
<div class="header-container">
    <div class="title-container">
        <h1>S.E.I.S.M.I.C.</h1>
        <p>Sistema Evoluto di Identificazione e Sorveglianza Movimenti Italia Centrale</p>
        <p class="copyright">© 2024 Mike Gazzaruso</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Nota informativa per il tema nella sidebar
st.sidebar.markdown("""
### Impostazioni Tema
Per cambiare il tema (Chiaro/Scuro):
1. Clicca su ⋮ in alto a destra
2. Seleziona 'Settings'
3. Scegli il tema sotto 'Theme'
""")

# Lista delle province italiane
province = [
    "Agrigento", "Alessandria", "Ancona", "Aosta", "Arezzo", "Ascoli Piceno", "Asti", "Avellino", 
    "Bari", "Barletta-Andria-Trani", "Belluno", "Benevento", "Bergamo", "Biella", "Bologna", 
    "Bolzano", "Brescia", "Brindisi", "Cagliari", "Caltanissetta", "Campobasso", "Carbonia-Iglesias",
    "Caserta", "Catania", "Catanzaro", "Chieti", "Como", "Cosenza", "Cremona", "Crotone", "Cuneo",
    "Enna", "Fermo", "Ferrara", "Firenze", "Foggia", "Forlì-Cesena", "Frosinone", "Genova",
    "Gorizia", "Grosseto", "Imperia", "Isernia", "La Spezia", "L'Aquila", "Latina", "Lecce",
    "Lecco", "Livorno", "Lodi", "Lucca", "Macerata", "Mantova", "Massa-Carrara", "Matera",
    "Messina", "Milano", "Modena", "Monza e Brianza", "Napoli", "Novara", "Nuoro", "Olbia-Tempio",
    "Oristano", "Padova", "Palermo", "Parma", "Pavia", "Perugia", "Pesaro e Urbino", "Pescara",
    "Piacenza", "Pisa", "Pistoia", "Pordenone", "Potenza", "Prato", "Ragusa", "Ravenna",
    "Reggio Calabria", "Reggio Emilia", "Rieti", "Rimini", "Roma", "Rovigo", "Salerno", "Sassari",
    "Savona", "Siena", "Siracusa", "Sondrio", "Sud Sardegna", "Taranto", "Teramo", "Terni",
    "Torino", "Trapani", "Trento", "Treviso", "Trieste", "Udine", "Varese", "Venezia",
    "Verbano-Cusio-Ossola", "Vercelli", "Verona", "Vibo Valentia", "Vicenza", "Viterbo"
]

# Funzione per ottenere i dati dei terremoti
@st.cache_data(ttl=300)
def get_terremoti():
    url = "https://webservices.ingv.it/fdsnws/event/1/query"
    
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "starttime": start_date,
        "endtime": end_date,
        "format": "text",
        "minmag": 0,
        "limit": 1000
    }
    
    response = requests.get(url, params=params)
    
    data = []
    for line in response.text.split('\n')[1:]:
        if line.strip():
            parts = line.split('|')
            if len(parts) >= 13:
                data.append({
                    'Data': datetime.strptime(parts[1], '%Y-%m-%dT%H:%M:%S.%f'),
                    'Latitudine': float(parts[2]),
                    'Longitudine': float(parts[3]),
                    'Profondità': float(parts[4]),
                    'Magnitudo': float(parts[10]),
                    'Località': parts[12].strip()
                })
    
    return pd.DataFrame(data)

def get_provincia_sigla(provincia):
    sigle = {
        'Agrigento': 'AG', 'Alessandria': 'AL', 'Ancona': 'AN', 'Aosta': 'AO', 'Arezzo': 'AR',
        'Ascoli Piceno': 'AP', 'Asti': 'AT', 'Avellino': 'AV', 'Bari': 'BA', 'Barletta-Andria-Trani': 'BT',
        'Belluno': 'BL', 'Benevento': 'BN', 'Bergamo': 'BG', 'Biella': 'BI', 'Bologna': 'BO',
        'Bolzano': 'BZ', 'Brescia': 'BS', 'Brindisi': 'BR', 'Cagliari': 'CA', 'Caltanissetta': 'CL',
        'Campobasso': 'CB', 'Caserta': 'CE', 'Catania': 'CT', 'Catanzaro': 'CZ', 'Chieti': 'CH',
        'Como': 'CO', 'Cosenza': 'CS', 'Cremona': 'CR', 'Crotone': 'KR', 'Cuneo': 'CN',
        'Enna': 'EN', 'Fermo': 'FM', 'Ferrara': 'FE', 'Firenze': 'FI', 'Foggia': 'FG',
        'Forlì-Cesena': 'FC', 'Frosinone': 'FR', 'Genova': 'GE', 'Gorizia': 'GO', 'Grosseto': 'GR',
        'Imperia': 'IM', 'Isernia': 'IS', 'La Spezia': 'SP', "L'Aquila": 'AQ', 'Latina': 'LT',
        'Lecce': 'LE', 'Lecco': 'LC', 'Livorno': 'LI', 'Lodi': 'LO', 'Lucca': 'LU',
        'Macerata': 'MC', 'Mantova': 'MN', 'Massa-Carrara': 'MS', 'Matera': 'MT', 'Messina': 'ME',
        'Milano': 'MI', 'Modena': 'MO', 'Monza e Brianza': 'MB', 'Napoli': 'NA', 'Novara': 'NO',
        'Nuoro': 'NU', 'Oristano': 'OR', 'Padova': 'PD', 'Palermo': 'PA', 'Parma': 'PR',
        'Pavia': 'PV', 'Perugia': 'PG', 'Pesaro e Urbino': 'PU', 'Pescara': 'PE', 'Piacenza': 'PC',
        'Pisa': 'PI', 'Pistoia': 'PT', 'Pordenone': 'PN', 'Potenza': 'PZ', 'Prato': 'PO',
        'Ragusa': 'RG', 'Ravenna': 'RA', 'Reggio Calabria': 'RC', 'Reggio Emilia': 'RE',
        'Rieti': 'RI', 'Rimini': 'RN', 'Roma': 'RM', 'Rovigo': 'RO', 'Salerno': 'SA',
        'Sassari': 'SS', 'Savona': 'SV', 'Siena': 'SI', 'Siracusa': 'SR', 'Sondrio': 'SO',
        'Taranto': 'TA', 'Teramo': 'TE', 'Terni': 'TR', 'Torino': 'TO', 'Trapani': 'TP',
        'Trento': 'TN', 'Treviso': 'TV', 'Trieste': 'TS', 'Udine': 'UD', 'Varese': 'VA',
        'Venezia': 'VE', 'Verbano-Cusio-Ossola': 'VB', 'Vercelli': 'VC', 'Verona': 'VR',
        'Vibo Valentia': 'VV', 'Vicenza': 'VI', 'Viterbo': 'VT'
    }
    return sigle.get(provincia, '')

def appartiene_a_provincia(localita, provincia):
    localita = localita.lower()
    provincia = provincia.lower()
    sigla = get_provincia_sigla(provincia.title())
    return provincia in localita or f"({sigla.lower()})" in localita

# Selectbox per la provincia
province_list = [""] + sorted(province)
col1, col2 = st.columns([3,1])
with col1:
    provincia_selezionata = st.selectbox(
        "Seleziona una provincia:",
        options=province_list,
        key="provincia_select",
        index=0
    )
with col2:
    if st.button("Aggiorna dati", key="refresh_button"):
        with st.spinner('Aggiornamento dati in corso...'):
            st.cache_data.clear()
            st.rerun()

if provincia_selezionata:
    try:
        df = get_terremoti()
        
        df_provincia = df[df['Località'].apply(lambda x: appartiene_a_provincia(x, provincia_selezionata))]
        df_provincia = df_provincia.sort_values('Data', ascending=False)
        
        if len(df_provincia) > 0:
            st.subheader(f"Ultimi 10 terremoti nella provincia di {provincia_selezionata}")
            
            # Prepara i dati per la tabella
            df_display = df_provincia.head(10).copy()
            
            # Formatta le colonne
            df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y %H:%M:%S')
            df_display['Latitudine'] = df_display['Latitudine'].round(3)
            df_display['Longitudine'] = df_display['Longitudine'].round(3)
            df_display['Profondità'] = df_display['Profondità'].round(1)
            df_display['Magnitudo'] = df_display['Magnitudo'].round(1)
            
            # Rinomina le colonne per una migliore visualizzazione
            df_display = df_display.rename(columns={
                'Data': 'Data e Ora',
                'Località': 'Località',
                'Magnitudo': 'Magnitudo',
                'Profondità': 'Profondità (km)',
                'Latitudine': 'Latitudine',
                'Longitudine': 'Longitudine'
            })
            
            # Mostra la tabella
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Data e Ora": st.column_config.TextColumn(width="medium"),
                    "Località": st.column_config.TextColumn(width="large"),
                    "Magnitudo": st.column_config.NumberColumn(width="small"),
                    "Profondità (km)": st.column_config.NumberColumn(width="small"),
                    "Latitudine": st.column_config.NumberColumn(width="small"),
                    "Longitudine": st.column_config.NumberColumn(width="small")
                }
            )
            
            # Grafici temporali
            st.markdown("---")
            st.subheader("Analisi Temporale dell'Attività Sismica")
            
            # Prepara i dati ordinati per data
            df_plot = df_provincia.sort_values('Data')
            
            # Crea due grafici affiancati
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Magnitudo nel tempo', 'Profondità nel tempo'),
                vertical_spacing=0.12,
                specs=[[{"secondary_y": True}],
                      [{"secondary_y": True}]]
            )
            
            # Grafico Magnitudo
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Data'],
                    y=df_plot['Magnitudo'],
                    mode='lines+markers',
                    name='Magnitudo',
                    line=dict(color='red'),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            # Media mobile della magnitudo (7 giorni)
            df_plot['Magnitudo_MA'] = df_plot['Magnitudo'].rolling(window=7, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Data'],
                    y=df_plot['Magnitudo_MA'],
                    mode='lines',
                    name='Media Mobile (7g)',
                    line=dict(color='rgba(255, 0, 0, 0.3)', dash='dash')
                ),
                row=1, col=1
            )
            
            # Grafico Profondità
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Data'],
                    y=df_plot['Profondità'],
                    mode='lines+markers',
                    name='Profondità',
                    line=dict(color='blue'),
                    marker=dict(size=8)
                ),
                row=2, col=1
            )
            
            # Media mobile della profondità (7 giorni)
            df_plot['Profondita_MA'] = df_plot['Profondità'].rolling(window=7, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Data'],
                    y=df_plot['Profondita_MA'],
                    mode='lines',
                    name='Media Mobile (7g)',
                    line=dict(color='rgba(0, 0, 255, 0.3)', dash='dash')
                ),
                row=2, col=1
            )
            
            # Aggiorna il layout
            fig.update_layout(
                height=700,
                showlegend=True,
                template='plotly_white',
                hovermode='x unified'
            )
            
            # Aggiorna gli assi
            fig.update_yaxes(title_text="Magnitudo", row=1, col=1)
            fig.update_yaxes(title_text="Profondità (km)", row=2, col=1)
            
            # Mostra il grafico
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistiche riassuntive
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Frequenza giornaliera
                giorni_totali = (df_provincia['Data'].max() - df_provincia['Data'].min()).days + 1
                eventi_per_giorno = len(df_provincia) / max(giorni_totali, 1)
                st.metric("Media eventi giornalieri", f"{eventi_per_giorno:.1f}")
            
            with col2:
                # Trend magnitudo
                try:
                    if len(df_plot) >= 2:
                        trend = np.polyfit(range(len(df_plot)), df_plot['Magnitudo'], 1)[0]
                        trend_direction = "↑" if trend > 0 else "↓" if trend < 0 else "→"
                        st.metric("Trend Magnitudo", trend_direction, f"{abs(trend):.3f}/evento")
                    else:
                        st.metric("Trend Magnitudo", "N/D", "Dati insufficienti")
                except:
                    st.metric("Trend Magnitudo", "N/D", "Calcolo non possibile")
            
            with col3:
                # Eventi ultime 24h
                ore_24 = df_provincia[df_provincia['Data'] > datetime.now() - timedelta(days=1)]
                st.metric("Eventi ultime 24h", len(ore_24))
            
            # Istogramma della distribuzione oraria
            st.subheader("Distribuzione oraria degli eventi")
            
            # Estrai l'ora del giorno per ogni evento
            df_provincia['Ora'] = df_provincia['Data'].dt.hour
            
            # Crea l'istogramma
            fig_hist = px.histogram(
                df_provincia,
                x='Ora',
                nbins=24,
                title='Distribuzione degli eventi nelle 24 ore',
                labels={'Ora': 'Ora del giorno', 'count': 'Numero di eventi'},
                color_discrete_sequence=['indianred']
            )
            
            fig_hist.update_layout(
                bargap=0.1,
                xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                showlegend=False
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Analisi del rischio
            st.markdown("---")
            st.subheader("Analisi del Rischio Sismico")
            
            def calcola_rischio_relativo(df_provincia):
                if len(df_provincia) == 0:
                    return 0, "Insufficiente storico dati"
                
                # 1. Frequenza terremoti (ultimi 7 giorni)
                week_ago = datetime.now() - timedelta(days=7)
                eventi_settimana = len(df_provincia[df_provincia['Data'] > week_ago])
                freq_score = min(eventi_settimana / 7, 1)  # Normalizzato a 1
                
                # 2. Trend magnitudo
                df_sorted = df_provincia.sort_values('Data')
                if len(df_sorted) >= 3:
                    magnitudo_trend = np.polyfit(range(len(df_sorted)), df_sorted['Magnitudo'], 1)[0]
                    trend_score = min(max(magnitudo_trend, 0), 1)  # Normalizzato tra 0 e 1
                else:
                    trend_score = 0
                
                # 3. Profondità media (più superficiale = più rischio)
                prof_media = df_provincia['Profondità'].mean()
                depth_score = 1 - min(prof_media / 100, 1)  # Normalizzato, considerando 100km come profondità massima
                
                # 4. Tempo dall'ultimo evento
                ultimo_evento = df_provincia['Data'].max()
                ore_da_ultimo = (datetime.now() - ultimo_evento).total_seconds() / 3600
                tempo_score = 1 - min(ore_da_ultimo / 72, 1)  # Normalizzato, considerando 72 ore
                
                # Calcolo rischio complessivo (media pesata)
                pesi = [0.4, 0.2, 0.2, 0.2]  # Maggior peso alla frequenza
                rischio = (freq_score * pesi[0] + 
                        trend_score * pesi[1] + 
                        depth_score * pesi[2] + 
                        tempo_score * pesi[3])
                
                # Determina il livello di rischio e il messaggio
                if rischio < 0.2:
                    livello = "BASSO"
                    colore = "green"
                    msg = "Attività sismica nella norma."
                elif rischio < 0.4:
                    livello = "MEDIO-BASSO"
                    colore = "lightgreen"
                    msg = "Leggero incremento dell'attività sismica."
                elif rischio < 0.6:
                    livello = "MEDIO"
                    colore = "yellow"
                    msg = "Attività sismica moderata, situazione da monitorare."
                elif rischio < 0.8:
                    livello = "MEDIO-ALTO"
                    colore = "orange"
                    msg = "Significativa attività sismica nelle ultime ore."
                else:
                    livello = "ALTO"
                    colore = "red"
                    msg = "Intensa attività sismica in corso."
                
                dettagli = f"""
                Fattori considerati:
                • Frequenza eventi recenti: {freq_score:.2f}
                • Trend magnitudo: {trend_score:.2f}
                • Analisi profondità: {depth_score:.2f}
                • Tempo dall'ultimo evento: {tempo_score:.2f}
                """
                
                return rischio, livello, colore, msg, dettagli

            rischio, livello, colore, msg, dettagli = calcola_rischio_relativo(df_provincia)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Visualizza il gauge meter del rischio
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = rischio * 100,
                    title = {'text': f"Livello di Rischio: {livello}"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': colore},
                        'steps': [
                            {'range': [0, 20], 'color': 'lightgray'},
                            {'range': [20, 40], 'color': 'lightgreen'},
                            {'range': [40, 60], 'color': 'yellow'},
                            {'range': [60, 80], 'color': 'orange'},
                            {'range': [80, 100], 'color': 'red'}
                        ]
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                ### Previsione per le prossime 24 ore
                
                **Stato attuale**: {msg}
                
                {dettagli}
                
                *Nota: Questa è una stima statistica basata sui dati storici recenti. 
                Non è possibile prevedere con certezza gli eventi sismici.*
                """)
            
        else:
            st.info(f"Nessun terremoto registrato negli ultimi 30 giorni nella provincia di {provincia_selezionata}")
    
    except Exception as e:
        st.error(f"Si è verificato un errore durante il recupero dei dati: {str(e)}")
else:
    st.info("Seleziona una provincia per visualizzare i dati sui terremoti")