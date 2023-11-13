import os
import pdfplumber
import csv
import re
from datetime import datetime
import pandas as pd

def dividir_nombres(nombre):
    nombres = nombre.split()
    todojunto = ["","","",""]
    conta = 0
    
    i = 0
    while i < len(nombres):
        if nombres[i] in ["DE", "DEL", "LA", "LAS"] and conta < 4:
            if nombres[i+1] in ["DE", "DEL", "LA", "LAS"]:
                todojunto[conta] += nombres[i] + " " + nombres[i + 1] + " " + nombres[i + 2]
                i += 3
            elif i + 1 < len(nombres):
                todojunto[conta] += nombres[i] + " " + nombres[i + 1]
                i += 2
            else:
                todojunto[conta] += nombres[i]
                i += 1
        elif conta < 4:
            todojunto[conta] += nombres[i]
            i += 1
        else:
            todojunto[3] += " " + nombres[i]
            i+=1
        conta += 1
        # else:
        #     break
    #print (todojunto)
    #nameylastname = todojunto.spl
    return todojunto[2], todojunto[3], todojunto[0], todojunto[1]

def dividir_por_delimitadores(delimitadores, texto):
    for delimitador in delimitadores:
        if delimitador in texto:
            partes = texto.rsplit(delimitador, 1)
            if "X" in partes[1]:
                cedula = partes[1].split("X")[0].strip()
            else:
                cedula = partes[1].strip()
            return partes[0], cedula
    return texto, ""

# Carpeta que contiene los archivos PDF
#carpeta_raiz = "C:/Users/nacho/Downloads/davud/Autofinal/CORRECCIOES_PREDIOS_ANTES/"
carpeta_raiz = "C:/Users/nacho/Downloads/davud/Autofinal/11-11-2023/"

# Nombre del archivo CSV de salida
archivo_csv = carpeta_raiz+"nombres_cedulas.csv"
# Cargar el archivo CSV
df = pd.read_csv('Data_generos.csv', sep=';')

# Listas para almacenar los nombres y cédulas
nombres = []
primer_nombre  = []
segundo_nombre = []
primer_apellido = []
segundo_apellido = []
cedulas = []
anotacionesfuera = ["CANCELACION",
                    "PARCIAL",
                    "EMBARGO",
                    "DEMANDA EN PROCESO",
                    "ACLARACION",
                    "FALSA TRADICION",
                    "ESTA ANOTACION NO TIENE VALIDEZ",
                    "PATRIMONIO DE FAMILIA",
                    "DECLARACION DE MEJORAS",
                    "ADJUDICACION EN SUCESION",
                    "COMPRAVENTA DERECHOS DE CUOTA"]

anotacionessiosi = ["COMPRAVENTA (MODO DE ADQUISICION)",
                    "LOTEO (OTRO)"]

delimitado_cedula = [" CC "," TI ", " NIT. ","(ME X","(MENOR) X"," (MENOR) X", " X", " # "]

