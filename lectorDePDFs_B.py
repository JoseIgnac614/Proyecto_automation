import os
import pdfplumber
import csv
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Carpeta que contiene las subcarpetas con los archivos PDF
carpeta_raiz = "C:/Users/nacho/Downloads/davud/Autofinal/05-11-2023/"
#carpeta_raiz = "C:/Users/PORTATIL LENOVO/Downloads/Pruebas_autom/01-11-2023/"

# Nombre del archivo CSV de salida
archivo_csv = carpeta_raiz+"informacion_propiedades.csv"

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

# Itera a través de las subcarpetas
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        if (archivo_pdf.endswith(".pdf") and ("B" in archivo_pdf or "b" in archivo_pdf)):
            pdf_path = os.path.join(subdir, archivo_pdf)
            with pdfplumber.open(pdf_path) as pdf:
                info_dict = {"Nombre de Archivo": archivo_pdf}

                folio = archivo_pdf.split("-")[1].split(" ")[0] if "-" in archivo_pdf and " " in archivo_pdf else None # Obtener el número del nombre del archivo PDF
                info_dict["Folio"] = folio # Agregar el valor del "Folio" al diccionario info_dict
                
                for page in pdf.pages:
                    text = page.extract_text()
                    # Extraer el número después de "Matrícula(s) Matriz:"
                    matricula_match = re.search(r"Matrícula\(s\) Matriz:(.*?)([A-Za-z]|$)", text, re.DOTALL)
                    if matricula_match:
                        matriculas = matricula_match.group(1).strip().split() if matricula_match.group(1) else []
                        info_dict["Matrícula matriz"] = " ".join(matriculas) if matriculas else None

                    # Extraer el número después de "Matrícula(s) Derivada(s):" 
                    matriculas_derivadas_match = re.search(r"Matrícula\(s\) Derivada\(s\):(.*?)([A-Za-z]|$)", text, re.DOTALL)
                    if matriculas_derivadas_match:
                        matriculas_derivadas = matriculas_derivadas_match.group(1).strip().split() if matriculas_derivadas_match.group(1) else []
                        info_dict["Matrículas derivadas"] = " ".join(matriculas_derivadas) if matriculas_derivadas else None
                    
                    #Extraer número después de "Area de terreno Hectareas:" o "AREA:"
                    areas = ["Metros:", "AREA", "Centimietros:"]
                    for i in areas:
                        area_match = re.search(rf"({i})\s+(\d+(\.\d+)?)", text)
                        if archivo_pdf == "148-50746 B.pdf":
                            print (re.search(rf"({i})\s+(\d+(\.\d+)?)", text))
                        if area_match:
                            etiqueta = area_match.group(1)
                            
                            if etiqueta == "Centimietros:":
                                # Si la etiqueta es "Centimetros:", concatena el valor con un punto
                                valor = area_match.group(2)
                                area_terreno += "." + valor
                            else:
                                valor = area_match.group(2)
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