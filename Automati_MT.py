from selenium import webdriver
from selenium.webdriver.common.by import By  # Importa el módulo By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import openpyxl
import time

# Abre el archivo Excel
archivo_excel = openpyxl.load_workbook('tu_archivo.xlsx')

# Selecciona la hoja en la que deseas trabajar
hoja = archivo_excel['nombre_de_la_hoja']


# Crea un diccionario para mapear los nombres de encabezados a variables
datos = {
    'Nombre de Archivo': None,
    'Folio': None,
    'Matrícula matriz': None,
    'Área de Terreno': None,
    'Dirección Corregida': None,
}

# Obtén los valores de los encabezados en la primera fila
for columna in hoja.iter_cols(min_row=1, max_row=1):
    for celda in columna:
        if celda.value in datos:
            datos[celda.value] = celda.column

# Crea una instancia de un navegador web (por ejemplo, Edge)
driver = webdriver.Chrome()

# Navega a la página web deseada
driver.get("https://www.realidad5.com/realmultipropositosanluis/servlet/com.realmultipropositogam.iniciosesion")

# Localiza el campo de texto de usuario por su selector CSS
campo_usuario = driver.find_element(By.CSS_SELECTOR, "#vUSERNAME")
campo_usuario.send_keys("jgonzalez")

# Localiza el campo de texto de contraseña por su selector CSS
campo_contrasena = driver.find_element(By.CSS_SELECTOR, "#vUSERPASSWORD")
campo_contrasena.send_keys("u9OPY2tnZs*71")

entrar = driver.find_element(By.CSS_SELECTOR, "#BTNENTER")
entrar.click()

# Esperar 5 segundos
time.sleep(6)

driver.get("https://www.realidad5.com/realmultipropositosanluis/servlet/com.realmultipropositogam.wwfichprediact")



mas = driver.find_element(By.CSS_SELECTOR, "#ACTIONNEW")
mas.click()
time.sleep(1)
matricula = driver.find_element(By.CSS_SELECTOR, "#vACTPREDIOMATRICULA")
matricula.send_keys("7")
time.sleep(3)

matricula = driver.find_element(By.CSS_SELECTOR, "#vUPDATE_0001")
matricula.click()
time.sleep(8)


# Localiza el combobox por su selector CSS, XPath u otro método.
combobox = driver.find_element(By.CSS_SELECTOR, "#W0014vTIPOLOTE_ID") # Ajusta el selector según tu página.

# Obtiene el texto del elemento seleccionado.
elemento_seleccionado = Select(combobox).first_selected_option
texto_elemento = elemento_seleccionado.text

# Define la cadena de caracteres que deseas buscar.
cadena_busqueda = "Unidad_Predial"

# Comprueba si la cadena de búsqueda está presente en el texto.
if cadena_busqueda not in texto_elemento:
    print(f"La cadena '{cadena_busqueda}' está en el elemento seleccionado.")
    
    # Define la fila desde la que deseas extraer datos
    fila_a_extraer = 2  # Reemplaza con el número de fila deseado

    # Extrae los datos de la fila y almacénalos en el diccionario
    fila = hoja[fila_a_extraer]
    for encabezado, columna in datos.items():
        if columna:
            datos[encabezado] = fila[columna].value

    # Ahora puedes acceder a los datos a través del diccionario
    print('Nombre de Archivo:', datos['Nombre de Archivo'])
    print('Folio:', datos['Folio'])
    print('Matrícula matriz:', datos['Matrícula matriz'])
    print('Área de Terreno:', datos['Área de Terreno'])
    print('Dirección Corregida:', datos['Dirección Corregida'])
    






    
    

matricula = driver.find_element(By.CSS_SELECTOR, "#Tab_TAB1Containerpanel3")
matricula.click()
time.sleep(1)

matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTFUENTEADMINTIPOID")
matricula.send_keys("Escritura")
matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTPRINCIPALDOCTIPOID")
matricula.send_keys("Documento")
matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTFUEADMFECHDOC")
driver.execute_script("arguments[0].value = arguments[1];", matricula, "29/12/2020")
# matricula.send_keys("29/12/2020")
matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTNUMFUENTE")
matricula.send_keys("369")
matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTENTEEMISOR")
matricula.send_keys("MARINILLA")
matricula = driver.find_element(By.CSS_SELECTOR, "#W0030vACTFUEADMFECHREG")
driver.execute_script("arguments[0].value = arguments[1];", matricula, "10/12/2020")


matricula = driver.find_element(By.CSS_SELECTOR, "#W0030ENTER")
matricula.send_keys(Keys.PAGE_DOWN)
matricula.click()

time.sleep(5)


#W0030vACTFUENTEADMINTIPOID

#Tab_TAB1Containerpanel3
#vUPDATE_0001
#vACTPREDIOMATRICULA

# entrar = driver.find_element(By.XPATH, "//*[contains(text(), 'Actualización')]")

# entrar.click()

# time.sleep(3)
# campo_juridico = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "<span class="menu-text">Jurídico</span>"))
# )
# campo_juridico.click()
# # Abre el archivo de Excel
# workbook = openpyxl.load_workbook('O:/ANTES DE FORMATEO/SAN LUIIIIIIS/25102023/Libro1.xlsx')

# # Selecciona la hoja en la que se encuentra la celda
# sheet = workbook['nombres_cedulas']

# # Lee el valor de la celda
# valor_de_excel = sheet['B3'].value  # Reemplaza 'A1' por la celda que deseas usar


# # Encuentra el campo de búsqueda en la página web (debes inspeccionar el código fuente de la página para obtener el selector adecuado)
# campo_busqueda = driver.find_element_by_css_selector("#W0030vACTENTEEMISOR")

# # Envía el valor de Excel al campo de búsqueda
# campo_busqueda.send_keys(valor_de_excel)
