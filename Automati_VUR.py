from selenium import webdriver
from selenium.webdriver.common.by import By  # Importa el módulo By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import os
from selenium.common.exceptions import TimeoutException
import openpyxl
import sys
import io

# Configura las opciones de impresión para guardar como PDF
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--kiosk-printing')
chrome_options.add_argument('--disable-gpu')

nivel_de_zoom = 0.8
# Configura las opciones del navegador para ajustar el nivel de zoom
chrome_options.add_argument(f"--force-device-scale-factor={nivel_de_zoom}")


# Configura la opción para guardar como PDF
prefs = {
    'printing.print_preview_sticky_settings.appState': json.dumps({
        'recentDestinations': [{
            'id': 'Save as PDF',
            'origin': 'local',
            'account': '',
        }],
        'selectedDestinationId': 'Save as PDF',
        'version': 2,
    }),
}
directorio = "C:/Users/nacho/Downloads/davud/Autofinal/05-11-2023/Libro1.xlsx"
#directorio = "C:/Users/PORTATIL LENOVO/Downloads/Pruebas_autom/01-11-2023/Libro1.xlsx"

DirDescargasVUR = 'C:\\Users\\nacho\\Downloads\\'

# Abre el archivo de Excel
workbook = openpyxl.load_workbook(directorio)

# Selecciona la hoja en la que se encuentra la celda
sheet = workbook['Hoja1']



departameto= 'CORDOBA'
#municipio = 'SAHAGUN'           #
circulo = 'ORIP - SAHAGUN'             #ORIP - 
valor_indice = '148'
#valor_excel va a ser el A1 del excel


#print (prefs['download.default_directory'])
# Agrega la preferencia para la ubicación de descarga.
#prefs['download.default_directory'] = 'C:/Users/PORTATIL LENOVO/Downloads/Pruebas_autom'

def descargar_pdf(driver, download_folder, file_name, nuevo_nombre, tiempo_maximo_espera=30):
    # Realiza la descarga
    driver.execute_script("window.print();")

    # Inicia un temporizador
    inicio = time.time()

    while time.time() - inicio < tiempo_maximo_espera:
        if os.path.isfile(os.path.join(download_folder, file_name)):
            # El archivo ha sido encontrado, cambia el nombre si es necesario
            if os.path.isfile(os.path.join(download_folder, nuevo_nombre)):
                os.remove(os.path.join(download_folder, nuevo_nombre))  # Elimina el archivo con el nuevo nombre
            os.rename(os.path.join(download_folder, file_name), os.path.join(download_folder, nuevo_nombre))
            print("Archivo encontrado y renombrado.")
            return True
        else:
            # El archivo aún no está disponible, espera un segundo y verifica nuevamente
            time.sleep(1)

def wait_n_refresh(tiempo_max_espera, elemento):
    try:
        interaccion = WebDriverWait(driver, tiempo_max_espera).until(EC.presence_of_element_located((By.CSS_SELECTOR, elemento)))
        return interaccion
    except:
        #print("Tiempo de espera agotado. Recargando la página...")
        driver.refresh()

chrome_options.add_experimental_option('prefs', prefs)
timeout = 10

# Inicializa el navegador
driver = webdriver.Chrome(options=chrome_options)


# Maximiza la ventana del navegador
driver.maximize_window()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Navega a la página web deseada
driver.get("https://www.vur.gov.co/siteminderagent/forms_es-ES/loginsnr.fcc?TYPE=100663297&REALMOID=06-6c1363d6-46ce-4693-bea4-501339aa6485&GUID=&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=-SM-fqc7JfbsitKYA98880nx7GzOWf3PHSx%2frBwpwn0hvw7giR0TRx5Ii32r0m4mIlPP&TARGET=-SM-HTTP%3a%2f%2fwww%2evur%2egov%2eco%2fportal%2fpages%2fvur%2finicio%2ejsf%3furl%3d-%2Fportal-%2FPantallasVUR-%2F-%23-%2F-%3Ftipo-%3DdatosBasicosTierras")

