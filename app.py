import streamlit as st
from datetime import datetime
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Avaliação Pré-Anestésica", page_icon="🏥", layout="centered")

# --- CSS (ESTILO VISUAL + CORREÇÃO DE IMPRESSÃO) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ESTILOS GERAIS */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background-color: #ffe6e6;
        color: #cc0000;
        border: 1px solid #cc0000;
    }
    
    /* CAIXAS DE TEXTO */
    .sigilo-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
        font-size: 0.95em;
        color: #004085;
    }
    .orientacao-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff3cd !important; /* Força cor na impressão */
        border-left: 5px solid #ffc107;
        margin-bottom: 10px;
        color: #856404;
    }
    .med-suspensao {
        padding: 15px;
        background-color: #f8d7da !important;
        border-left: 8px solid #dc3545;
        margin-bottom: 10px;
        color: #721c24;
    }
    .med-manter {
        padding: 15px;
        background-color: #d4edda !important;
        border-left: 8px solid #28a745;
        margin-bottom: 10px;
        color: #155724;
    }
    .alert-medico {
        background-color: #ffe6e6;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #cc0000;
        color: #cc0000;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .status-verde {
        background-color: #d4edda !important;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #28a745;
        color: #155724;
    }
    .status-amarelo {
        background-color: #fff3cd !important;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #ffc107;
        color: #856404;
    }
    .stImage { border: 1px solid #ddd; border-radius: 5px; padding: 5px; }

    /* --- COMANDOS PARA FORÇAR IMPRESSÃO CORRETA --- */
    @media print {
        body {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        /* Esconder botões e menus na impressão */
        button, .stButton, footer, header, .stFileUploader, .stExpander { 
            display: none !important; 
        }
        /* Garantir contraste do texto */
        .orientacao-box, .med-suspensao, .med-manter, .status-verde, .status-amarelo {
            border: 1px solid #ccc;
            color: black !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMÓRIA E VARIÁVEIS ---
if 'pagina_atual' not in st.session_state: st.session_state.pagina_atual = 1
if 'dados' not in st.session_state: st.session_state.dados = {}
if 'lista_medicamentos' not in st.session_state: st.session_state.lista_medicamentos = []
if 'lista_doencas_detectadas' not in st.session_state: st.session_state.lista_doencas_detectadas = []
if 'orientacoes_finais' not in st.session_state: st.session_state.orientacoes_finais = []
if 'files_uploaded' not in st.session_state: st.session_state.files_uploaded = {}

# VARIÁVEIS DE CONTROLE (INICIALIZAÇÃO COMPLETA)
variaveis_inputs = {
    # Pág 2
    "peso_kg": 0.0, "altura_m": 0.0,
    # Pág 3
    "cx_radio": "Não", "lista_cx": "", "tipos_anest": [], "prob_anest": "", "data_ultima_cirurgia": "",
    # Pág 4
    "radio_alergia": "Não", "alg_dip": False, "alg_aines": False, "alg_pen": False, 
    "alg_sulfa": False, "alg_latex": False, "alg_buscopan": False, "alg_iodo": False, 
    "alg_esparadrapo": False, "desc_alergia": "", "uti_alergia": "Não", "tempo_uti_alergia": "",
    "origem_familia": "Não/Não sei", "hist_familia_anestesia": "Não / Não sei", "detalhe_prob_familia": [],
    "status_fumo": "Não, nunca fumei", "tipo_fumo": [], "cig_dia": 0, "anos_fumo": 0.0, "tempo_parou_fumo": "",
    "status_alcool": "Não bebo", "tempo_bebe_alcool": "", "tipo_bebida_alcool": "Cerveja",
    "uso_drogas": [], "tempo_drogas": "", "ultima_drogas": "",
    # Pág 5
    "caminha_2q": "Sim", "sobe_escada": "Sim", "sintoma_esforco": "Não",
    "tipo_sintoma": [], "nivel_esforco": "Grandes esforços (>10 METs)",
    "ja_recebeu_sangue": "Não", "reacao_sangue": "Não", "qual_reacao_sangue": "", 
    "uti_reacao_sangue": "Não", "tempo_uti_sangue": "",
    "jeova": "Não", "abre_boca": "Sim", "move_pescoco": "Sim",
    "uso_aparelho": "Não", "loc_aparelho": "Ambos", "uso_protese": "Não", "loc_protese": "Superior",
    "dente_mole": "Não",
    # STOP-BANG
    "sb_s": "Não", "sb_t": "Não", "sb_o": "Não", "sb_n": "Não"
}

for key, val in variaveis_inputs.items():
    if key not in st.session_state:
        st.session_state[key] = val

def proxima_pagina(): st.session_state.pagina_atual += 1
def pagina_anterior(): st.session_state.pagina_atual -= 1
def remover_medicamento(index): st.session_state.lista_medicamentos.pop(index); st.rerun()

# ==============================================================================
# PÁGINA 1: BOAS-VINDAS E TCLE (COMPLETA)
# ==============================================================================
if st.session_state.pagina_atual == 1:
    st.title("🏥 Avaliação Pré-Anestésica Digital")
    st.markdown("""
    ### Seja bem-vindo(a)!
    Este aplicativo é uma ferramenta criada para **agilizar e facilitar** o seu cuidado pré-operatório.
    """)
    st.markdown("""
    <div class="sigilo-box">
    🔒 <b>Segurança e Sigilo:</b><br>
    Todas as informações fornecidas aqui são protegidas por sigilo médico absoluto (LGPD/Ética Médica).
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    st.subheader("Termo de Consentimento")
    
    url_tcle = "https://drive.google.com/file/d/1DjP021tMa0XoJGXJCI81o22b1QlERW0X/view?usp=sharing"
    
    st.info(f"📄 [Clique aqui para ler o Termo de Consentimento Completo (TCLE)]({url_tcle})")
    aceite = st.checkbox("Li e aceito os termos de consentimento e uso de dados.")
    st.write("")
    if st.button("Iniciar Avaliação ➤", type="primary", disabled=not aceite):
        proxima_pagina()
        st.rerun()

# ==============================================================================
# PÁGINA 2: IDENTIFICAÇÃO E CIRURGIA
# ==============================================================================
elif st.session_state.pagina_atual == 2:
    st.progress(15)
    st.header("1. Identificação")
    with st.form("form_identificacao"):
        st.subheader("Dados Pessoais")
        nome = st.text_input("Nome Completo (Civil)", value=st.session_state.dados.get("nome", ""))
        nome_social = st.text_input("Nome Social (Opcional)", value=st.session_state.dados.get("nome_social", ""))
        col1, col2 = st.columns(2)
        with col1: cpf = st.text_input("CPF (Apenas números)", max_chars=11, placeholder="12345678900", value=st.session_state.dados.get("cpf", ""))
        with col2: nascimento = st.date_input("Data de Nascimento *", value=st.session_state.dados.get("nascimento", datetime(1990, 1, 1)), min_value=datetime(1900, 1, 1), max_value=datetime.today())
        
        col3, col4 = st.columns(2)
        with col3: peso = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, step=0.1, key="peso_kg")
        with col4: altura = st.number_input("Altura (cm) *", min_value=0, max_value=250, step=1, key="altura_cm", help="Ex: 165 para 1 metro e 65")

        telefone = st.text_input("Celular com DDD", max_chars=11, placeholder="11999998888", value=st.session_state.dados.get("telefone", ""))
        genero = st.selectbox("Gênero Biológico", ["Feminino", "Masculino", "Prefiro não responder"], index=0)
        endereco = st.text_input("Endereço Completo", placeholder="Rua, Número, Cidade...", value=st.session_state.dados.get("endereco", ""))
        st.divider()
        st.subheader("Dados da Cirurgia")
        tipo_cirurgia = st.text_input("Qual cirurgia será realizada?", value=st.session_state.dados.get("tipo_cirurgia", ""))
        cirurgiao = st.text_input("Nome do Cirurgião (Opcional)", value=st.session_state.dados.get("cirurgiao", ""))
        data_cirurgia = st.date_input("Data da cirurgia", min_value=datetime.today(), value=st.session_state.dados.get("data_cirurgia", datetime.today()))
        lateralidade = st.radio("Lado da cirurgia", ["Não se aplica", "Direita", "Esquerda", "Ambos"], horizontal=True)
        st.write("")
        c1, c2 = st.columns([1, 1])
        with c1: 
            if st.form_submit_button("⬅ Voltar"): pagina_anterior(); st.rerun()
        with c2:
            submitted = st.form_submit_button("Próximo Passo ➡", type="primary")
            if submitted:
                st.session_state.dados.update({"nome": nome, "cpf": cpf, "telefone": telefone, "endereco": endereco, "genero": genero, "nascimento": nascimento, "peso": peso, "altura": altura})
                proxima_pagina()
                st.rerun()

# ==============================================================================
# PÁGINA 3: MEDICAMENTOS (LISTA GIGANTE - RESTAURADA)
# ==============================================================================
elif st.session_state.pagina_atual == 3:
    st.progress(30)
    st.header("2. Histórico de Saúde")
    st.markdown("Selecione seus medicamentos na lista abaixo (Ordem Alfabética).")
    
    DB_MEDICAMENTOS = {
        "AAS (Aspirina) 100mg": "PERGUNTAR_AAS",
        "Abciximab": "Risco de Sangramento (Antiagregante)",
        "Allenia (Fumarato de Formoterol + Budesonida)": "Asma/DPOC",
        "Amitriptilina 25mg": "PERGUNTAR_AMITRIPTILINA",
        "Anabolizantes / Testosterona (Durateston, Deca, etc)": "PERGUNTAR_ANABOLIZANTE",
        "Anfepramona (Dualid) / Femproporex": "PERGUNTAR_ESTIMULANTE",
        "Anlodipino 5mg": "Hipertensão (Pressão Alta)",
        "Apixabana (Eliquis)": "Risco de Sangramento (Anticoagulante)",
        "Aripiprazol": "Transtorno Psiquiátrico",
        "Atenolol 25mg": "Hipertensão/Arritmia",
        "Atenolol 50mg": "Hipertensão/Arritmia",
        "Bisoprolol 2.5mg": "Cardiopatia/Hipertensão",
        "Bisoprolol 5mg": "Cardiopatia/Hipertensão",
        "Bupropiona (Bup/Wellbutrin)": "PERGUNTAR_PSIQUIATRIA",
        "Cangrelor": "Risco de Sangramento (Antiagregante)",
        "Captopril 25mg": "Hipertensão",
        "Carvedilol 6.25mg": "Insuficiência Cardíaca",
        "Carvedilol 12.5mg": "Insuficiência Cardíaca",
        "Carvedilol 25mg": "Insuficiência Cardíaca",
        "Castanha da Índia": "Risco de Sangramento (Fitoterápico)",
        "Clexane (Enoxaparina)": "PERGUNTAR_CLEXANE",
        "Clonazepam (Rivotril) - COMPRIMIDO": "PERGUNTAR_PSIQUIATRIA",
        "Clonazepam (Rivotril) - GOTAS": "PERGUNTAR_PSIQUIATRIA",
        "Clopidogrel 75mg": "Risco de Sangramento (Antiagregante)",
        "Clortalidona 12.5mg": "Hipertensão (Diurético)",
        "Clortalidona 25mg": "Hipertensão (Diurético)",
        "Dabigatrana (Pradaxa)": "Risco de Sangramento (Anticoagulante)",
        "Dapagliflozina (Forxiga)": "Diabetes/Cardio",
        "Diltiazem": "Arritmia",
        "Diosmina + Hesperidina (Daflon/Venaflon)": "Varizes/Circulação",
        "Dipiridamol": "Risco de Sangramento (Antiagregante)",
        "Doxazosina": "Próstata (HPB) ou Hipertensão",
        "Dutasterida": "Próstata (HPB)",
        "Edoxabana (Lixiana)": "Risco de Sangramento (Anticoagulante)",
        "Empagliflozina (Jardiance)": "Diabetes/Cardio",
        "Enalapril 10mg": "Hipertensão",
        "Enalapril 20mg": "Hipertensão",
        "Ephedra (Ma Huang)": "PERGUNTAR_ESTIMULANTE",
        "Eptifibatide": "Risco de Sangramento (Antiagregante)",
        "Erva de São João (Hipérico)": "Depressão (Interação Medicamentosa)",
        "Escitalopram 10mg": "PERGUNTAR_PSIQUIATRIA",
        "Espironolactona 25mg": "Insuficiência Cardíaca/Diurético",
        "Espironolactona 50mg": "Insuficiência Cardíaca/Diurético",
        "Finasterida": "Próstata (HPB) ou Queda de Cabelo",
        "Fluoxetina 20mg": "PERGUNTAR_PSIQUIATRIA",
        "Fondaparinux (Arixtra)": "Risco de Sangramento (Anticoagulante)",
        "Formoterol": "Asma/DPOC",
        "Furosemida (Lasix) 40mg": "Edema/Insuficiência Cardíaca",
        "Gengibre (Suplemento)": "Risco de Sangramento (Fitoterápico)",
        "Ginkgo Biloba": "Risco de Sangramento (Fitoterápico)",
        "Ginseng": "Risco de Sangramento/Hipoglicemia",
        "Glibenclamida 5mg": "Diabetes Tipo 2",
        "Gliclazida 30mg": "Diabetes Tipo 2",
        "Gliclazida 60mg": "Diabetes Tipo 2",
        "Heparina Não Fracionada": "PERGUNTAR_HNF",
        "Hidroclorotiazida 25mg": "Hipertensão (Diurético)",
        "Insulina Aspart (Novorapid)": "PERGUNTAR_INSULINA_RAPIDA",
        "Insulina Glargina (Lantus/Basaglar)": "PERGUNTAR_INSULINA_LENTA",
        "Insulina Lispro (Humalog)": "PERGUNTAR_INSULINA_RAPIDA",
        "Insulina NPH": "PERGUNTAR_INSULINA_NPH",
        "Insulina Regular": "PERGUNTAR_INSULINA_RAPIDA",
        "Insulina Degludeca (Tresiba)": "PERGUNTAR_INSULINA_LENTA",
        "Levotiroxina (Puran/Euthyrox)": "Hipotireoidismo",
        "Liraglutida (Victoza/Saxenda)": "PERGUNTAR_GLP1",
        "Lixisenatida": "PERGUNTAR_GLP1",
        "Lítio": "Transtorno Bipolar",
        "Losartana 50mg": "Hipertensão",
        "Losartana 100mg": "Hipertensão",
        "Marevan (Varfarina)": "Risco de Sangramento (Anticoagulante)",
        "Metformina (Glifage) 500mg": "Diabetes Tipo 2",
        "Metformina (Glifage) 850mg": "Diabetes Tipo 2",
        "Metoprolol": "Cardiopatia",
        "Metotrexato": "Artrite/Autoimune (Imunossupressor)",
        "Montelucaste": "Asma/Rinite",
        "Mounjaro (Tirzepatida)": "PERGUNTAR_GLP1",
        "Omeprazol 20mg": "Gastrite",
        "Orlistate (Xenical)": "Obesidade",
        "Ozempic (Semaglutida)": "PERGUNTAR_GLP1",
        "Pantoprazol 40mg": "Gastrite",
        "Pioglitazona": "Diabetes Tipo 2",
        "Prasugrel": "Risco de Sangramento (Antiagregante)",
        "Prazosina": "Hipertensão/Próstata",
        "Prednisona (Corticoide)": "Uso Crônico de Corticoide (Risco Adrenal)",
        "Risperidona": "Psiquiátrico",
        "Ritalina": "PERGUNTAR_ESTIMULANTE",
        "Salbutamol (Aerolin)": "Asma (Bombinha)",
        "Salmeterol": "Asma/DPOC",
        "Semaglutida (Rybelsus/Wegovy)": "PERGUNTAR_GLP1",
        "Seretide (Salmeterol + Fluticasona)": "Asma/DPOC",
        "Sertralina 50mg": "PERGUNTAR_PSIQUIATRIA",
        "Sibutramina": "PERGUNTAR_ESTIMULANTE",
        "Sildenafila (Viagra)": "PERGUNTAR_VIAGRA",
        "Sinvastatina 20mg": "Colesterol",
        "Sinvastatina 40mg": "Colesterol",
        "Symbicort (Formoterol + Budesonida)": "Asma/DPOC",
        "Tadalafila (Cialis)": "PERGUNTAR_VIAGRA",
        "Tansulosina": "Próstata (HPB)",
        "Ticagrelor (Brilinta)": "Risco de Sangramento (Antiagregante)",
        "Ticlopidina": "Risco de Sangramento (Antiagregante)",
        "Tirofiban": "Risco de Sangramento (Antiagregante)",
        "Tirzepatida (Mounjaro)": "PERGUNTAR_GLP1",
        "Trembolona": "PERGUNTAR_ANABOLIZANTE",
        "Valsartana": "Hipertensão",
        "Venvanse": "PERGUNTAR_ESTIMULANTE",
        "Xarelto (Rivaroxabana)": "Risco de Sangramento (Anticoagulante)",
    }
    
    with st.container(border=True):
        st.subheader("💊 Adicionar Medicamento")
        col1, col2 = st.columns([2, 1])
        with col1:
            sel = st.selectbox("Nome do Medicamento", ["Selecione..."] + sorted(list(DB_MEDICAMENTOS.keys())) + ["Outro..."])
            manual = st.text_input("Digite o nome e dosagem:") if sel == "Outro..." else ""
        with col2:
            freq = st.selectbox("Frequência", ["1x ao dia (manhã)", "1x ao dia (almoço)", "1x ao dia (noite)", "2x dia", "3x dia", "1x na semana (Semanal)", "Se necessário"])

        doenca, detalhe = "", ""
        if sel in DB_MEDICAMENTOS:
            base = DB_MEDICAMENTOS[sel]
            
            if base == "PERGUNTAR_AAS":
                st.warning("Precisamos detalhar o uso do AAS.")
                motivo = st.radio("Motivo:", ["Prevenção (Nunca tive nada)", "Já tive Infarto (IAM)", "Já tive AVC", "Outro"])
                if motivo == "Já tive Infarto (IAM)":
                    ano = st.text_input("Ano do Infarto?")
                    stent = st.radio("Colocou Stent?", ["Não", "Metálico", "Farmacológico", "Não sei"])
                    detalhe = f"[IAM: {ano} | Stent: {stent}]"; doenca = "Histórico IAM"
                elif motivo == "Já tive AVC":
                    sequela = st.radio("Ficou com sequela?", ["Não", "Sim, fraqueza lado Direito", "Sim, fraqueza lado Esquerdo", "Outra"])
                    detalhe = f"[AVC Prévio | Sequela: {sequela}]"; doenca = "Histórico AVC"
                else: doenca = "Prevenção (AAS)"
            
            elif base == "PERGUNTAR_INSULINA_NPH":
                st.info("Para o jejum, precisamos saber a dose.")
                dose = st.text_input("Esquema (Manhã-Tarde-Noite):", placeholder="Ex: 20-0-10")
                if dose: detalhe = f"[Esquema NPH: {dose}]"; doenca = "Diabetes (Insulina NPH)"
            elif base == "PERGUNTAR_INSULINA_RAPIDA": doenca = "Diabetes (Insulina Rápida/Regular)"
            elif base == "PERGUNTAR_INSULINA_LENTA": doenca = "Diabetes (Insulina Glargina/Lenta)"

            elif base == "PERGUNTAR_GLP1": 
                st.warning("Atenção: Risco de estômago cheio.")
                tempo_uso = st.text_input("Há quanto tempo você usa?")
                ultima_dose = st.text_input("Quando foi a última dose? (Dia/Hora)")
                detalhe = f"[Uso há: {tempo_uso} | Última: {ultima_dose}]"; doenca = "Uso de GLP-1 (Ozempic/Mounjaro)"

            elif base == "PERGUNTAR_ANABOLIZANTE":
                st.warning("Hormônios alteram a anestesia.")
                tempo_uso = st.text_input("Usa há quanto tempo?")
                ultima_dose = st.text_input("Última aplicação?")
                detalhe = f"[Uso há: {tempo_uso} | Última: {ultima_dose}]"; doenca = "Uso de Anabolizantes"
            
            elif base == "PERGUNTAR_ESTIMULANTE": 
                st.warning("Estimulantes interferem na frequência cardíaca.")
                tempo_uso = st.text_input("Usa há quanto tempo?")
                ultima_dose = st.text_input("Quando tomou o último?")
                detalhe = f"[Uso há: {tempo_uso} | Última: {ultima_dose}]"; doenca = "Uso de Estimulantes/Anorexígenos"
            
            elif base == "PERGUNTAR_PSIQUIATRIA":
                motivo = st.radio("Motivo principal:", ["Ansiedade", "Depressão", "Pânico", "Outro"], horizontal=True)
                if motivo: doenca = motivo
            
            elif base == "PERGUNTAR_AMITRIPTILINA":
                 motivo = st.radio("Motivo:", ["Dor Crônica", "Depressão", "Insônia"], horizontal=True)
                 if motivo: doenca = motivo
            
            elif base == "PERGUNTAR_CLEXANE":
                tipo = st.radio("Dose:", ["Profilática (ex: 40mg 1x dia)", "Terapêutica (>40mg ou 2x dia)"])
                hora = st.text_input("Horário da última dose?")
                detalhe = f"[{tipo} | Última: {hora}]"; doenca = "Uso Enoxaparina"
            
            elif base == "PERGUNTAR_HNF":
                dose = st.radio("Dose Diária Total:", ["< 20.000 UI", "> 20.000 UI"])
                detalhe = f"[Dose: {dose}]"; doenca = "Uso Heparina"

            elif base == "PERGUNTAR_VIAGRA":
                motivo = st.radio("Motivo do uso:", ["Disfunção Erétil", "Hipertensão Pulmonar"])
                detalhe = f"[Motivo: {motivo}]"; doenca = "Uso Sidenafila/Tadalafila"

            else: doenca = base

        if st.button("➕ Adicionar"):
            nome = manual if sel == "Outro..." else sel
            if nome and nome != "Selecione...":
                st.session_state.lista_medicamentos.append(f"{nome} ({freq}) {detalhe}")
                if doenca: st.session_state.lista_doencas_detectadas.append(doenca)
                st.rerun()

    col_list, col_disease = st.columns(2)
    with col_list:
        st.subheader("📋 Sua Lista")
        if st.session_state.lista_medicamentos:
            for i, item in enumerate(st.session_state.lista_medicamentos):
                c1, c2 = st.columns([4, 1])
                c1.text(f"• {item}")
                if c2.button("🗑️", key=f"del_{i}"): remover_medicamento(i)
    with col_disease:
        st.subheader("🩺 Condições")
        for d in st.session_state.lista_doencas_detectadas: st.info(d)
        novo = st.text_input("Outra doença?")
        if st.button("Add Doença") and novo:
             st.session_state.lista_doencas_detectadas.append(novo); st.rerun()

    st.divider()
    st.subheader("Histórico Cirúrgico")
    if st.radio("Já fez cirurgia?", ["Não", "Sim"], horizontal=True, key="cx_radio") == "Sim":
        st.text_area("Quais cirurgias você já fez?", placeholder="Ex: Cesárea, Vesícula, Amígdalas...", key="lista_cirurgias")
        col_data, col_anestesia = st.columns(2)
        with col_data:
            st.write("**Quando foi a última?**")
            st.text_input("Data aproximada (Mês/Ano ou só Ano)", placeholder="Ex: 2015", key="data_ultima_cirurgia")
        with col_anestesia:
            st.write("**Quais anestesias você já tomou?**")
            st.multiselect("Selecione todas que lembrar:", ["Geral (Dorme tudo, intubado)", "Raqui (Nas costas, pernas dormentes)", "Peridural (Nas costas)", "Sedação (Dorme leve para exames)", "Local / Bloqueio (Só no braço/perna)", "Não lembro / Não sei dizer"], key="tipos_anest")
        st.write("**Teve algum problema com a anestesia?** (Ex: Enjoo forte, alergia, dificuldade pra acordar)")
        st.text_input("Descreva se houve problema (ou deixe em branco se foi tudo bem):", key="problemas_anestesia")

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1: 
        if st.button("⬅ Voltar"): pagina_anterior(); st.rerun()
    with c2: 
        if st.button("Próximo ➡", type="primary"): proxima_pagina(); st.rerun()

# ==============================================================================
# PÁGINA 4: ALERGIAS, FAMÍLIA E HÁBITOS (LÓGICA COMPLETA)
# ==============================================================================
elif st.session_state.pagina_atual == 4:
    st.progress(45)
    st.header("3. Alergias, Família e Hábitos")
    
    # LISTA DE SOBRENOMES DE RISCO (ATUALIZADA)
    SOBRENOMES_RISCO_HM = [
        "ALIAGHA", "BERKEMBROCK", "BOMBONATTI", "CLASEN", "COSTA", "COUTO", "ENDER COLETO", 
        "GERVIN", "HILLESHEIN", "HOFFMANN", "JANSEN", "JASPER", "KOERICH", "KUHNEN", 
        "LEHMKUHL", "MATTOS", "NEUMANN", "STUART", "POSSAS", "REGIS", "RIZZATI", 
        "SENA", "STEFENS", "WOLLSTEIN", "MORITZ", "KRETZER"
    ]
    
    if any(s in st.session_state.dados.get("nome", "").upper() for s in SOBRENOMES_RISCO_HM):
        st.warning(f"ℹ️ Notei que seu sobrenome é comum na nossa região.")
        if st.radio("Família tem origem Alemã/Europeia?", ["Não/Não sei", "Sim"], horizontal=True, key="origem_familia") == "Sim":
            msg_hm = "ALERTA HIPERTERMIA MALIGNA (Sobrenome de Risco)."
            if msg_hm not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_hm)

    st.subheader("Alergias")
    if st.radio("Tem alergia?", ["Não", "Sim"], horizontal=True, key="radio_alergia") == "Sim":
        c1, c2 = st.columns(2)
        with c1: 
            st.checkbox("Dipirona", key="alg_dip"); st.checkbox("AINES", key="alg_aines")
            st.checkbox("Penicilina", key="alg_pen"); st.checkbox("Sulfa", key="alg_sulfa")
        with c2:
            latex = st.checkbox("Látex", key="alg_latex")
            st.checkbox("Escopolamina (Buscopan)", key="alg_buscopan")
            st.checkbox("Iodo", key="alg_iodo"); st.checkbox("Esparadrapo", key="alg_esparadrapo")
        
        if latex and "ALERTA LÁTEX: Sala Latex-Free Necessária." not in st.session_state.orientacoes_finais:
            st.session_state.orientacoes_finais.append("ALERTA LÁTEX: Sala Latex-Free Necessária.")
        
        st.text_input("Descreva a reação:", key="desc_alergia")
        if st.radio("Precisou internar/UTI?", ["Não", "Sim"], horizontal=True, key="uti_alergia") == "Sim":
            st.text_input("Por quanto tempo?", key="tempo_uti_alergia")

    st.divider()

    st.subheader("Histórico Familiar")
    st.write("Família tem histórico de **problemas graves** com anestesia?")
    if st.radio("Selecione:", ["Não / Não sei", "Sim, já tiveram"], horizontal=True, key="hist_familia_anestesia") == "Sim, já tiveram":
        probs = st.multiselect("O que houve?", [
            "Enjoo, Vômito ou Dor de Cabeça", "Demora para acordar", "Alergia",
            "Febre muito alta (Hipertermia)", "Rigidez muscular", 
            "Parada Cardíaca inesperada", "Falecimento inesperado"
        ], key="detalhe_prob_familia")
        
        sinais_hm = ["Febre muito alta (Hipertermia)", "Rigidez muscular", "Parada Cardíaca inesperada", "Falecimento inesperado"]
        if any(x in probs for x in sinais_hm):
            msg = "ALERTA HIPERTERMIA MALIGNA: Histórico familiar sugestivo."
            if msg not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg)

    st.divider()

    st.subheader("Hábitos (Sigilo Médico 🔒)")
    c1, c2 = st.columns(2)
    with c1:
        fuma = st.radio("Fuma?", ["Não, nunca fumei", "Sim, fumo atualmente", "Ex-fumante (Parei)"], key="status_fumo")
        if fuma == "Sim, fumo atualmente":
            tipo = st.multiselect("Tipo:", ["Cigarro comum", "Vape / Eletrônico", "Palheiro", "Outros"], key="tipo_fumo")
            if "Cigarro comum" in tipo or "Palheiro" in tipo: 
                c = st.number_input("Cigarros/dia", min_value=0, step=1, key="cig_dia")
                a = st.number_input("Anos", min_value=0.0, step=0.1, format="%.1f", key="anos_fumo")
                if c > 0 and a > 0: st.info(f"Carga: {(c/20)*a:.1f} anos-maço")
        elif fuma == "Ex-fumante (Parei)":
            st.text_input("Parou há quanto tempo?", key="tempo_parou_fumo")

    with c2:
        bebe = st.selectbox("Álcool:", ["Não bebo", "Sim, raramente", "Sim, socialmente", "Sim, diariamente/frequentemente"], key="status_alcool")
        if bebe == "Sim, diariamente/frequentemente":
            st.text_input("Há quanto tempo/O que bebe?", key="tempo_bebe_alcool")
            st.radio("O que costuma beber?", ["Cerveja", "Vinho", "Destilados", "Misturo tudo"], key="tipo_bebida_alcool")

    st.write("Drogas Ilícitas:")
    drogas = st.multiselect("Uso:", ["Maconha", "Cocaína", "Crack", "Ecstasy/MDMA", "LSD", "Outras"], key="uso_drogas")
    
    if ("Cocaína" in drogas or "Crack" in drogas or "Ecstasy/MDMA" in drogas) and "ECG Recente (Estimulantes)" not in st.session_state.orientacoes_finais:
        st.session_state.orientacoes_finais.append("ECG Recente (Estimulantes)")
    
    if drogas:
        c1, c2 = st.columns(2)
        with c1: st.text_input("Usa há quanto tempo?", key="tempo_drogas")
        with c2: st.text_input("Último uso?", key="ultima_drogas")

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1: 
        if st.button("⬅ Voltar"): pagina_anterior(); st.rerun()
    with c2: 
        if st.button("Próximo ➡", type="primary"): proxima_pagina(); st.rerun()

# ==============================================================================
# PÁGINA 5: EXAME FÍSICO (VIA AÉREA, SANGUE E STOP-BANG)
# ==============================================================================
elif st.session_state.pagina_atual == 5:
    st.progress(60)
    st.header("4. Exame Físico e Capacidade")
    
    with st.container(border=True):
        st.subheader("😮 Avaliação da Boca e Pescoço")
        col_va1, col_va2 = st.columns(2)
        with col_va1:
            st.write("**Abertura:**")
            boca = st.radio("Consegue colocar 3 dedos seus (em pé) dentro da boca?", ["Sim", "Não"], horizontal=True, key="abre_boca")
        with col_va2:
            st.write("**Pescoço:**")
            pescoco = st.radio("Consegue encostar o queixo no peito e olhar pro teto?", ["Sim", "Não"], horizontal=True, key="move_pescoco")
            
        if boca == "Não" or pescoco == "Não":
            msg_va = "ALERTA VIA AÉREA: Possível intubação difícil. Preparar videolaringoscópio."
            if msg_va not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_va)

        st.divider()
        st.subheader("😁 Dentes e Próteses")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.radio("Usa aparelho ortodôntico?", ["Não", "Sim"], horizontal=True, key="uso_aparelho") == "Sim":
                st.radio("Onde?", ["Superior", "Inferior", "Ambos"], key="loc_aparelho")
        with col_d2:
            if st.radio("Usa prótese dentária (dentadura/ponte)?", ["Não", "Sim"], horizontal=True, key="uso_protese") == "Sim":
                st.radio("Onde é a prótese?", ["Superior", "Inferior", "Ambos"], key="loc_protese")
        
        st.write("")
        if st.radio("Possui algum dente mole, quebrado ou que caiu recentemente?", ["Não", "Sim"], horizontal=True, key="dente_mole") == "Sim":
            msg_dente = "ALERTA DENTAL: Risco de avulsão (Dentes moles/frágeis)."
            if msg_dente not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_dente)

    st.divider()

    with st.container(border=True):
        st.subheader("🏃‍♂️ Capacidade Física")
        caminha = st.radio("1. Caminha 2 quarteirões sem parar?", ["Sim", "Não"], horizontal=True, key="caminha_2q")
        escada = st.radio("2. Sobe 2 lances de escada sem parar?", ["Sim", "Não"], horizontal=True, key="sobe_escada")
        sintoma = st.radio("3. Sente dor no peito ou falta de ar?", ["Não", "Sim"], horizontal=True, key="sintoma_esforco")
        
        if caminha == "Não" or escada == "Não" or sintoma == "Sim":
            st.warning("⚠️ Vamos detalhar.")
            st.multiselect("Sintomas:", ["Falta de ar", "Dor no peito", "Palpitações", "Cansaço"], key="tipo_sintoma")
            opcoes_esforco = [
                "Grandes esforços (>10 METs) - Ex: Correr, Tênis, Futebol",
                "Médios esforços (4-10 METs) - Ex: Varrer casa, Dançar",
                "Pequenos esforços (<4 METs) - Ex: Tomar banho, Vestir-se",
                "Em repouso - Ex: Sentado"
            ]
            esforco = st.radio("Quando cansa?", opcoes_esforco, key="nivel_esforco")
            msg_cardio = "Necessário Avaliação de Risco Cirúrgico (Cardiologista)."
            if "Pequenos" in esforco or "repouso" in esforco or sintoma == "Sim":
                if msg_cardio not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_cardio)

    st.divider()
    
    st.subheader("🩸 Sangue")
    if st.radio("Já recebeu transfusão?", ["Não", "Sim"], horizontal=True, key="ja_recebeu_sangue") == "Sim":
        if st.radio("Teve reação?", ["Não", "Sim"], horizontal=True, key="reacao_sangue") == "Sim":
            st.text_input("O que sentiu?", key="qual_reacao_sangue")
            if st.radio("Precisou de UTI?", ["Não", "Sim"], horizontal=True, key="uti_reacao_sangue") == "Sim":
                st.text_input("Tempo?", key="tempo_uti_sangue")
    
    st.write("")
    jeova = st.radio("Você é Testemunha de Jeová (Recusa Transfusão)?", ["Não", "Sim"], horizontal=True, key="jeova")
    if jeova == "Sim":
        msg_jeova = "ALERTA LEGAL: Testemunha de Jeová. Assinar Termo de Recusa."
        if msg_jeova not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_jeova)

    # --- STOP-BANG (SE IMC > 40) ---
    p = st.session_state.dados.get("peso", 0)
    a = st.session_state.dados.get("altura", 0)
    imc = p / (a * a) if a > 0 else 0

    if imc > 40:
        st.divider()
        st.subheader("💤 Avaliação do Sono (STOP-BANG)")
        st.info(f"Devido ao IMC ({imc:.1f}), responda sobre seu sono:")
        
        sb_s = st.radio("1. Ronca alto?", ["Não", "Sim"], horizontal=True, key="sb_s")
        sb_t = st.radio("2. Cansado de dia?", ["Não", "Sim"], horizontal=True, key="sb_t")
        sb_o = st.radio("3. Para de respirar dormindo?", ["Não", "Sim"], horizontal=True, key="sb_o")
        sb_n = st.radio("4. Pescoço > 40cm?", ["Não", "Sim"], horizontal=True, key="sb_n")
        
        score = 0
        if sb_s == "Sim": score += 1
        if sb_t == "Sim": score += 1
        if sb_o == "Sim": score += 1
        if sb_n == "Sim": score += 1
        if imc > 35: score += 1
        nasc = st.session_state.dados.get("nascimento", datetime.today())
        if (datetime.now().date() - nasc).days // 365 > 50: score += 1
        if st.session_state.dados.get("genero") == "Masculino": score += 1
        
        tem_has = any("Hipertensão" in d for d in st.session_state.lista_doencas_detectadas)
        if tem_has: score += 1
        
        if score >= 5:
            msg_apneia = f"ALERTA APNEIA (STOP-BANG {score}/8): Alto Risco. Preparar VAD."
            if msg_apneia not in st.session_state.orientacoes_finais: st.session_state.orientacoes_finais.append(msg_apneia)

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1: 
        if st.button("⬅ Voltar"): pagina_anterior(); st.rerun()
    with c2: 
        if st.button("Próximo ➡", type="primary"): proxima_pagina(); st.rerun()

# ==============================================================================
# PÁGINA 6: UPLOAD DE EXAMES (LINKS WEB CORRIGIDOS - SEM ERRO DE PASTA)
# ==============================================================================
elif st.session_state.pagina_atual == 6:
    st.progress(90)
    st.header("5. Envio de Exames")
    
    st.info("📷 Tire uma foto clara ou anexe o PDF dos seus exames mais recentes.")
    
    # HEMOGRAMA
    st.subheader("1. Hemograma Completo")
    st.caption("Procure pela folha que tem uma lista de nomes como 'Hemácias', 'Leucócitos' e 'Plaquetas'.")
    
    up_hemo = st.file_uploader("Selecione o arquivo do Hemograma:", type=["jpg", "png", "pdf"], key="up_hemo")
    if up_hemo: st.session_state.files_uploaded["hemo"] = True
    
    # ECG
    st.divider()
    st.subheader("2. Eletrocardiograma (ECG)")
    st.caption("É aquele exame com as linhas desenhadas em papel milimetrado (geralmente rosa ou verde).")
    
    up_ecg = st.file_uploader("Selecione o arquivo do ECG:", type=["jpg", "png", "pdf"], key="up_ecg")
    if up_ecg: st.session_state.files_uploaded["ecg"] = True
    
    # RX
    st.divider()
    st.subheader("3. Raio-X de Tórax (Laudo ou Imagem)")
    st.caption("Pode ser a foto do filme (chapa) ou a foto do papel com o laudo escrito.")
    st.file_uploader("Selecione o arquivo do Raio-X:", type=["jpg", "png", "pdf"], key="up_rx")
    
    # OUTROS
    st.divider()
    st.subheader("4. Outros Exames (Opcional)")
    st.caption("Ex: Ecocardiograma, Teste de Esforço, Espirometria, Parecer do Cardiologista.")
    st.file_uploader("Selecione outros arquivos:", type=["jpg", "png", "pdf"], accept_multiple_files=True, key="up_outros")

    st.write("")
    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1: 
        if st.button("⬅ Voltar"): pagina_anterior(); st.rerun()
    with c2: 
        if st.button("Finalizar Avaliação 🏁", type="primary"): proxima_pagina(); st.rerun()

# ==============================================================================
# PÁGINA 7: RESUMO E LÓGICA DE SUSPENSÃO COMPLETA (V44)
# ==============================================================================
elif st.session_state.pagina_atual == 7:
    st.progress(100)
    st.header("✅ Avaliação Concluída!")
    st.success("Obrigado! Seus dados e exames foram registrados.")
    st.divider()

    # --- 1. ORIENTAÇÕES AO PACIENTE ---
    st.subheader("📄 Suas Orientações Pré-Operatórias")
    
    texto_jejum = "8 horas de jejum absoluto (sólidos e líquidos grossos). Água pura até 2h antes."
    st.markdown(f"""<div class="orientacao-box">🍽️ <b>JEJUM OBRIGATÓRIO:</b><br>{texto_jejum}</div>""", unsafe_allow_html=True)
    
    # ADORNOS E PRÓTESES
    texto_adornos = "💍 <b>ADORNOS E PRÓTESES:</b><br>- <b>Retirar todos os adornos</b> (brincos, anéis, alianças, piercings, relógios)."
    if st.session_state.get("uso_protese") == "Sim":
        texto_adornos += "<br>- <b>⚠️ Vir sem a prótese dentária</b> (ou trazer caixinha própria para guardar)."
    
    st.markdown(f"""<div class="orientacao-box">{texto_adornos}</div>""", unsafe_allow_html=True)

    # --- LÓGICA DE SUSPENSÃO DE MEDICAMENTOS (RIGOROSA E COMPLETA V44) ---
    st.subheader("💊 Orientação sobre seus Medicamentos")
    
    lista_meds = str(st.session_state.lista_medicamentos).lower()
    
    suspensao_antes = []
    suspensao_dia = []
    manter = []

    # 1. IECA/BRA (Manter)
    if any(x in lista_meds for x in ["losartana", "enalapril", "captopril", "valsartana"]):
        manter.append("Remédios de Pressão (Losartana/Enalapril, etc) - Tomar com pouca água 2h antes")

    # 2. ANTIDIABÉTICOS
    if "metformina" in lista_meds: suspensao_dia.append("Metformina (Glifage)")
    if "glibenclamida" in lista_meds: suspensao_antes.append("Glibenclamida (1 dia antes)")
    if "gliclazida" in lista_meds: suspensao_antes.append("Gliclazida (1 dia antes)")
    if "pioglitazona" in lista_meds: manter.append("Pioglitazona")
    
    # SGLT2
    if "dapagliflozina" in lista_meds or "empagliflozina" in lista_meds:
        suspensao_antes.append("Dapagliflozina/Empagliflozina (3 dias antes)")
    
    # GLP-1
    if "lixisenatida" in lista_meds: suspensao_antes.append("Lixisenatida (1 dia antes)")
    if "liraglutida" in lista_meds: suspensao_antes.append("Liraglutida (Victoza/Saxenda) - 2 dias antes")
    if "tirzepatida" in lista_meds: suspensao_antes.append("Tirzepatida (Mounjaro) - 15 dias antes")
    if "semaglutida" in lista_meds: suspensao_antes.append("Semaglutida (Ozempic/Wegovy) - 21 dias antes")

    # INSULINAS (CÁLCULO NPH)
    if "nph" in lista_meds:
        dose_noite = "metade da dose usual"
        try:
            nums = re.findall(r'\d+', lista_meds.split("nph")[1])
            if nums:
                dose_calc = int(nums[-1]) / 2
                dose_noite = f"{dose_calc:.0f} unidades"
        except: pass
        suspensao_antes.append(f"<b>Insulina NPH:</b> Aplicar apenas {dose_noite} na noite anterior. NÃO aplicar na manhã da cirurgia.")
    
    if "rápida" in lista_meds or "regular" in lista_meds:
        suspensao_dia.append("Insulina Rápida/Regular (A glicemia será corrigida no hospital se necessário)")
    
    if "glargina" in lista_meds or "degludeca" in lista_meds or "lenta" in lista_meds:
        suspensao_antes.append("Insulina Lenta (Glargina/Degludeca) - Suspender 72h antes")

    # FITOTERÁPICOS
    if "ginseng" in lista_meds or "são joão" in lista_meds: suspensao_antes.append("Ginseng/Erva de São João (7 dias antes)")
    if "ginkgo" in lista_meds: suspensao_antes.append("Ginkgo Biloba (36h antes)")
    if "gengibre" in lista_meds: suspensao_antes.append("Gengibre (15 dias antes)")
    if "ephedra" in lista_meds: suspensao_antes.append("Ephedra (24h antes)")

    # ORLISTATE
    if "orlistate" in lista_meds: suspensao_antes.append("Orlistate (2 semanas antes)")

    # VIAGRA/CIALIS
    if "viagra" in lista_meds or "cialis" in lista_meds or "sildenafila" in lista_meds or "tadalafila" in lista_meds:
        if "hipertensão pulmonar" in lista_meds: manter.append("Sildenafila/Tadalafila (Motivo: Pulmão)")
        else: suspensao_antes.append("Viagra/Cialis/Sildenafila (15 dias antes)")

    # ANTICOAGULANTES/ANTIAGREGANTES
    if "clopidogrel" in lista_meds: suspensao_antes.append("Clopidogrel (5 dias antes)")
    if "prasugrel" in lista_meds or "ticagrelor" in lista_meds: suspensao_antes.append("Prasugrel/Ticagrelor (7 dias antes)")
    if "cilostazol" in lista_meds: suspensao_antes.append("Cilostazol (48h antes)")
    if "abciximab" in lista_meds: suspensao_antes.append("Abciximab (48h antes)")
    if "tirofiban" in lista_meds or "eptifibatide" in lista_meds: suspensao_antes.append("Tirofiban/Eptifibatide (8h antes)")
    
    if "marevan" in lista_meds or "varfarina" in lista_meds: 
        suspensao_antes.append("Varfarina (5 dias antes) - Trazer Coagulograma Novo (INR < 1.5)")
        
    if "rivaroxabana" in lista_meds or "apixabana" in lista_meds or "dabigatrana" in lista_meds:
        suspensao_antes.append("Xarelto/Eliquis/Pradaxa (72h antes) - Confirmar função renal")

    # HEPARINAS (DOSE DEPENDENTE)
    if "heparina" in lista_meds:
        if "< 20.000" in lista_meds: suspensao_antes.append("Heparina (HNF) - 12h antes")
        else: suspensao_antes.append("Heparina (HNF) - 24h antes")
        
    if "enoxaparina" in lista_meds or "clexane" in lista_meds:
        if "profilática" in lista_meds: suspensao_antes.append("Enoxaparina (Clexane) - 12h antes")
        else: suspensao_antes.append("Enoxaparina (Clexane) - 24h antes")

    # AAS (PADRÃO MANTER)
    if "aas" in lista_meds: manter.append("AAS (Aspirina) - Exceto se cirurgião pedir suspensão")

    # EXIBIÇÃO
    if suspensao_antes:
        st.markdown(f"""<div class="med-suspensao">🛑 <b>SUSPENDER ANTES:</b><br>{'<br>'.join(suspensao_antes)}</div>""", unsafe_allow_html=True)
    if suspensao_dia:
        st.markdown(f"""<div class="med-suspensao">🚫 <b>NÃO TOMAR NO DIA:</b><br>{'<br>'.join(suspensao_dia)}</div>""", unsafe_allow_html=True)
    if manter:
        st.markdown(f"""<div class="med-manter">✅ <b>MANTER (TOMAR):</b><br>{'<br>'.join(manter)}</div>""", unsafe_allow_html=True)

    st.divider()

    # --- 2. ALERTAS DE EXAMES E LEGAIS ---
    if "ALERTA LEGAL: Testemunha de Jeová." in st.session_state.orientacoes_finais:
        st.warning("⚖️ Testemunha de Jeová: Necessário assinar Termo de Recusa de Transfusão (Disponível no hospital).")
    
    fez_ecg = st.session_state.files_uploaded.get("ecg", False)
    if "ECG Recente (Estimulantes)" in st.session_state.orientacoes_finais and not fez_ecg:
        st.error("⚠️ PENDÊNCIA: Necessário trazer ECG recente devido ao histórico de uso de substâncias.")

    st.divider()

    # --- 3. STATUS (SEMÁFORO) ---
    bloqueio_cardio = "Necessário Avaliação de Risco Cirúrgico" in str(st.session_state.orientacoes_finais)
    bloqueio_drogas = "ECG Recente (Estimulantes)" in str(st.session_state.orientacoes_finais) and not fez_ecg
    bloqueio_apneia = any("ALERTA APNEIA" in x for x in st.session_state.orientacoes_finais)
    
    if not bloqueio_cardio and not bloqueio_drogas and not bloqueio_apneia:
        st.markdown("""<div class="status-verde">✅ <b>CIRURGIA PRÉ-APROVADA!</b><br>Aguarde contato para agendamento.</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="status-amarelo">⚠️ <b>ANÁLISE PENDENTE</b><br>Necessário avaliação da equipe (Cardio/Exames) antes da liberação.</div>""", unsafe_allow_html=True)

    st.write("")
    
    # --- 4. ÁREA RESTRITA (EXPANDER FECHADO) ---
    with st.expander("🔒 Área Restrita (Equipe Médica)"):
        st.write("### Resumo de Alertas Técnicos")
        alertas_tecnicos = ["ALERTA LÁTEX", "ALERTA HIPERTERMIA", "ALERTA VIA AÉREA", "ALERTA APNEIA", "Orlistate", "ALERTA DENTAL"]
        encontrou = False
        for alerta in st.session_state.orientacoes_finais:
            if any(x in alerta for x in alertas_tecnicos) or ("Orlistate" in lista_meds and "Vit K" not in str(st.session_state.orientacoes_finais)):
                st.markdown(f"""<div class="alert-medico">🚨 {alerta}</div>""", unsafe_allow_html=True)
                encontrou = True
        
        if "orlistate" in lista_meds: 
            st.markdown(f"""<div class="alert-medico">🚨 Orlistate: Checar coagulação (Vit K).</div>""", unsafe_allow_html=True)
            encontrou = True
            
        if not encontrou: st.success("Sem alertas técnicos graves.")

    st.write("")
    
    # --- GERADOR DE HTML PARA IMPRESSÃO ---
    def gerar_html_impressao():
        html = f"""
        <html>
        <head>
            <title>Relatório Pré-Anestésico</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                .box {{ border: 1px solid #ccc; padding: 15px; margin-bottom: 10px; background: #f9f9f9; }}
                .warning {{ background-color: #f8d7da; border: 1px solid #dc3545; color: #721c24; padding: 10px; }}
                h1 {{ color: #007bff; }}
            </style>
        </head>
        <body onload="window.print()">
            <h1>Relatório de Orientações</h1>
            <p><b>Paciente:</b> {st.session_state.dados.get('nome')}</p>
            <p><b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
            <hr>
            <div class="box">
                <h3>🍽️ Jejum e Adornos</h3>
                <p><b>Jejum:</b> {texto_jejum}</p>
                <p><b>Adornos:</b> {texto_adornos}</p>
            </div>
            
            <div class="box">
                <h3>💊 Medicamentos</h3>
                {'<p>' + '<br>'.join(st.session_state.lista_medicamentos) + '</p>' if st.session_state.lista_medicamentos else "<p>Nenhum medicamento informado.</p>"}
            </div>

            {f'<div class="warning"><h3>🛑 Suspensão Obrigatória:</h3><p>{"<br>".join(suspensao_antes)}</p></div>' if suspensao_antes else ''}
            
            <hr>
            <p style="font-size: small; color: gray;">Este documento é um guia pré-operatório gerado automaticamente.</p>
        </body>
        </html>
        """
        return html

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🖨️ Gerar Relatório (Visualizar)"):
            html_code = gerar_html_impressao()
            st.components.v1.html(html_code, height=400, scrolling=True)
            
    with c2:
        st.write("---")
        st.caption("Validação TCC:")
        if st.button("Área do Avaliador (Juiz) ➡", type="secondary"):
            proxima_pagina()
            st.rerun()

# ==============================================================================
# PÁGINA 8: AVALIAÇÃO DOS JUÍZES (LINK SEGURO PARA GOOGLE FORMS)
# ==============================================================================
elif st.session_state.pagina_atual == 8:
    st.header("📋 Questionário de Validação")
    
    st.markdown("""
    **Prezado(a) Avaliador(a),**
    
    Para garantir a segurança e a integridade dos dados da pesquisa, a avaliação do protótipo é realizada através de um formulário externo seguro.
    
    Por favor, clique no botão abaixo para responder ao questionário de validação.
    """)
    st.divider()

    # SEU LINK DO GOOGLE FORMS AQUI
    url_forms = "https://docs.google.com/forms/d/e/1FAIpQLSejX8GH9Vzf0kb9fLbRsCVKAO80-R-yigAQ7Mae8IgJC-5GbQ/viewform"

    # Botão Grande e Chamativo
    st.link_button("📝 CLIQUE AQUI PARA AVALIAR O PROTÓTIPO (Google Forms)", url_forms, type="primary", use_container_width=True)

    st.divider()
    st.info("Após responder o formulário, você pode fechar esta página. Muito obrigada pela colaboração!")
