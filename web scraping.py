""""
/*******************************************************************************
 *
 * web scraping.py (web scraping a un sitio web de un supermercado)
 *
 * Programador: Jaime Orellana Esquivel
 *
 * Santiago de Chile, 03/03/2025
 *
 * **************************************************************************"""

from bs4 import BeautifulSoup as bs #importación de la libería beautifulsoup que sirve para hacer scraping, se usará bajo el alias de "bs"
import time #libería para detener la ejecución del programa (el objetivo es esperar que se carguen los elementos)
from selenium import webdriver #librería selenium que sirve para navegar mientras se hace scraping (extraer información)
from selenium.webdriver.common.by import By #libería selenium para buscar elementos en una página web
import re #librería para expresiones regulares
import pandas as pd #librería que será util para exportar .xlsx a partir de listas bidimensionales

def eliminar_repetidos_lista(lista_productos): #elimina las filas que se repiten

    productos_no_repetidos = []

    for sublista_productos in lista_productos:

        if sublista_productos not in productos_no_repetidos:

            productos_no_repetidos.append(sublista_productos)

    return productos_no_repetidos

def exportar_excel(lista, nombre_fichero): #exportación a .xlsx a partir de una lista bidimensional

	pd.DataFrame(lista).to_excel(str(nombre_fichero), header=False, index=False) #tiene de argumento la lista y el nombre del fichero a exportar

head = {"User-Agent": "Mozilla/5.0"} #cabecera (se usa en beatifulsoup)
url = "https://www.unimarc.cl"
driver = webdriver.Chrome() #se abre google chrome
driver.maximize_window() #maximiza la ventana
driver.get(url) #ingresa a la página de unimarc
time.sleep(5) #delay de 5 segundos
div_categoria = driver.find_element(By.XPATH, ".//p[contains(text(), 'Categorías')]") #busca los elementos <p> que contenga la palabra "Categorías"
div_categoria.click()
time.sleep(3) #delay de 3 segundos
soup = bs(driver.page_source,"html.parser") #se llama beautiful soup para que busque todos los elementos <a> con enlaces href
links = soup.find_all('a',href=True)

lista_links = [] #inicializa lista_links

for link in links: #filtra todos los enlaces que no comienzan con "/category/"

    if link['href'][:10] == "/category/":

        lista_links.append(str(link['href'])) #apunta al atributo href

    """
    la lista con enlaces se compone de los siguientes href:

    /category/bebes-y-ninos
    /category/bebidas-y-licores
    /category/carnes
    /category/congelados
    /category/congelados/hamburguesas-apanados-y-churrascos/hamburguesas?brands=la-crianza
    /category/desayuno-y-dulces
    /category/despensa
    /category/despensa/harina-y-reposteria/harina?brands=mont-blanc
    /category/frutas-y-verduras
    /category/hogar
    /category/lacteos-huevos-y-refrigerados
    /category/limpieza
    /category/mascotas
    /category/panaderia-y-pasteleria
    /category/perfumeria
    /category/quesos-y-fiambres
    """

lista_links = list(set(lista_links)) #conversión a lista
lista_links.sort() #ordena de manera ascendente
productos=[]
productos.append(["Categoría","Nombre producto","Id","Precio (CLP)"]) #se agrega la primera fila que indica las caracteristicas de cada columna

