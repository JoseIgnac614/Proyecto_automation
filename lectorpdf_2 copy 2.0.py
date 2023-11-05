import os
import pdfplumber
import csv
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Carpeta que contiene las subcarpetas con los archivos PDF
carpeta_raiz = "vur/"

# Nombre del archivo CSV de salida
archivo_csv = "informacion_propiedades.csv"

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
        if archivo_pdf.endswith(".pdf") and "B" in archivo_pdf:
            pdf_path = os.path.join(subdir, archivo_pdf)

            with pdfplumber.open(pdf_path) as pdf:
                info_dict = {"Nombre de Archivo": archivo_pdf}

                folio = archivo_pdf.split("-")[1].split(" ")[0] if "-" in archivo_pdf and " " in archivo_pdf else None # Obtener el número del nombre del archivo PDF
                info_dict["Folio"] = folio # Agregar el valor del "Folio" al diccionario info_dict
                
                # Inicializa area_area como una lista para acumular los números de todas las páginas
                area_area = []
                area_terreno = []
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
                    
                    # Buscar números después de "AREA:" en cada página
                    area_match_area = re.search(r"AREA\s+(\d+(\.\d+)?)", text)
                    if area_match_area:
                        area_area_texto = area_match_area.group(1).strip()
                        print ("area  -> ",area_area_texto)
                        
                        # Extender la lista area_area con los números encontrados en esta página
                        area_area.extend(area_area_texto)

                    # Buscar números después de "Area de terreno Hectareas:" en cada página
                    area_match = re.search(r"Area de terreno Hectareas:(.*?)(?:Coeficiente|$)", text, re.DOTALL)
                    if area_match:
                        area_terreno_texto = area_match.group(1).strip()
                        print ("area terreno -> ",area_terreno_texto)
                         # Buscar números en el texto de esta página
                        numeros_encontrados = re.findall(r'(\d+(\.\d+)?)', area_terreno_texto)
                        print ("area terreno numeros -> ",numeros_encontrados)
                        #numeros_mayores_de_cero = [numero[0] for numero in numeros_encontrados if float(numero[0]) > 0]
                        #print ("area terreno numeros >0 -> ",numeros_mayores_de_cero)
                        # Extender la lista area_terreno con los números encontrados en esta página
                        area_terreno.extend(numeros_encontrados)

                    # Buscar la palabra "Servidumbre"
                    servidumbre_match = re.search(r"Servidumbre", text)
                    if servidumbre_match:
                        info_dict["Servidumbre"] = "SI"
                    else:
                        info_dict["Servidumbre"] = "NO"

                    # Extraer la dirección antes del salto de línea
                    direccion_match = re.search(r"Dirección Actual del Inmueble:(.*?)(?:\n|$)", text)
                    if direccion_match:
                        direccion = direccion_match.group(1).strip()
                        info_dict["Dirección"] = direccion if direccion else None
                    #print (text)

                # Concatenar los números con espacios
                area_area = ' '.join(area_area) if area_area else None
                area_terreno = 'x '.join(area_terreno) if area_terreno else None

                # Asignar la cadena resultante a la columna "Área de Terreno (Hectáreas)"
                info_dict["Área de Terreno"] = ' '.join(filter(None, [area_terreno, area_area]))
                area_terreno = ' '.join(map(str, numeros_mayores_de_cero)) if numeros_mayores_de_cero else None
                
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
    columnas = ["Nombre de Archivo","Folio", "Matrícula matriz","Matrículas derivadas", "Área de Terreno", "Servidumbre", "Dirección", "Dirección Corregida"]
    csv_writer = csv.DictWriter(csv_file, fieldnames=columnas)
    csv_writer.writeheader()

    for info in informacion:
        csv_writer.writerow(info)

print(f"Se ha extraído y guardado la información de {len(informacion)} propiedades en {archivo_csv}.")