count = 1
while sheet['A'+str(count)].value != None:
    while True:
        try:
            # Lee el valor de la celda
            valor_excel = sheet['A'+str(count)].value  # Reemplaza 'A1' por la celda que deseas usar
            valor_cadena = valor_indice + "-" + str(valor_excel)
            informacion_combobox = {
                '#header1 > table:nth-child(4) > tbody > tr > td > form > input[type=text]:nth-child(2)': 'LILIANAP.LOPEZ',
                '#header1 > table:nth-child(4) > tbody > tr > td > form > input[type=password]:nth-child(6)': 'P890980L',
            }

            for combobox_id, opcion in informacion_combobox.items():
                element = driver.find_element(By.CSS_SELECTOR, combobox_id)
                element.send_keys(opcion)
                    
            entrar = driver.find_element(By.CSS_SELECTOR, "#ext-gen40")
            entrar.click()

            # # Esperar 5 segundos
            time.sleep(1)
            driver.switch_to.default_content()   
            entrar = wait_n_refresh(15,"#menu-navegacion > li.dropdown > a")
            entrar.click()

            time.sleep(2)
            # Localiza el elemento sobre el cual deseas pasar el mouse
            elemento = driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li.dropdown.open > ul > li > a")

            # Crea una instancia de ActionChains
            actions = ActionChains(driver)

            # Mueve el mouse sobre el elemento
            actions.move_to_element(elemento).perform()

            time.sleep(0.5)
            entrar = driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li.dropdown.open > ul > li > ul > li:nth-child(1) > a")
            entrar.click()

            #time.sleep(5)

            iframe = driver.find_element(By.XPATH, "//iframe[@id='page']")
            driver.switch_to.frame(iframe)

            informacion_combobox = {
                '#selectDepartamento': departameto,
        #       '#selectMunicipio': municipio,
                '#circulo': circulo,
                '#matricula': valor_excel,
            }                  

            entrar = wait_n_refresh(10,"#selectDepartamento")

            flag = 0                    #Para avisar que el folio no está en el VU
            start_time = time.time()
            break
        except:
            driver.refresh()
    
    while True:
        try:
            if flag != 2:
                # Llena la información en los combobox en la página actual
                for combobox_id, opcion in informacion_combobox.items():
                    element = driver.find_element(By.CSS_SELECTOR, combobox_id)
                    element.send_keys(opcion)

                # Haz clic en el botón "Continuar" (ajusta el selector según tu página)
                driver.find_element(By.CSS_SELECTOR, "body > div.wrapper.ng-scope > div > div:nth-child(2) > div.panel-body > div.btn-group.pull-right > button").click()
                time.sleep(1.5)    
                #Espera hasta que aparezca el elemento en la siguiente página
                wait = WebDriverWait(driver, timeout)
                
                matricula = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.wrapper.ng-scope > div > div:nth-child(3) > div.panel-body > table > tbody > tr > td:nth-child(1) > a")))
                matricula.click()
                #Si el elemento se encuentra, el bucle se detiene
                
                wait = WebDriverWait(driver, timeout)
                matricula = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.panel.panel-primary.datos-basicos[ng-show="pantallaDatosBasicos"]:not(.ng-hide)'))
                )

                # Abre el diálogo de impresión del navegador
                descargar_pdf(driver,DirDescargasVUR,"-VUR.pdf",valor_cadena+" B.pdf")
                # Encuentra todos los elementos que tienen un atributo "id"
                driver.switch_to.default_content()

                    
                entrar = driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li.dropdown > a")
                entrar.click()
                time.sleep(0.5)
                # Localiza el elemento sobre el cual deseas pasar el mouse
                elemento = driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li.dropdown.open > ul > li > a")

                # Crea una instancia de ActionChains
                actions = ActionChains(driver)

                # Mueve el mouse sobre el elemento
                actions.move_to_element(elemento).perform()

                time.sleep(0.5)
                entrar = driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li.dropdown.open > ul > li > ul > li:nth-child(2) > a")
                entrar.click()

                iframe = driver.find_element(By.XPATH, "//iframe[@id='page']")
                driver.switch_to.frame(iframe)
                flag = 2
            time.sleep(2)
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.panel.panel-primary[ng-show="pantallaDatosJuridicos"]:not(.ng-hide)'))
            )

            # Esperar hasta que se encuentre un elemento <li> que contiene "Lista"
            elemento = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.wrapper.ng-scope > div > div:nth-child(11) > div > div.tabbable.ng-isolate-scope > ul > li:nth-child(2)"))
            )
            elemento.click()
            descargar_pdf(driver,DirDescargasVUR,"-VUR.pdf",valor_cadena+" J.pdf")
            
            driver.switch_to.default_content()
            driver.find_element(By.CSS_SELECTOR, "#menu-navegacion > li:nth-child(5) > a").click()
            break

        except Exception as e:
            print(f"Se produjo un error: {e}")
            # Si el elemento no se encuentra, recarga la página
            driver.refresh()
            time.sleep(3)
            iframe = driver.find_element(By.XPATH, "//iframe[@id='page']")
            driver.switch_to.frame(iframe)
            
            elapsed_time = time.time() - start_time                 #Por si el folio no está en el vur
            if elapsed_time >= 5:
                if flag == 2:
                    start_time = time.time()
                    flag = 1
                else:
                    flag = 1
                    break
                
            
    if flag == 1:
        #escribir algo en el excel
        #print ("No está el folio en el VUR")
        sheet['B'+str(count)] = "No está el folio en el VUR"
        workbook.save(directorio)
        flag = 0
        
        driver.switch_to.default_content()
        wait = WebDriverWait(driver, timeout)
        matricula = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#menu-navegacion > li:nth-child(5) > a"))).click()
        
    count += 1
        
time.sleep(2)
