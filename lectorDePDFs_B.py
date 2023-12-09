import os
import pdfplumber
import csv
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Carpeta que contiene las subcarpetas con los archivos PDF
#carpeta_raiz = "C:/Users/nacho/Downloads/davud/Autofinal/CORRECCIOES_PREDIOS_ANTES/"
carpeta_raiz = "C:/Users/nacho/Downloads/Pruebas_autom/08-12-2023/"

# Nombre del archivo CSV de salida
archivo_csv = carpeta_raiz+"informacion_propiedades.csv"








def eliminar_secuencias_repetidas(cadena):
    # Encuentra todas las secuencias repetidas de dos o más palabras
    patron = r'\b(\w+(?:\s+\w+)+)\b\s+\1\b'
    coincidencias = re.findall(patron, cadena)

    # Reemplaza cada secuencia repetida por solo una instancia de las palabras
    for secuencia in coincidencias:
        if cadena.count(secuencia) > 1:
            # Reemplazar todas las ocurrencias menos una de cadena2 en cadena1
            cadena = cadena.replace(secuencia, '', cadena.count(secuencia) - 1)
    cadena = ' '.join(filter(None, cadena.split()))
    return cadena


# Cargar las normas de corrección desde el archivo "norma.csv" en un diccionario
normas = {}
with open("norma.csv", "r", newline="", encoding="utf-8") as norma_file:
    csv_reader = csv.reader(norma_file, delimiter=",")
    for row in csv_reader:
        if len(row) == 2:
            palabras = row[0].split(";")  # Separar las palabras por ;
            reemplazo = row[1]
            for palabra in palabras:
                normas[palabra] = reemplazo

# Lista para almacenar la información
informacion = []
conversiones = {
    "HAS": 10000,  # 1 Ha = 10,000 m2
    "HECT": 10000,
    "M2": 1,        # 1 m2 = 1 m2
    "MTS": 1,
    "MTS2": 1
}


