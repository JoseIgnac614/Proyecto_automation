import re

lista_de_cadenas = [
    "Algo",
   # "ESPECIFICACION: 0913 DECLARACION PARTE RESTANTE EN 892 M2 (OTRO)",
   "Otra cadena con PARTE RESTANTE 76 HAS 4.405 M2 (OTRO)",
#     "Una cadena con un número PARTE RESTANTE 419.25 M2 y otro 1.000"

]

conversiones = {
    "HAS": 10000,  # 1 Ha = 10,000 m2
    "M2": 1        # 1 m2 = 1 m2
}

total_m2 = None

for cadena in lista_de_cadenas:
    if "PARTE RESTANTE" in cadena:
        # Buscar las unidades de medida y sus valores numéricos
        matches = re.findall(r'\b(\d{1,3}(?:[\.,]\d{3})*(?:\.\d+)?|\d+)\s*(\w+)', cadena)
        for match in matches:
            valor, unidad = match
            #valor = valor.replace(".", "").replace(",", "")  # Eliminar puntos y comas como separadores de miles

            # Determinar si el número debe ser tratado como decimal o número de miles
            if '.' in valor:
                parte_decimal = valor.split('.')[1]
                if len(parte_decimal) == 3:
                    valor = valor.replace('.', '')  # Tratar como número de miles

            if unidad in conversiones:
                valor_m2 = float(valor) * conversiones[unidad]
                if total_m2 is None:
                    total_m2 = valor_m2
                else:
                    total_m2 += valor_m2
                    break  # Romper el bucle si ya se encontró el valor total en m2

print("Total en metros cuadrados:", total_m2)