for k in range(len(lista_links)): #va a recorrer todas las categorías y las va a recolectar en la lista productos
    
    driver.get(url+str(lista_links[k])) #se prepara para el k-ésimo enlace
    time.sleep(5) #delay de 5 segundos
    parrafos = driver.find_elements(By.TAG_NAME, "p") #pregunta por todos los elementos <P> pero usando By, ya que beautifulsoup hace scraping cuando el código es estático 
    texto_resultado = r"\(\d+ resultados\)" #es el patrón que se busca, la forma génerica para encontrar el valor de X cuando se desconoce por (X resultados), ejemplo: X = 83
    
    for parrafo in parrafos: #recorre todos los textos de elemento <p>

        if re.search(texto_resultado, parrafo.text): #cuando encuentra la coincidencia

            texto = parrafo.text #iguala una variable
            numero = texto.split(' ')[0] #separa el (X Resultados) en "(X"
            numero = int(numero[1:]) #quita el "(" para que se quede el valor X
            break

    paginas = int(numero/50) #la página esta diseñada para que muestre entre 0 a 50 productos, toma un numero entero para calcular la cantidad de paginas

    if numero % 50 > 0: #cuando los productos son entre 1 y 49

        paginas=paginas+1

    elif numero == 0:#en caso que no haya resultados
            
        paginas = 0

    else: #las paginas no pueden ser negativas
        print("error")

    for pagina in range(paginas): #recorre desde la pagina 1 hasta la útlima

        if pagina == 0: #en caso que no haya página

            pass

        else:
            """
            Inspeccionando elemento uno puede saber las clases que nos interesan para el scraping

            la clase "Text_text--primary__OoK0C" indica el precio en color rojo, que es el precio final
            la clase "Text_text--black__zYYxI precio negro" indica el valor c/u cuando el precio final empieza con "2x" o "3x"
            la clase "Shelf_nameProduct__CXI5M" indica el nombre del producto
            la clase "Shelf_defaultImgStyle__ylyx2" indica el Id de la imagen que aparece en el catálogo, estaba la opción de colocar el código de barra pero tenía caracteres
            """
            time.sleep(5) #delay de 5 segundos
            driver.get(url+str(lista_links[k])+"?page="+str(pagina)) #recorre las paginas de la k-ésima categoría
            time.sleep(10) #10 segundos de delay para que carguen los elementos
            lista_precios=[] #inicializa la lista con precios
            lista_precios_rojo=[] #inicializa la lista con precios finales que están en rojo
            lista_precios_negro=[] #inicializa la lista con el valor de c/u cuando los precios en rojo indican promocion tipo "2x" o "3x"
            precios_rojos = driver.find_elements(By.XPATH, "//div[contains(@class, 'baseContainer_container__TSgMX')]//p[contains(@class, 'Text_text--primary__OoK0C')]") #busca todos los elementos que contienen la clase precio rojo
            for precio in precios_rojos:

                texto = precio.text
                lista_precios_rojo.append(str(texto)) #agrega a una lista de solo rojos

            precios_negros = driver.find_elements(By.XPATH, "//div[contains(@class, 'baseContainer_container__TSgMX')]//p[contains(@class, 'Text_text--black__zYYxI')]") #busca todos los elementos que contienen la clase precio negro

            for precio in precios_negros:

                if str(precio.text).endswith("c/u"): #pregunta por los precios que son c/u ya que el precio rojo indica promoción

                    texto = precio.text
                    lista_precios_negro.append(str(texto)) #agrega a una lista de solo negros

            j=0 #se inicializa en j=0 para avanzar la lista de los negros mientras avanza el rojo

            for i in range(len(lista_precios_rojo)):

                if str(lista_precios_rojo[i]).startswith("$"): #discrimina si el precio es o no promoción "2x" o "3x"

                    lista_precios.append(str(lista_precios_rojo[i]).replace('.', '').replace('$', '')) #remueve la "," y el signo "$"

                else:

                    lista_precios.append(str(lista_precios_negro[j][:-4]).replace('.', '').replace('$', '')) #remueve la "," y el signo "$"
                    j = j+1 #avanza la iteración en la lista de los precios negros

            lista_nombres = [] #se inicializa la lista de nombres
            nombre_productos = driver.find_elements(By.XPATH, "//div[contains(@class, 'baseContainer_container__TSgMX')]//p[contains(@class, 'Shelf_nameProduct__CXI5M')]") #pregunta por la clase que contiene el nombre del producto

            for nombre in nombre_productos: #itera los nombres de los productos
                
                texto = nombre.text
                lista_nombres.append(str(texto)) #se agrega a una lista

            lista_ids = [] #se inicializa la lista de ids
            nombre_ids = driver.find_elements(By.XPATH, "//div[contains(@class, 'baseContainer_container__TSgMX')]//img[contains(@class, 'Shelf_defaultImgStyle__ylyx2')]")  #pregunta por la clase que contiene la imagen del producto

            for id in nombre_ids: #recorre los ids de los elementos encontrados
                
                numero_id = id.get_attribute('src') #extrae el atributo source que es el link de la imagen
                numero_id = str(numero_id) #se pasa a string
                numero_id = re.search(r"ids/(\d+)", numero_id) #se ocupa expresiones regulares para quitar el Id que pertenece a la imagen, no quise poner código de barra ya que un Id numérico tiende a ser entero
                numero_id = str(numero_id.group(1)) #separa el segundo elemento ya que ej: https://unimarc.vtexassets.com/arquivos/ids/244254/000000000000645361-UN-01.jpg?v=638627860538970000 -----> /ids/244254 ----> 244254
                lista_ids.append(str(numero_id)) #se agrega a la lista de ids

            categoria = (str(lista_links[k]).split('/')[2]).replace('-', ' ') #en las categorías se reemplazan los guiones por espacios
            
            for i in range(len(lista_ids)): #se recorre la lista de ids, pero en realidad puede ser cualquiera ya que tanto la de nombres y precios tienen la misma longitud
                
                productos.append([categoria,lista_nombres[i],lista_ids[i],lista_precios[i]]) #se agregan los nuevos elementos a la lista productos.


productos = eliminar_repetidos_lista(productos)#llama a funcion que elimina las filas repetidas

print("exportando excel...")
exportar_excel(productos,"lista_unimarc.xlsx") #exporta el .xlsx
print("excel exportado con exito!")    #finaliza el programa una vez que se exporta el excel

"""
el archivo "lista_unimarc.xlsx" tiene la siguiente estructura

Catergoría	        Nombre producto	                                            Id	        Precio (CLP)
bebes y ninos	    Pañal babysec super premium confort care talla xxg 112 un	246319	    30990
bebes y ninos	    Pants pampers premium care xxg 104 un	                    232174	    37990
bebes y ninos	    Pañal pampers premium care hipoalergénico talla xxg 128 un	244254	    39990
bebes y ninos	    Pañal babysec super premium confort care talla xg 112 un	246318	    30990
.                   .                                                           .           .
.                   .                                                           .           .
.                   .                                                           .           .
quesos y fiambres	Queso ferrari grana padano 200 g	                        218975	    9150
"""

