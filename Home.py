import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# streamlit -> Framework de desenvolvimento de dashboards interativos

# plotly -> Biblioteca de plotagem de gráficos

# folium -> Biblioteca de confecção de mapas

# streamlit_folium -> Biblioteca de integração do streamlit com o folium

# Funções de disposição de elementos na tela
st.title('MBA Inteligência de dados ambientais')

st.subheader('Este é um dashboard de estudo')

st.sidebar.title('Menu')

# Upload de um arquivo
arquivo_subido = st.sidebar.file_uploader('Selecione o arquivo a ser subido')

# Elemento de seleção da visualização
elemento = st.sidebar.radio('Selecione o elemento a ser visualizado',
                                options=['Mapa','Gráfico','Resumo','Cabeçalho'])

# Checagem para saber se o arquivo foi subido

if arquivo_subido:
    # Leitura do aquivo na forma de uma geodataframe
    gdf = gpd.read_file(arquivo_subido)
    #Conversão do geodataframe em um dataframe
    df = pd.DataFrame(gdf).drop(columns=['geometry'])
    
    # Criar funções para separar os elementos
    def resumo():
        # Divisão em colunas para melhor visualização
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(gdf,height=320)

        with col2:
            st.dataframe(gdf.describe(),height=320)

    def cabecalho():  
        st.dataframe(df)

    def grafico():
        col1_gra,col2_gra,col3_gra = st.columns(3)
        # Seleção do tipo de gráfico e uma opção padrão(index)
        tipo_grafico = col1_gra.selectbox('Selecione o tipo de gráfico',
                        options=['box','bar','line','scatter','violin','histogram'],index=5)
        # Plotagem da função utilizando o plotly express
        plot_func = getattr(px, tipo_grafico)
        # criação de opções dos eixos x e y com um opção padrão
        x_val = col2_gra.selectbox('Selecione o eixo x',options=df.columns,index=6)

        y_val = col3_gra.selectbox('Selecione o eixo y',options=df.columns,index=5)
        # Crio a plotagem do gráfico
        plot = plot_func(df,x=x_val,y=y_val)
        # Faço a plotagem
        st.plotly_chart(plot, use_container_width=True)

    def mapa():
        # Crio um mapa e seleciono algumas opções
        m = folium.Map(location=[-14,-54],zoom_start=4,control_scale=True,tiles='Esri World Imagery')
        # Deletando colunas do geodataframe
        gdf1 = gdf.drop(columns=['dat_criaca','data_atual'])
        # Plotagem do geodataframe no mapa
        folium.GeoJson(gdf1).add_to(m)
        # Calculo o limite da geometria
        bounds = gdf1.total_bounds
        # Ajusto o mapa para os limites de geometria
        m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
        # Adiciona os controle de camadas no mapa
        folium.LayerControl().add_to(m)
        # Faço a plotagem do mapa no dashboard
        folium_static(m,width=700,height=500)

    # Condicional para mostrar os elementos na tela
    if elemento == 'Cabeçalho':
        cabecalho()
    elif elemento == 'Resumo':
        resumo()
    elif elemento == 'Gráfico':
        grafico()
    elif elemento == 'Mapa':
        mapa()
else:
    st.warning('Selecione um arquivo para iniciar o dashboard')

