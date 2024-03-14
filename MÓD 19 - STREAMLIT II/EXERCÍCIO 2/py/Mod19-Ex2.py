
import timeit
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# from PIL import Image
from PIL                 import Image
from io                  import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

#FUNÇÃO PARA CARREGAR OS DADOS
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter o df para csv
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Função principal da aplicação
def main():
    st.set_page_config(page_title = 'Telemarketing analisys', \
        page_icon = '../img/telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )
    st.write('# Telemarketing analisys')
    st.markdown("---")
    
    image = Image.open('../img/Bank-Branding.jpg')
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if (data_file_1 is not None):
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())
        st.write('Quantidade de linhas:', bank_raw.shape[0])
        st.write('Quantidade de colunas:', bank_raw.shape[1])

        with st.sidebar.form(key='my_form'):
            # TIPO DE GRÁFICO
            graph_type = st.radio("Tipo de gráfico:", ("Barras", "Pizza"))

            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade',
                                min_value = min_age,
                                max_value = max_age,
                                value = (min_age, max_age),
                                step = 1)


            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])


            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])


            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])


            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])


            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])


            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])


            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )

            submit_button = st.form_submit_button(label='Aplicar')
    
        st.write('## Após os filtros')
        st.write(bank.head())
        st.write('Quantidade de linhas:', bank.shape[0])
        st.write('Quantidade de colunas:', bank.shape[1])

        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                           data=df_xlsx,
                           file_name='bank_filtered.xlsx')

        st.markdown("---")

        # PLOTS
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
        # Coluna 1
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()

        # Coluna 2
        bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
        bank_target_perc = bank_target_perc.sort_index()


        # Botões de download dos dados dos gráficos
        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_raw_y.xlsx')

        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_y.xlsx')
        st.markdown("---")

        st.write('## Proporção de aceite')

        # PLOTS
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
        if graph_type == "Barras":
            sns.barplot(
                x=bank_raw_target_perc.index,
                y="proportion",
                data=bank_raw_target_perc,
                ax=axes[0],
            )
            axes[0].bar_label(container=axes[0].containers[0])
            axes[0].set_title(label="Dados brutos", fontweight="bold")
            sns.barplot(
                x=bank_target_perc.index,
                y="proportion",
                data=bank_target_perc,
                ax=axes[1],
            )
            axes[1].bar_label(container=axes[1].containers[0])
            axes[1].set_title(label="Dados filtrados", fontweight="bold")
        else:
            bank_raw_target_perc.plot(
                kind="pie", autopct="%.2f", y="proportion", ax=axes[0]
            )
            axes[0].set_title("Dados brutos", fontweight="bold")
            bank_target_perc.plot(kind="pie", autopct="%.2f", y="proportion", ax=axes[1])
            axes[1].set_title("Dados filtrados", fontweight="bold")

        st.pyplot(plt)

if __name__ == '__main__':
	main()
    