# Itera a través de las subcarpetas
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        if (archivo_pdf.endswith(".pdf") and ("B" in archivo_pdf or "b" in archivo_pdf)):
            pdf_path = os.path.join(subdir, archivo_pdf)
            with pdfplumber.open(pdf_path) as pdf:
                info_dict = {"Nombre de Archivo": archivo_pdf}                        
                folio = archivo_pdf.split("-")[1].split(" ")[0] if "-" in archivo_pdf and " " in archivo_pdf else None # Obtener el número del nombre del archivo PDF
                info_dict["Folio"] = folio # Agregar el valor del "Folio" al diccionario info_dict
                total_m2 = None
                bool_area = False                       #señala  cuando hay una parte restante en el documento juridico
                
                pdf_pathj = os.path.join(subdir, archivo_pdf.replace("B","J"))
                if os.path.exists(pdf_pathj):
                    with pdfplumber.open(pdf_pathj) as pdfj:
                        for pagej in reversed(pdfj.pages):
                            # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                            lines = pagej.extract_text().splitlines()
                            for line in reversed(lines):
                                if "PARTE RESTANTE" in line or "AREA" in line or "�REA" in line:
                                    bool_area = True
                                    if "PARTE RESTANTE" in line:
                                        cadena = line.split("PARTE RESTANTE")[1].strip()
                                        cadena = cadena.split("ARTICULO")[0].strip()
                                    elif "AREA" in line:
                                        cadena = line.split("AREA")[1].strip()
                                    else:
                                        cadena = line.split("�REA")[1].strip()
                                        
                                    # Buscar las unidades de medida y sus valores numéricos                                                                                                            
                                    matches = re.findall(r'\b(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d+)?|\d+)[\s,]*(\w+)?', cadena)
                                    for match in matches:
                                        valor, unidad = match
                                        #valor = valor.replace(".", "").replace(",", "")  # Eliminar puntos y comas como separadores de miles

                                        # Determinar si el número debe ser tratado como decimal o número de miles
                                        if ',' in valor:
                                            valor = valor.replace(',', '.')  # Reemplazar coma por punto para tratar como número decimal
                                        elif '.' in valor and len(valor.split('.')[-1]) == 3:
                                            valor = valor.replace('.', '')  # Tratar como número de miles si tiene tres dígitos después del punto

                                        if unidad is None or unidad not in conversiones:
                                            unidad = "M2"  # Asignar M2 como unidad por defecto si no se encuentra o no está definida

                                        if unidad in conversiones:
                                            valor_m2 = float(valor) * conversiones[unidad]
                                            if total_m2 is None:
                                                total_m2 = valor_m2
                                            else:
                                                total_m2 += valor_m2
                                                break  # Romper el bucle si ya se encontró el valor total en m2
                                            if unidad == "M2" or unidad == "MTS2":
                                                break
                                    
                                    if total_m2 != None: 
                                        info_dict["Área de Terreno"] = str(total_m2)
                                        break
                                    else:
                                        bool_area = False
                                    
                            else:
                                continue  # Este `continue` es ejecutado solo si el bucle `for line in reversed(lines)` se completa sin encontrar "PARTE RESTANTE"
                            break  # Sale del bucle `for pagej in reversed(pdfj.pages)` (el bucle medio)

                
                for page in pdf.pages:
                    text = page.extract_text()
                    # Extraer el número después de "Matrícula(s) Matriz:"
                    #matricula_match = re.search(r"Matrícula\(s\) Matriz:(.*?)([A-Za-z]|$)", text, re.DOTALL)
                    matricula_match = re.search(r"Matrícula\(s\) Matriz:.*?-(\d+)", text, re.DOTALL)
                    if matricula_match:
                        matriculas = matricula_match.group(1).strip().split() if matricula_match.group(1) else []
                        info_dict["Matrícula matriz"] = " ".join(matriculas) if matriculas else None

                    # Extraer el número después de "Matrícula(s) Derivada(s):" 
                    matriculas_derivadas_match = re.search(r"Matrícula\(s\) Derivada\(s\):(.*?)([A-Za-z]|$)", text, re.DOTALL)
                    if matriculas_derivadas_match:
                        matriculas_derivadas = matriculas_derivadas_match.group(1).strip().split() if matriculas_derivadas_match.group(1) else []
                        info_dict["Matrículas derivadas"] = " ".join(matriculas_derivadas) if matriculas_derivadas else None
                    
                    # if folio == '48799':
                    #     print ('hola')
                    #Extraer número después de "Area de terreno Hectareas:" o "AREA:"
                    area_terreno = "" 
                    if not bool_area:
                        areas = ["area","�REA","Metros:", "Centimietros:"]
                        for i in areas:
                            textarea = text.split("Salvedades")[0].strip()
                            area_match = re.search(rf"({i})\D*(\d+(\.\d+)?) ", textarea, re.IGNORECASE)
                            
                            if i == 'Centimietros:':
                                oe = re.findall(rf"({i})\D*(\d+(\.\d+)?)", textarea, re.IGNORECASE)
                                if oe:
                                    area_match = oe[0]
                                    # print (area_match)
                                    posicion2 = area_match[1]
                            elif area_match:    
                                posicion2 = area_match.group(2)
                            #area_matches = re.findall(rf"({i})\D*(\d+(\.\d+)?)", textarea, re.IGNORECASE)
                            # for match in area_matches:
                            #     print(match)
                            # # if archivo_pdf == "148-50746 B.pdf":
                            # #     print (re.search(rf"({i})\s+(\d+(\.\d+)?)", text))
                            # if area_match:
                            #     hola1 = area_match.group(0)
                            #     hola2 = area_match.group(1)
                            #     hola3 = area_match.group(2)

                            if area_match and str(posicion2) != "0" and str(posicion2) != "":
                                if i == "Centimietros:":
                                    # Si la etiqueta es "Centimetros:", concatena el valor con un punto
                                    valor = posicion2
                                    area_terreno += "." + valor
                                else:
                                    valor = posicion2
                                    area_terreno = valor
                                #print("Área de Terreno:", area_terreno)  # Agrega esta línea para depura
                                info_dict["Área de Terreno"] = area_terreno

                    # Buscar la palabra "Servidumbre"
                    servidumbre_match = re.search(r"servidumbre", text, re.IGNORECASE)
                    if servidumbre_match:
                        info_dict["Servidumbre"] = "SI"
                    else:
                        info_dict["Servidumbre"] = "NO"
 
                    # Busca "Tipo de Predio: " y captura el próximo carácter en una variable
                    tipo_predio_match = re.search(r"Tipo de Predio: (\S)", text)

                    if tipo_predio_match:
                        info_dict["Tipo Predio"] = tipo_predio_match.group(1)
                                            
                    # Extraer la dirección antes del salto de línea
                    direccion_match = re.search(r"Dirección Actual del Inmueble:(.*?)(?:\n|$)", text)
                    if direccion_match:
                        direccion = direccion_match.group(1).strip()
                        info_dict["Dirección"] = direccion if direccion else None
                    #print (text)
                
                
                
                # Aplicar las normas de corrección a la dirección si existe
                if "Dirección" in info_dict:
                    direccion_original = info_dict["Dirección"]
                    if direccion_original:
                        direccion_corregida = direccion_original

                        # Aplicar las normas de corrección
                        for palabra, reemplazo in normas.items():
                            direccion_corregida = direccion_corregida.replace(palabra, reemplazo)                        
                        #info_dict["Dirección Corregida"] = eliminar_secuencias_repetidas(direccion_corregida)
                        info_dict["Dirección Corregida"] = direccion_corregida
                    else:
                        info_dict["Dirección Corregida"] = None
                else:
                    info_dict["Dirección Corregida"] = None

                # Añadir la información al listado
                informacion.append(info_dict)
#print (info_dict)
# Guardar la información en un archivo CSV
with open(archivo_csv, "w", newline="", encoding="utf-8") as csv_file:
    columnas = ["Nombre de Archivo","Folio", "Matrícula matriz","Matrículas derivadas", "Área de Terreno", "Servidumbre", "Tipo Predio", "Dirección", "Dirección Corregida"]
    csv_writer = csv.DictWriter(csv_file, fieldnames=columnas)
    csv_writer.writeheader()

    for info in informacion:
        csv_writer.writerow(info)

print(f"Se ha extraído y guardado la información de {len(informacion)} propiedades en {archivo_csv}.")
