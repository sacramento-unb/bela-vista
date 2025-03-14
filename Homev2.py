import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static,st_folium
#from car_downloader import baixar_car
from zona_utm import calcular_utm
from PIL import Image
import os

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

# Funções de disposição de elementos na tela
st.title('POC - Bela vista floresta plantada')
st.write('')
st.write('')
st.sidebar.title('Menu')

fazendas_select = [_ for _ in os.listdir('fazendas') if _.endswith('.geojson')]

select_arquivo = st.sidebar.selectbox('Selecione a fazenda a ser visualizada',options=fazendas_select)

# Upload de um arquivo
arquivo_subido = os.path.join('fazendas',select_arquivo)

app_subida = os.path.join('fazendas',os.path.splitext(select_arquivo)[0]+'_app.gpkg')

compacto = st.sidebar.checkbox(label='Ativar modo compacto',value=True)

# Checagem para saber se o arquivo foi subido

EMBARGO = 'dados/embargos/embargos_ibama.parquet'
DESMATAMENTO = 'dados/mapbiomas/mapbiomas_alertas.parquet'
TIS = 'dados/tis_poligonais/tis.parquet'

if arquivo_subido and app_subida:
    poligono_analise = gpd.read_file(arquivo_subido)
    app_analise = gpd.read_file(app_subida)
    epsg = calcular_utm(poligono_analise)

