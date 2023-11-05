import os
import pdfplumber
import csv
import re

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
carpeta_raiz = "SANLUIS_20_21/"

# Nombre del archivo CSV de salida
archivo_csv = "nombres_cedulas2.csv"

# Listas para almacenar los nombres y cédulas
nombres = []
primer_nombre  = []
segundo_nombre = []
primer_apellido = []
segundo_apellido = []
cedulas = []

# Itera a través de los archivos PDF en la carpeta
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        if archivo_pdf.endswith(".pdf") and "J" in archivo_pdf or "j" in archivo_pdf:
            pdf_path = os.path.join(subdir, archivo_pdf)

            with pdfplumber.open(pdf_path) as pdf:
                page = None  # Página actual
                encontrado_x = False  # Indica si se ha encontrado " X "
                encontrado_an = False # Indica si se ha encontrado "ANOTACION"
                encontrado_de = False # Indica si se ha encontrado un "DE:"
                encontrado_nr2 = False # Indica si ya pasó por la anotacion nro 2
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
                servidumbre = "NO"
                ph = "NO"

                for page in reversed(pdf.pages):
                    # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                    lines = page.extract_text().splitlines()
                    for line in lines:
                        if "ANOTACION: Nro 1" in line:
                            count_anotacion_nro_1 = True
                        if count_anotacion_nro_1 and "ANOTACION" in line:
                            count_anotacion += 1
                        if count_anotacion_nro_1 and "A:" in line or count_nr1_a == 0 and "DE:" in line:
                            count_nr1_a += 1
                        if re.search(r"servidumbre", line, re.IGNORECASE):
                            servidumbre = "SI"
                        if re.search(r"horizontal", line, re.IGNORECASE):
                            ph = "SI"

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
                        if "DE:" in line or bool_A:           #para poder guardar un párrafo solo cuando tenga "DE:"
                            encontrado_de = True
                        elif "CANCELACION" in line or "PARCIAL" in line or "EMBARGO" in line or "DEMANDA EN PROCESO" in line or "ACLARACION" in line or "FALSA TRADICION" in line:
                            encontrado_de = False
                        elif "Se cancela anotación No: " in line:
                            # Buscar números después de "No:"
                            nuevos_numeros = [numero.strip() for numero in line.split("No: ")[1].split(",")]
                            numeros_cancelados = numeros_cancelados + nuevos_numeros
                        
                        if "A:" in line and encontrado_nr2 or "A:" in line and encontrado_x:
                            encontrado_nr2 = True
                            encontrado_de = True
                        elif "DE:" in line and encontrado_nr2:
                            encontrado_nr2 = True
                            encontrado_de = True
                            
                            # Verificar si existe "ANOTACION: Nro " seguido de los números cancelados
                        for numero in numeros_cancelados:
                            if f"ANOTACION: Nro {numero}" in line:
                                encontrado_de = False
                                break  # Puedes detener la búsqueda una vez que se cumple la condición
                        
                        if resultado: #PARA LOS CASOS EN QUE NO HAYAN MAS ANOTACIONES MAS QUE LA PRIMERA Y ASEGURAR QUE GUARDE ALGUN PROPIETARIO
                            if bool_A and "DE:" in line:
                                anot1 = True
                            elif "A:" in line:
                                bool_A = False

                        if " X" in line and "A:" in line or resultado and "A:" in line or anot1 or encontrado_nr2 or " X" in line and "A:" in line:# and not encontrado_x:
                            encontrado_x = True
                            encontrado_nr2 = False
                            #print (line)

                            # TRATAMIENTO DE DATOS PARA LA CÉDULA Y NOMBRE
                            nombre = line[3:]
                            nombre, cedula = dividir_por_delimitadores([" CC ", " NIT. ", " X", " # "], nombre)

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
                # nombres_celda = "\n".join(nombres)
                # cedulas_celda = "\n".join(cedulas)
                texto_celda = "\n".join(texto_lineas)
                primer_nombre = []
                segundo_nombre = []
                primer_apellido = []
                segundo_apellido = []

                # Dividir nombres en primer nombre, segundo nombre, primer apellido y segundo apellido
                #print ("nombres_celda-> ",nombres_celda)
                if nombres != "":
                    i=0
                    while i < len(nombres):
                        pn, sn,pa, sa = dividir_nombres(nombres[i])
                        primer_nombre.append(pn)
                        segundo_nombre.append(sn)
                        primer_apellido.append(pa)
                        segundo_apellido.append(sa) 
                        i += 1

                # Guardar los datos en el archivo CSV si se encontró " X "
                with open(archivo_csv, "a", newline="", encoding="utf-8") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Agregar encabezados si el archivo está vacío
                    if os.path.getsize(archivo_csv) == 0:
                        csv_writer.writerow(["Nombre de archivo", "Servidumbre", "PH","Texto", "Cédulas", "Primer Nombre", "Segundo Nombre", "Primer Apellido", "Segundo Apellido"])
                    
                    if primer_nombre == []:
                        print ("No hay nadaaaaaaa, archivo: ", archivo_pdf)
                    
                    # Agregar los datos del archivo PDF actual
                    i = 0
                    while i < len(nombres):
                        if i == 0:
                            csv_writer.writerow([archivo_pdf, servidumbre, ph, texto_celda, cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i]])
                        else:
                            csv_writer.writerow(["", "","","", cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i]])
                        i += 1

                # Limpiar las listas para el próximo archivo PDF
                nombres.clear()
                cedulas.clear()
                texto_lineas.clear()

print(f"Se ha analizado y guardado la información en {archivo_csv}.")
