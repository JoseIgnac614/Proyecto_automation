import re

lista_de_cadenas = [
    "Algo",
    "ESPECIFICACION: 0901 ACLARACION AREA EN 689M2, ESCRITURA 992 DE 16/09/2004.- NOTARIA UNICA DE SAHAGUN ",
   "ESPECIFICACION: 0913 DECLARACION PARTE RESTANTE EN 892 M2 (OTRO)",
   "Otra cadena con PARTE RESTANTE 76 HAS 4.405 M2 (OTRO)",
    "Una cadena con un número PARTE RESTANTE 419.25 M2 y otro 1.000",
    "ESPECIFICACION: 0913 DECLARACION PARTE RESTANTE SE RESERVA UN �REA DE 70 M2. (OTRO)"
]

conversiones = {
    "HAS": 10000,  # 1 Ha = 10,000 m2
    "HECT": 10000,
    "M2": 1,        # 1 m2 = 1 m2
    "MTS2": 1
}

# total_m2 = None

for cadena in lista_de_cadenas:
    total_m2 = None
    if "PARTE RESTANTE" in cadena or "ACLARACION AREA" in cadena:

        if "PARTE RESTANTE" in cadena:
            cadena2 = cadena.split("PARTE RESTANTE")[1].strip()
        else:
            cadena2 = cadena.split("ACLARACION AREA")[1].strip()
        matches = re.findall(r'\b(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d+)?|\d+)[\s,]*(\w+)?', cadena2)
        
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

print("Total en metros cuadrados:", total_m2)
