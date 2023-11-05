import os
import pdfplumber
import csv

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
carpeta_raiz = "vur/"

# Nombre del archivo CSV de salida
archivo_csv = "nombres_cedulas.csv"

# Listas para almacenar los nombres y cédulas
nombres = []
cedulas = []

# Itera a través de los archivos PDF en la carpeta
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        if archivo_pdf.endswith(".pdf") and "J" in archivo_pdf:
            pdf_path = os.path.join(subdir, archivo_pdf)

            with pdfplumber.open(pdf_path) as pdf:
                page_curr = None  # Página actual
                encontrado_x = False  # Indica si se ha encontrado " X "
                encontrado_an = False # Indica si se ha encontrado "ANOTACION"
                encontrado_de = False # Indica si se ha encontrado un "DE:"
                encontrado_nr2 = False # Indica si ya pasó por la anotacion nro 2
                found = False #Indica si encuentra mas de un anotacion y si encuentra un nro 1
                count_anotacion = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                count_anotacion_nro_1 = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                numeros_cancelados = []
                nuevos_numeros = []
                numero = 0
                count_nr1_a = 0
                contador = 0
                texto_lineas = []  # Almacena el texto de las líneas relevantes
                nombres = []  # Lista para almacenar los nombres
                cedulas = []  # Lista para almacenar las cédulas

                for page in reversed(pdf.pages):
                    if encontrado_x and encontrado_an:
                        encontrado_x = False
                        encontrado_an = False
                        break  # Si " X " ya se encontró, detén la iteración
                    
                    page_curr = page

                    lines = page_curr.extract_text().splitlines()
                    #print (lines)
                    # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                    for line in lines:
                        if "ANOTACION: Nro 1" in line:
                            count_anotacion_nro_1 = True
                        if count_anotacion_nro_1 and "ANOTACION" in line:
                            count_anotacion += 1
                        if count_anotacion_nro_1 and "A:" in line:
                            count_nr1_a += 1
                    # Comprobar si "ANOTACION: Nro 1" se encontró y "ANOTACION" aparece más de una vez
                    resultado = count_anotacion_nro_1 == 1 and count_anotacion == 1
                                        
                    for line in reversed(lines):
                        # if "ANTONIO MARIA" in line:
                        #     print ("tons")
                        if "DE:" in line:           #para poder guardar un parrafo solo cuando tenga "DE:"
                            encontrado_de = True
                        elif "CANCELACION" in line or "PARCIAL" in line:
                            encontrado_de = False
                        elif "A:" in line and encontrado_nr2 or "A:" in line and encontrado_x:
                            encontrado_nr2 = True
                            encontrado_de = True
                        elif "Se cancela anotación No: " in line:
                            # Buscar números después de "No:"
                            nuevos_numeros = [numero.strip() for numero in line.split("No: ")[1].split(",")]
                            numeros_cancelados = numeros_cancelados + nuevos_numeros
                            
                            # Verificar si existe "ANOTACION: Nro " seguido de los números cancelados
                        for numero in numeros_cancelados:
                            if f"ANOTACION: Nro {numero}" in line:
                                encontrado_de = False
                                break  # Puedes detener la búsqueda una vez que se cumple la condición
                        
                        
                        if " X" in line and "A:" in line or resultado and "A:" in line and " X" not in line or encontrado_nr2:# and not encontrado_x:
                            encontrado_x = True
                            encontrado_nr2 = False
                            #print (line)
                            
                            #TRATAMIENTO DE DATOS PARA LA CEDULA Y NOMBRE
                            nombre = line[3:]
                            nombre, cedula = dividir_por_delimitadores([" CC ", " NIT. ", " X", " # "], nombre)
                                
                            if resultado: #sirve para cuando solo hay una anotacion nro 1.
                                contador+=1
                                if count_nr1_a == contador:
                                    resultado = False
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
                                texto_lineas.insert(0, line)
                                break
                            else:
                                encontrado_x = False
                                nombres = []
                                cedulas = []
                                texto_lineas = []
                                if "ANOTACION: Nro 2" in line:
                                    encontrado_nr2 = True 

                # Combinar nombres y cédulas en una sola celda con saltos de línea
                #print (nombres)
                nombres_celda = "\n".join(nombres)
                cedulas_celda = "\n".join(cedulas)
                texto_celda = "\n".join(texto_lineas)

                # Guardar los datos en el archivo CSV si se encontró " X "
                with open(archivo_csv, "a", newline="", encoding="utf-8") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Agregar encabezados si el archivo está vacío
                    if os.path.getsize(archivo_csv) == 0:
                        csv_writer.writerow(["Nombre de archivo", "Nombres", "Cédulas", "Texto"])

                    # Agregar los datos del archivo PDF actual
                    csv_writer.writerow([archivo_pdf, nombres_celda, cedulas_celda, texto_celda])

                # Limpiar las listas para el próximo archivo PDF
                nombres.clear()
                cedulas.clear()
                texto_lineas.clear()

print(f"Se ha analizado y guardado la información en {archivo_csv}.")