if arquivo_subido and not compacto:

    # Elemento de seleção da visualização
    elemento = st.sidebar.radio('Selecione o elemento a ser visualizado',
                                options=['Mapa','Gráfico','Resumo','Cabeçalho'])
    # Leitura do aquivo na forma de uma geodataframe
    gdf = poligono_analise
    
    @st.cache_resource
    def abrir_embargo():
        gdf_embargo = gpd.read_parquet(EMBARGO)
        return gdf_embargo
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(DESMATAMENTO)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_tis():
        gdf_ti = gpd.read_parquet(TIS)
        return gdf_ti
    
    gdf_embargo = abrir_embargo()

    gdf_desmat = abrir_desmatamento()

    gdf_ti = abrir_tis()

    #st.dataframe(gdf_embargo.head())

    gdf_embargo = gdf_embargo.drop(columns=['nom_pessoa','cpf_cnpj_i',
                            'cpf_cnpj_s','end_pessoa',
                            'des_bairro','num_cep','num_fone',
                            'data_tad','dat_altera','data_cadas',
                            'data_geom','dt_carga'])

    entrada_embargo = gpd.sjoin(gdf_embargo,gdf,how='inner',predicate='intersects')

    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')

    entrada_ti = gpd.sjoin(gdf_ti,gdf,how='inner',predicate='intersects')


    #Conversão do geodataframe em um dataframe
    df_embargo = pd.DataFrame(entrada_embargo).drop(columns=['geometry'])

    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])

    df_ti = pd.DataFrame(entrada_ti).drop(columns=['geometry'])

    # Criar funções para separar os elementos
    def resumo():
        # Divisão em colunas para melhor visualização
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(df_embargo,height=320)
            st.dataframe(df_desmat,height=320)
            st.dataframe(df_ti,height=320)

        with col2:
            st.dataframe(df_embargo.describe(),height=320)
            st.dataframe(df_desmat.describe(),height=320)
            st.dataframe(df_ti.describe(),height=320)

    def cabecalho():
        st.subheader('Dados de embargo')
        st.dataframe(df_embargo)
        st.subheader('Dados de desmatamento')
        st.dataframe(df_desmat)
        st.subheader('Dados de Terras Indígenas')
        st.dataframe(df_ti)

    def grafico():
        col1_gra,col2_gra,col3_gra,col4_gra = st.columns(4)
        # Seleção do tipo de gráfico e uma opção padrão(index)
        tema_grafico = col1_gra.selectbox('Selecione o tema do gráfico',
                options=['Embargo','Desmatamento','Terras Indígenas'])
        
        if tema_grafico == 'Embargo':
            df_analisado = df_embargo
        elif tema_grafico == 'Desmatamento':
            df_analisado = df_desmat
        elif tema_grafico == 'Terras Indígenas':
            df_analisado = df_ti

        tipo_grafico = col2_gra.selectbox('Selecione o tipo de gráfico',
                        options=['box','bar','line','scatter','violin','histogram'],index=5)
        # Plotagem da função utilizando o plotly express
        plot_func = getattr(px, tipo_grafico)
        # criação de opções dos eixos x e y com um opção padrão
        x_val = col3_gra.selectbox('Selecione o eixo x',options=df_analisado.columns,index=6)

        y_val = col4_gra.selectbox('Selecione o eixo y',options=df_analisado.columns,index=5)
        # Crio a plotagem do gráfico
        plot = plot_func(df_analisado,x=x_val,y=y_val)
        # Faço a plotagem
        st.plotly_chart(plot, use_container_width=True)

    def mapa():
        # Crio um mapa e seleciono algumas opções
        m = folium.Map(location=[-14,-54],zoom_start=4,control_scale=True,tiles='Esri World Imagery')
        
        def style_function_entrada(x): return{
            'fillColor': 'blue',
            'color':'black',
            'weight':0,
            'fillOpacity':0.3
        }

        def style_function_embargo(x): return{
            'fillColor': 'orange',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        def style_function_desmat(x): return{
            'fillColor': 'red',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        def style_function_ti(x): return{
            'fillColor': 'yellow',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }
        # Plotagem do geodataframe no mapa
        gdf_limpo = gpd.GeoDataFrame(gdf,columns=['geometry'])
        folium.GeoJson(gdf_limpo,style_function=style_function_entrada).add_to(m)
        entrada_embargo_limpo = gpd.GeoDataFrame(entrada_embargo,columns=['geometry'])
        folium.GeoJson(entrada_embargo_limpo,style_function=style_function_embargo).add_to(m)
        entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
        folium.GeoJson(entrada_desmat_limpo,style_function=style_function_desmat).add_to(m)
        entrada_ti_limpo = gpd.GeoDataFrame(entrada_ti,columns=['geometry'])
        folium.GeoJson(entrada_ti_limpo,style_function=style_function_ti).add_to(m)
        # Calculo o limite da geometria
        bounds = gdf.total_bounds
        # Ajusto o mapa para os limites de geometria
        m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
        # Adiciona os controle de camadas no mapa
        folium.LayerControl().add_to(m)
        # Faço a plotagem do mapa no dashboard
        st_folium(m,width="100%")

    # Condicional para mostrar os elementos na tela
    if elemento == 'Cabeçalho':
        cabecalho()
    elif elemento == 'Resumo':
        resumo()
    elif elemento == 'Gráfico':
        grafico()
    elif elemento == 'Mapa':
        mapa()

elif arquivo_subido and app_subida and compacto:

    st.sidebar.selectbox('Selecione o relatório a ser gerado',options=[''])
    st.sidebar.button('Gerar Relatório')
    gdf = poligono_analise
    gdf_app = app_analise
    @st.cache_resource
    def abrir_embargo():
        gdf_embargo = gpd.read_parquet(EMBARGO)
        return gdf_embargo
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(DESMATAMENTO)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_tis():
        gdf_ti = gpd.read_parquet(TIS)
        return gdf_ti
    
    gdf_embargo = abrir_embargo()

    gdf_desmat = abrir_desmatamento()

    gdf_ti = abrir_tis()

    #st.dataframe(gdf_embargo.head())

    gdf_embargo = gdf_embargo.drop(columns=['nom_pessoa','cpf_cnpj_i',
                            'cpf_cnpj_s','end_pessoa',
                            'des_bairro','num_cep','num_fone',
                            'data_tad','dat_altera','data_cadas',
                            'data_geom','dt_carga'])

    entrada_embargo = gpd.sjoin(gdf_embargo,gdf,how='inner',predicate='intersects')

    entrada_embargo = gpd.overlay(entrada_embargo,gdf,how='intersection')

    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')

    entrada_desmat = gpd.overlay(entrada_desmat,gdf,how='intersection')

    entrada_ti = gpd.sjoin(gdf_ti,gdf,how='inner',predicate='intersects')

    entrada_ti = gpd.overlay(entrada_ti,gdf,how='intersection')
    #Conversão do geodataframe em um dataframe
    df_embargo = pd.DataFrame(entrada_embargo).drop(columns=['geometry'])

    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])

    df_ti = pd.DataFrame(entrada_ti).drop(columns=['geometry'])

    area_desmat = entrada_desmat.dissolve(by=None)

    area_desmat = area_desmat.to_crs(epsg=epsg)

    area_desmat['area'] = area_desmat.area / 10000



    area_embargo = entrada_embargo.dissolve(by=None)

    area_embargo = area_embargo.to_crs(epsg=epsg)

    area_embargo['area'] = area_embargo.area / 10000



    area_ti = entrada_ti.dissolve(by=None)

    area_ti = area_ti.to_crs(epsg=epsg)

    area_ti['area'] = area_ti.area / 10000

    card_columns1,card_columns2,card_columns3 = st.columns(3)

    with card_columns1:
        st.write('Área Total desmatada')
        if len(area_desmat) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_desmat.loc[0,'area'],2)))

    with card_columns2:
        st.write('Área Total de embargos')
        if len(area_embargo) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_embargo.loc[0,'area'],2)))

    with card_columns3:
        st.write('Área Total de Terras Indígenas')
        if len(area_ti) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_ti.loc[0,'area'],2)))

    card_columns4,card_columns5,card_columns6 = st.columns(3)

    with card_columns1:
        st.write('Área de Floresta plantada')
        if select_arquivo == 'Sítio Ebenezer.geojson':
            st.subheader('0')
        if select_arquivo == 'poc_test.geojson':
            st.subheader('5,97')

    with card_columns2:
        st.write('Excedente de Reserva legal')
        if select_arquivo == 'Sítio Ebenezer.geojson':
            st.subheader('0')
        if select_arquivo == 'poc_test.geojson':
            st.subheader('-0,02')

    with card_columns3:
        st.write('Área produtiva ociosa')
        st.subheader('0')

    m = folium.Map(location=[-14,-54],zoom_start=4,control_scale=True,tiles='Esri World Imagery')
    
    def style_function_entrada(feature):
        """Define a cor e estilo de preenchimento com base na classe da feição."""
        classe = feature.get('properties', {}).get('classe', '').strip().capitalize()  # Obtém e normaliza a classe
    
        # Mapeamento de cores por classe
        color_mapping = {
            'Floresta plantada': '#722F37',  # Cor vinho
            'Vegetação': '#228B22',     # Verde (ForestGreen)
            'Agricultura': '#FAE042'    # Amarelo claro
        }
    
        return {
            'fillColor': color_mapping.get(classe, 'grey'),  # Cor padrão: cinza
            'color': 'black',
            'weight': 0,
            'fillOpacity': 0.3
        }

    def style_function_app(feature):
        """Define a cor e estilo de preenchimento com base na classe da feição."""
        descricao = feature.get('properties', {}).get('descricao', '')  # Obtém e normaliza a descricao
    
        # Mapeamento de cores por descricao
        color_mapping = {
            'APP a recuperar': '#BE1A25',  # Cor vinho
            'APP preservada': 'green',     # Verde (ForestGreen)
            'APP Consolidada': 'grey'    # Amarelo claro
        }
    
        return {
            'fillColor': color_mapping.get(descricao, 'grey'),  # Cor padrão: cinza
            'color': 'black',
            'weight': 0,
            'fillOpacity': 1
        }


    def style_function_embargo(x): return{
        'fillColor': 'orange',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
    }

    def style_function_desmat(x): return{
        'fillColor': 'red',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
    }

    def style_function_ti(x): return{
        'fillColor': 'yellow',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
    }

    # Plotagem do geodataframe no mapa
    gdf_limpo = gpd.GeoDataFrame(gdf)
    folium.GeoJson(gdf_limpo,style_function=style_function_entrada).add_to(m)
    entrada_embargo_limpo = gpd.GeoDataFrame(entrada_embargo,columns=['geometry'])
    folium.GeoJson(entrada_embargo_limpo,style_function=style_function_embargo).add_to(m)
    entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
    folium.GeoJson(entrada_desmat_limpo,style_function=style_function_desmat).add_to(m)
    entrada_ti_limpo = gpd.GeoDataFrame(entrada_ti,columns=['geometry'])
    folium.GeoJson(entrada_ti_limpo,style_function=style_function_ti).add_to(m)
    app_limpa = gpd.GeoDataFrame(app_analise,columns=['geometry','descricao'])
    folium.GeoJson(app_limpa,style_function=style_function_app).add_to(m)
    # Calculo o limite da geometria
    bounds = gdf.total_bounds
    # Ajusto o mapa para os limites de geometria
    m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
    # Adiciona os controle de camadas no mapa
    folium.LayerControl().add_to(m)
    # Faço a plotagem do mapa no dashboard
    st_folium(m,width="100%")
    
    merc = 'dados/Subcabecalho.png'
    merc = Image.open(merc)
    merc = merc.resize((300, 200))
    st.image(merc, caption="Legenda", use_column_width=False)

    col1_graf,col2_graf,col3_graf,col4_graf = st.columns(4)

    tema_grafico = col1_graf.selectbox('Selecione o tema do gráfico',
                options=['Embargo','Desmatamento','Terras Indígenas'])

    if tema_grafico == 'Embargo':
        df_analisado = df_embargo
    elif tema_grafico == 'Desmatamento':
        df_analisado = df_desmat
    elif tema_grafico == 'Terras Indígenas':
        df_analisado = df_ti

    tipo_grafico = col2_graf.selectbox('Selecione o tipo de gráfico',
                    options=['box','bar','line','scatter','violin','histogram'],index=5)

    plot_func = getattr(px, tipo_grafico)
    # criação de opções dos eixos x e y com um opção padrão
    x_val = col3_graf.selectbox('Selecione o eixo x',options=df_analisado.columns,index=6)

    y_val = col4_graf.selectbox('Selecione o eixo y',options=df_analisado.columns,index=5)
    # Crio a plotagem do gráfico
    plot = plot_func(df_analisado,x=x_val,y=y_val)
    # Faço a plotagem
    st.plotly_chart(plot, use_container_width=True)

else:
    st.warning('Selecione um arquivo para iniciar o dashboard')
