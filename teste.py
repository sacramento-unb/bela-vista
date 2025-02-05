import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static,st_folium

# streamlit -> Framework de desenvolvimento de dashboards interativos

# plotly -> Biblioteca de plotagem de gráficos

# folium -> Biblioteca de confecção de mapas

# streamlit_folium -> Biblioteca de integração do streamlit com o folium

# Funções de disposição de elementos na tela
st.title('MBA Inteligência de dados ambientais')

st.subheader('')

st.sidebar.title('Menu')

compact = st.sidebar.checkbox(label='Visualização compacta')

# Upload de um arquivo
arquivo_subido = st.sidebar.file_uploader('Selecione o arquivo a ser subido')

# Checagem para saber se o arquivo foi subido

EMBARGO = r'dados\embargos\adm_embargo_a.shp'


if arquivo_subido and compact is False:

# Elemento de seleção da visualização
    elemento = st.sidebar.radio('Selecione o elemento a ser visualizado',
                                options=['Mapa','Gráfico','Resumo','Cabeçalho'])

    # Leitura do aquivo na forma de uma geodataframe
    gdf = gpd.read_file(arquivo_subido)

    @st.cache_resource
    def abrir_embargo():
        gdf2 = gpd.read_file(EMBARGO)
        return gdf2
    
    gdf2 = abrir_embargo()
    #st.dataframe(gdf2.head())

    gdf2 = gdf2.drop(columns=['nom_pessoa','cpf_cnpj_i',
                            'cpf_cnpj_s','end_pessoa',
                            'des_bairro','num_cep','num_fone',
                            'data_tad','dat_altera','data_cadas',
                            'data_geom','dt_carga'])

    juntos = gpd.sjoin(gdf2,gdf,how='inner',predicate='intersects')

    #Conversão do geodataframe em um dataframe
    df = pd.DataFrame(juntos).drop(columns=['geometry'])
    
    # Criar funções para separar os elementos
    def resumo():
        # Divisão em colunas para melhor visualização
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(juntos,height=320)

        with col2:
            st.dataframe(juntos.describe(),height=320)

    def cabecalho():  
        st.dataframe(df)
        return cabecalho

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
        gdf1 = juntos.drop(columns=['dat_criaca','data_atual'])

        def style_function(x): return{
            'fillColor': 'blue',
            'color':'black',
            'weight':0,
            'fillOpacity':0.3
        }

        def style_function2(x): return{
            'fillColor': 'orange',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        # Plotagem do geodataframe no mapa
        folium.GeoJson(gdf,style_function=style_function).add_to(m)
        folium.GeoJson(gdf1,style_function=style_function2).add_to(m)
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


elif arquivo_subido and compact is True:

    # Leitura do aquivo na forma de uma geodataframe
    gdf = gpd.read_file(arquivo_subido)

    @st.cache_resource
    def abrir_embargo():
        gdf2 = gpd.read_file(EMBARGO)
        return gdf2
    
    gdf2 = abrir_embargo()
    #st.dataframe(gdf2.head())

    gdf2 = gdf2.drop(columns=['nom_pessoa','cpf_cnpj_i',
                            'cpf_cnpj_s','end_pessoa',
                            'des_bairro','num_cep','num_fone',
                            'data_tad','dat_altera','data_cadas',
                            'data_geom','dt_carga'])

    juntos = gpd.sjoin(gdf2,gdf,how='inner',predicate='intersects')

    #Conversão do geodataframe em um dataframe
    df = pd.DataFrame(juntos).drop(columns=['geometry'])

    col1_compact,col2_compact,col3_compact = st.columns(3)
    with col1_compact:
        st.markdown('Área média \n dos embargos')
        st.title(round(df.describe().loc['mean','qtd_area_e'],2))

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
#########################################################
    # Crio um mapa e seleciono algumas opções
    m = folium.Map(location=[-14,-54],zoom_start=4,control_scale=True,tiles='Esri World Imagery')
    
    # Deletando colunas do geodataframe
    gdf1 = juntos.drop(columns=['dat_criaca','data_atual'])

    def style_function(x): return{
        'fillColor': 'blue',
        'color':'black',
        'weight':0,
        'fillOpacity':0.3
    }

    def style_function2(x): return{
        'fillColor': 'orange',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
    }

    # Plotagem do geodataframe no mapa
    folium.GeoJson(gdf,style_function=style_function).add_to(m)
    folium.GeoJson(gdf1,style_function=style_function2).add_to(m)
    # Calculo o limite da geometria
    bounds = gdf1.total_bounds
    # Ajusto o mapa para os limites de geometria
    m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
    # Adiciona os controle de camadas no mapa
    folium.LayerControl().add_to(m)
    # Faço a plotagem do mapa no dashboard
    st_folium(m, width="100%")

else:
    st.warning('Selecione um arquivo para iniciar o dashboard')

