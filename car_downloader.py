import requests
import geopandas as gpd
from io import BytesIO

def baixar_car(cod_imovel):
    state = cod_imovel.lower()[0:2]

    url = 'https://geoserver.car.gov.br/geoserver/sicar/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sicar:sicar_imoveis_'+state+'&outputFormat=application/json&cql_filter=cod_imovel='+'\''+cod_imovel+'\''
    print(url)

    r = requests.get(url,allow_redirects=True,verify=False)

    gdf = gpd.read_file(BytesIO(r.content))

    gdf.to_file(r'E:\POC - Pirancajuba\dados\teste.gpkg', driver='GPKG', layer='name')  

    return gdf


if __name__ == '__main__':  
    baixar_car('GO-5203302-E8887537E89949728A0BA3BA3F94516C')
