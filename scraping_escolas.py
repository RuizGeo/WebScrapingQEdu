#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:20:36 2019

@author: root
"""


from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import re
import geopandas as gpd
import pandas as pd
import geocoder
import pycep_correios
import numpy as np


#Url qedu
qedu='https://www.qedu.org.br'
#Qedu municipio
url_rio_branco="https://www.qedu.org.br/busca/101-acre/3070-rio-branco"


def obterUrlEscolas(link):
    #request
    page = requests.get(link)
    print('page.status_code:',page.status_code)
     #Criar objeto bs4
    bsObj=BeautifulSoup(page.content, 'html.parser')
    #Encontrar as urls das escolas
    urlSchools=bsObj.findAll("a",{"href":re.compile("(/escola/)")})
    #print len
    print('Len: ',len(urlSchools))   
    #criar listas com as urls
    listUrls=[url['href']   for url in urlSchools]
    return listUrls

def obterDadosEscola(url_qedu,list_urls):
    #iniciar os data set
    dados=np.recarray((len(list_urls)),dtype=([('Lat', np.float32),('Long', np.float32),('Rua', '<U40'), ('CEP', '<U10'),('Depend', '<U40'),('Func', np.float16),('Anos_ini', np.float16),('Anos_fins', np.float16),('EJA', np.float16),('Ed_espe', np.float16),('Ens_med', np.float16),('INEP', np.int32)]))
    
    #listas
    list_end=[]
    list_cod_inep=[]
    #loop urls
    for i, url in enumerate(list_urls):
        #request
        page = requests.get(url_qedu+url+'/sobre')
        print('#################')
        print(url_qedu+url)
        print('page.status_code:',page.status_code)
        #Criar objeto bs4
        bsObj=BeautifulSoup(page.content, 'html.parser')
        #Encontrar as urls das escolas
        table= bsObj.findAll("table",{"class":"table table-striped"})
        for t in table:
            #loop linhas
            for  row in t.select('tr'):
                if 'Endereço' in row.select('th')[0].text.strip():
                    endereco=row.select('td')[0].text.split('RAMAL')[0].split('Bairro')[0].split('CEP')[0].strip()
                    cep=row.select('td')[0].text.split('CEP:')[-1].strip()
                    #print('CEP: ',pycep_correios.consultar_cep(cep))
                if 'Código INEP' in row.select('th')[0].text.strip():
                    print(row.select('th')[0].text.strip())
                    inep=row.select('td')[0].text.strip()
                if 'Dependência' in row.select('th')[0].text.strip():
                    print(row.select('td')[0].text.strip())
                    depend = row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.stri
                if 'Funcionários' in row.select('th')[0].text.strip():
                    func=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
                if 'iniciais' in row.select('th')[0].text.strip():
                    iniciais=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
                if 'finais' in row.select('th')[0].text.strip():
                    finais=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
                if 'Médio' in row.select('th')[0].text.strip():
                    medio=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
                if 'Jovens' in row.select('th')[0].text.strip():
                    eja=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
                if 'Educação Especial' in row.select('th')[0].text.strip():
                    especial=row.select('td')[0].text.strip()
                    #list_cod_inep.append(row.select('td')[0].text.strip())
        #Geocode
        try:                 
                g = geocoder.osm(str(endereco).lower()+', Rio Branco, Acre, Brazil')
                geocod=g.osm
                #Inserir dados
                dados['Long'][i]=geocod['x']
                dados['Lat'][i]=geocod['y']
                dados['Rua'][i]=geocod['addr:street']
                dados['CEP'][i]=cep
                dados['Depend'][i]=depend
                dados['Func'][i]=func
                dados['Anos_fins'][i]=finais
                dados['Anos_ini'][i]=iniciais
                dados['EJA'][i]=eja
                dados['Ed_espe'][i]=especial
                dados['Ens_med'][i]=medio
                dados['INEP'][i]=inep
               
                
                
                
        except:
                 #Inserir dados
                    dados['Long'][i]=np.nan
                    dados['Lat'][i]=np.nan
                    dados['Rua'][i]=np.nan
                    dados['CEP'][i]=np.nan
                    dados['Depend'][i]=np.nan
                    dados['Func'][i]=np.nan
                    dados['Anos_fins'][i]=np.nan
                    dados['Anos_ini'][i]=np.nan
                    dados['EJA'][i]=np.nan
                    dados['Ed_espe'][i]=np.nan
                    dados['Ens_med'][i]=np.nan
                    
    #return
    return dados

#Obter as urls das escolas do municipio
listUrls = obterUrlEscolas(url_rio_branco)       
#loop escolas
dados=obterDadosEscola(qedu,listUrls)
#get name tags
#out shapefile
out='/media/ruiz/Novo volume/MEGAsync/CEMADEN/SHP/escolas.shp'
#CReate DataFrame
df=pd.DataFrame(dados)
#del(dados)
#Drop  na
df.dropna(inplace=True)
#Create geopandas
gdf = gpd.GeoDataFrame( df, geometry=gpd.points_from_xy(df.Long, df.Lat))
#write shapefile
gdf.to_file(out)

    