count_pdfs = 0
# Itera a través de los archivos PDF en la carpeta
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        folio = archivo_pdf.split("-")[1].split(" ")[0] if "-" in archivo_pdf and " " in archivo_pdf else None # Obtener el número del nombre del archivo PDF
        if archivo_pdf.endswith(".pdf") and ("J" in archivo_pdf or "j" in archivo_pdf):
            pdf_path = os.path.join(subdir, archivo_pdf)

            with pdfplumber.open(pdf_path) as pdf:
                page = None  # Página actual
                encontrado_x = False  # Indica si se ha encontrado " X "
                encontrado_an = False # Indica si se ha encontrado "ANOTACION"
                encontrado_de = False # Indica si se ha encontrado un "DE:"
                encontrado_nr2 = False # Indica si ya pasó por la anotacion nro 2
                encontrado_nohaymas = False #Cuando solo queda por validar anotacion 1, este está en true
                count_anotacion = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                count_anotacion_nro_1 = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                anot1 = False
                bool_A = True
                numeros_cancelados = []
                nuevos_numeros = []
                numero = 0
                count_nr1_a = 0
                contador = 0
                texto_lineas = []  # Almacena el texto de las líneas relevantes
                nombres = []  # Lista para almacenar los nombres
                cedulas = []  # Lista para almacenar las cédulas
                ph = "NO"
                # if folio == "33226":
                #     print ("Hola")
                tipo_servidumbre = ""
                compraventa = 100000000            #Para agregar una anotacion solo cuando salga esta palabra
                sianotacion = False
                pag_encontrado = ""             #para guardar la página en la que se encontró la anotacion clave
                entrarsiosi = False             #Para cuando quiero que guarde una anotacion si o si
                resultado = False
                n_anotacion = ''
                # derechoscuota = False           #Para cuando hay derechos de cuota que toca cambiar 
                # nombres_de = []
                # cedulas_de = []
                
                for page in reversed(pdf.pages):
                    # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                    lines = page.extract_text().splitlines()
                    for line in lines:
                        if "Doc: ESCRITURA" in line:
                            escrotura_match = re.search(r'ESCRITURA(.*?)(\d+):', line)
                            n_escrotora = escrotura_match.group(1).strip() if escrotura_match else None
                        if "ANOTACION" in line:
                            count_anotacion += 1
                            if " Nro 1 " in line:
                                count_anotacion_nro_1 = True
                            # Extraer el número después de "ANOTACION:"
                            anotacion_match = re.search(r'ANOTACION: Nro (\d+)', line)
                            n_anotacion = int(anotacion_match.group(1)) if anotacion_match else None
                        if count_anotacion_nro_1 and "A:" in line or count_nr1_a == 0 and "DE:" in line:
                            count_nr1_a += 1
                        if re.search(r"servidumbre", line, re.IGNORECASE):
                            tipo_servidumbre_match = re.search(r'SERVIDUMBRE(.*?)\(LIMITACION AL DOMINIO\)', line)
                            tipo_servidumbre = tipo_servidumbre_match.group(1).strip() if tipo_servidumbre_match.group(1).strip() else "TRANSITO"      
                            n_escritura_servidumbre = n_escrotora              
                        elif tipo_servidumbre == "":
                            tipo_servidumbre = "NO"
                        if re.search(r"horizontal", line, re.IGNORECASE):
                            ph = "SI"
                        if any(keyword in line for keyword in anotacionessiosi) and (pag_encontrado == page or sianotacion == False):
                            compraventa = n_anotacion
                            sianotacion = True
                            pag_encontrado = page
                    if n_anotacion == compraventa:
                        encontrado_nohaymas = True
                        entrarsiosi = True
                        
                        

                # Comprobar si "ANOTACION: Nro 1" se encontró y "ANOTACION" aparece más de una vez
                resultado = count_anotacion_nro_1 == 1 and count_anotacion == 1

                for page in reversed(pdf.pages):
                    if encontrado_x and encontrado_an:
                        encontrado_x = False
                        encontrado_an = False
                        break  # Si " X " ya se encontró, detén la iteración

                    lines = page.extract_text().splitlines()
                    #print (lines)

                    for line in reversed(lines):
                        # if "ANTONIO MARIA" in line:
                        #     print ("tons")
                        if "DE:" in line:           #para poder guardar un párrafo solo cuando tenga "DE:"
                            encontrado_de = True
                        elif any(keyword in line for keyword in anotacionesfuera) and ('SANEAMIENTO' not in line) and encontrado_nohaymas == False:      #CANCELACION", "PARCIAL", "EMBARGO", "DEMANDA EN PROCESO", "ACLARACION", "FALSA TRADICION"
                            encontrado_de = False
                        elif "Se cancela anotación No: " in line:
                            # Buscar números después de "No:"
                            nuevos_numeros = [numero.strip() for numero in line.split("No: ")[1].split(",")]
                            numeros_cancelados = numeros_cancelados + nuevos_numeros
                        
                        if ("A:" in line or "DE:" in line) and encontrado_nr2:
                            encontrado_nr2 = encontrado_de = True
                            
                            # Verificar si existe "ANOTACION: Nro " seguido de los números cancelados
                        for numero in numeros_cancelados:
                            if f"ANOTACION: Nro {numero}" in line:
                                encontrado_de = False
                                break  # Puedes detener la búsqueda una vez que se cumple la condición
                        
                        if resultado: #PARA LOS CASOS EN QUE NO HAYAN MAS ANOTACIONES MAS QUE LA PRIMERA Y ASEGURAR QUE GUARDE ALGUN PROPIETARIO
                            encontrado_nohaymas = True
                            if bool_A and "DE:" in line:
                                anot1 = True
                            elif "A:" in line:
                                bool_A = False

                        if (" X" in line and "A:" in line) or (resultado and "A:" in line) or anot1 or encontrado_nr2 or (entrarsiosi and "A:" in line):# and not encontrado_x:
                            encontrado_x = True
                            encontrado_nr2 = False
                            #print (line)

                            # TRATAMIENTO DE DATOS PARA LA CÉDULA Y NOMBRE
                            nombre = line[3:]
                            nombre, cedula = dividir_por_delimitadores(delimitado_cedula, nombre)
                            if resultado: #sirve para cuando solo hay una anotación nro 1.
                                contador += 1
                                if count_nr1_a == contador:
                                    resultado = False
                                    anot1 = False
                                    contador = 0
                                    count_nr1_a = 0
                                    encontrado_de = True

                            nombres.append(nombre)
                            cedulas.append(cedula)
                            texto_lineas.insert(0, line)
                        elif encontrado_x and "ANOTACION" not in line:
                            texto_lineas.insert(0, line)
                            #print ("texto_lineas ->> ",texto_lineas)
                        elif encontrado_x and "ANOTACION" in line:
                            if encontrado_de:
                                encontrado_an = True
                                encontrado_de = False
                                entrarsiosi = False
                                texto_lineas.insert(0, line)
                                break
                            else:
                                # for lineas in texto_lineas:
                                #     if "COMPRAVENTA DERECHOS DE CUOTA" in lineas:
                                #         derechoscuota = True
                                #         nombres_de_a = nombres
                                #     elif derechoscuota and "DE:" in lineas:
                                #         nombre_de = lineas[3:]
                                #         nombre_de, cedula_de = dividir_por_delimitadores(delimitado_cedula, nombre_de)
                                #         nombres_de.append(nombre_de)
                                        
                                encontrado_x = False
                                nombres = []
                                cedulas = []
                                texto_lineas = []
                        if "ANOTACION" in line:
                            encontrado_de = False
                        # if folio == '32897':
                        #     print ("hola")
                        if (" Nro 2 " in line) or (f" Nro {compraventa+1} " in line):
                            encontrado_nr2 = True
                            encontrado_nohaymas = True
                            
                # Combinar nombres y cédulas en una sola celda con saltos de línea
                #print (nombres)
                # nombres_celda = "\n".join(nombres)
                # cedulas_celda = "\n".join(cedulas)
                
                texto_celda = "\n".join(texto_lineas)
                
                if texto_celda != '':
                    # Buscar la primera fecha en formato DD-MM-AAAA
                    date_registro_match = re.search(r'\d{2}-\d{2}-\d{4}', texto_celda)
                    date_registro = date_registro_match.group(0) if date_registro_match else None

                    # Buscar la primera fecha en formato AAAA-MM-DD después del primer salto de línea
                    date_documento_match = re.search(r'DEL (\d{4}-\d{2}-\d{2}) ', texto_celda)
                    date_documento = date_documento_match.group(1) if date_documento_match else None
                    # if folio == '32666':
                    #     print ('error fecha->>',folio)
                    date_documento = datetime.strptime(date_documento, "%Y-%m-%d").strftime("%d-%m-%Y")

                    # Buscar la primera palabra después de "Doc: "
                    escritura_match = re.search(r'Doc: (\w+)', texto_celda)
                    escritura = escritura_match.group(1) if escritura_match else None

                    # Buscar el primer número después del primer salto de línea
                    n_escritura_match = re.search(r'(\w+) DEL', texto_celda)
                    n_escritura = n_escritura_match.group(1) if n_escritura_match else None
                        
                    # Buscar la cadena de caracteres entre "00:00:00 " y " VALOR"
                    ente_match = re.search(r':(\d+) (.*?) VALOR', texto_celda)
                    if ente_match:
                        ente = ente_match.group(2).upper()
                        if "JUZGADO" not in ente:
                            # Divide la cadena en dos partes usando " DE " como delimitador
                            ente_partes = ente.split(" DE ", 1)

                            # Reordena las partes y las une en una sola cadena
                            ente = ente_partes[1] +" "+ ente_partes[0]
                        elif ("PRIMERO" or "SEGUNDO") in ente:
                            ente = ente.replace("PRIMERO", "001")
                            ente = ente.replace("SEGUNDO", "002")
                        else:
                            ente = ente.replace("JUZGADO", "JUZGADO 001")
                            
                    else:
                        ente = None
                    
                    primer_nombre = []
                    segundo_nombre = []
                    primer_apellido = []
                    segundo_apellido = []
                    genero = []

                    # Dividir nombres en primer nombre, segundo nombre, primer apellido y segundo apellido
                    #print ("nombres_celda-> ",nombres_celda)
                    if nombres != "":
                        i=0
                        while i < len(nombres):
                            pn, sn,pa, sa = dividir_nombres(nombres[i])
                            pn = pn.strip()
                            sn = sn.strip()
                            pa = pa.strip()
                            sa = sa.strip()
                            
                            # if derechoscuota:
                            #     cuenta = 0
                            #     for o in nombres_de:
                            #         if (pn in o or sn in o) and (pa in o or sa in o):
                            #             pn, sn,pa, sa = dividir_nombres(nombres_de_a[cuenta])
                            #             pn = pn.strip()
                            #             sn = sn.strip()
                            #             pa = pa.strip()
                            #             sa = sa.strip()
                            #         cuenta += 1
                                    
                            # Buscar el género correspondiente en el DataFrame
                            #filtro = (df['primernombre'].str.strip() == pn) & (df['segundonombre'].str.strip() == sn)
                            varios_name = False
                            while True:
                                if varios_name == False:
                                    filtro = (df['primernombre'].str.strip() == pn)
                                else:
                                    filtro = (df['primernombre'].str.strip() == sn)
                                resultados = df[filtro]

                                # Verificar si se encontraron coincidencias
                                if not resultados.empty:
                                    genero_encontrado = resultados['sexo'].unique()
                                    if len(genero_encontrado) == 1:
                                        genero.append(genero_encontrado[0])
                                        break
                                    else:
                                        varios_name = True
                                        #genero.append("Nombre ambiguo, revisar")
                                else:
                                    genero.append("No se encontró información de género")
                                    break
                                
                            primer_nombre.append(pn)
                            segundo_nombre.append(sn)
                            primer_apellido.append(pa)
                            segundo_apellido.append(sa) 
                            i += 1
                        
                        for page in reversed(pdf.pages):
                            # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                            lines = page.extract_text().splitlines()
                            for line in reversed(lines):
                                for i in range(len(primer_nombre)):
                                    if (primer_nombre[i] in line or segundo_nombre[i] in line) and (primer_apellido[i] in line or segundo_apellido[i] in line):
                                        # Buscar cualquier número con más de dos dígitos en la línea
                                        matches = re.findall(r'\b\d{3,}\b', line)
                                        if matches and cedulas[i] == "":
                                            cedulas[i] = matches[0]  # Asignar el primer número de más de dos dígitos como cédula
                        
                else:
                    ph = 'COLOCAR DATOS MANUALMENTE'

                # Guardar los datos en el archivo CSV si se encontró " X "
                with open(archivo_csv, "a", newline="", encoding="utf-8") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Agregar encabezados si el archivo está vacío
                    if os.path.getsize(archivo_csv) == 0:
                        csv_writer.writerow(["Nombre de archivo","Folio", "Servidumbre","Escr. Serv", "PH","Texto", "Fecha registro","Fecha documento","Fuente adm.","N. Fuente","Ente Em.","Cédulas", "Primer Nombre", "Segundo Nombre", "Primer Apellido", "Segundo Apellido","Género"])
                    
                    if primer_nombre == []:
                        print ("No hay nadaaaaaaa, archivo: ", archivo_pdf)
                    
                    # Agregar los datos del archivo PDF actual
                    i = 0
                    if len(nombres) == 0:
                        print("No se agregó foliooooo: ",folio)
                    else:
                        count_pdfs += 1
                    while i < len(nombres):
                        if i == 0:
                            csv_writer.writerow([archivo_pdf,folio, tipo_servidumbre,n_escritura_servidumbre, ph, texto_celda,date_registro,date_documento,escritura,n_escritura,ente, cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i],genero[i]])
                        else:
                            csv_writer.writerow(["", folio,"","","","", "","","","", "",cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i],genero[i]])
                        i += 1

                # Limpiar las listas para el próximo archivo PDF
                nombres.clear()
                cedulas.clear()
                texto_lineas.clear()

print(f"Se ha analizado y guardado la información en {archivo_csv} de {count_pdfs} PDFs")
