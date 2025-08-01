# src/glgrpa/SAP.py

# Importaciones necesarias
from selenium.webdriver.common.by import By

from .Chrome import Chrome
from .Terminal import Terminal
from .Windows import Windows

class SAP(Chrome, Windows, Terminal):    
    def __init__(self, base_url: str, usuario: str, clave: str, dev: bool = False, driver=None):
        super().__init__(dev=dev, driver=driver)
        self.base_url = base_url
        
        self.autentificacion_http_activo = False
        self.autentificacion_sap_activo = False
        self.autentificacion_microsoft_activo = False

        self.usuario_sap = usuario
        self.clave_sap = clave
        self.set_credenciales_usuario(usuario, clave)

        self.sap_iniciado = False
        
        self.mapa_transacciones = {
            'OB08': "#Shell-startGUI?sap-ui2-tcode=OB08&sap-system=FIORI_MENU",
            'FB03': '#Shell-startGUI?sap-ui2-tcode=FB03&sap-system=FIORI_MENU',
            # Agrega más transacciones según sea necesario
        }
        
    def set_credenciales_usuario(self, usuario: str, clave: str) -> dict:
        """
        Configura las credenciales del usuario de SAP.
        
        Al inicializar la clase se setean las credenciales del usuario y la clave de SAP pero se pueden cambiar en cualquier momento.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.set_credenciales_usuario('nuevo_usuario', 'nueva_clave')
        ```
        >>> {'usuario': 'nuevo_usuario', 'clave': 'nueva_clave'}
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario está vacío.
        - Si la clave está vacía.
        """
        
        if usuario == '':
            raise ValueError("El usuario no puede estar vacío")
        if clave == '':
            raise ValueError("La clave no puede estar vacía")
        
        self.usuario_sap = usuario
        self.clave_sap = clave
        self.mostrar(f"Credenciales configuradas para {self.usuario_sap}")
        
        return {
            'usuario': self.usuario_sap,
            'clave': self.clave_sap
        }
        
    def obtener_usuario_sap(self) -> str:
        """ 
        Obtiene el usuario de SAP configurado.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.obtener_usuario_sap()
        ```
        >>> 'usuario'
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario SAP no está configurado.
        """
        if not self.usuario_sap:
            raise ValueError("Usuario SAP no configurado. Use set_credenciales_usuario() para configurarlo.")
        
        return self.usuario_sap
    
    def obtener_clave_sap(self) -> str:
        """
        Obtiene la clave de SAP configurada.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.obtener_clave_sap()
        ```
        >>> 'clave'

        ---
        ### Raises
        #### ValueError
        - Si la clave SAP no está configurada.
        """
        if not self.clave_sap:
            raise ValueError("Clave SAP no configurada. Use set_credenciales_usuario() para configurarla.")
        return self.clave_sap
            
    def navegar_inicio_SAP(self) -> bool:
        """
        Navega a la página de inicio de SAP.
        
        Obtiene el driver activo, navega a la URL base de SAP y activa la ventana. Luego depende el login que se deba realizar,
        realiza la autenticación HTTP, SAP o Microsoft según corresponda.
        
        ---
        ### Cuidado
        Este método utiliza `pyautogui` para simular teclas, por lo que es importante que la ventana de SAP esté activa y visible.  
        Si bien se pone en foco de forma automática, es recomendable que el usuario no interactúe con el teclado o el mouse durante la ejecución de este método.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.navegar_inicio_SAP()
        ```
        >>> True  # Si SAP se inició correctamente
        
        ---
        ### Raises
        #### ValueError
        - Las opciones del driver no están configuradas. Por favor, inicializa el objeto Chrome correctamente.
        - El navegador no está abierto. Por favor, abre el navegador antes de navegar.
        
        #### Exception
        - No se pudo obtener el PID del proceso de Chrome.
        - No se pudo activar la ventana de SAP.

        """
        self.driver = self.obtener_driver()
        self.navegar(self.base_url)
        self.activar_ventana()
        
        # Verificación rápida inicial del estado
        if self.__en_pagina_de_inicio():
            self.sap_iniciado = True
            self.mostrar("✅ SAP ya iniciado - sesión activa detectada")
            return self.sap_iniciado
        
        # Proceder con autenticación según el tipo detectado
        self.mostrar("🔐 Iniciando proceso de autenticación...")
        
        if self._autentificacion_http():
            self.mostrar("🌐 Autenticación HTTP detectada")
            import pyautogui
            pyautogui.hotkey('shift', 'tab')
            pyautogui.press('enter')
            self.demora()
            self.autentificacion_http_activo = False
            
        if self._autentificacion_sap():
            self.mostrar("🏢 Autenticación SAP detectada")
            self._ingresar_usuario()
            self._ingresar_contrasena(enter=True)
            self.autentificacion_sap_activo = False
        
        if self._autentificacion_microsoft():
            self.mostrar("🔐 Autenticación Microsoft detectada")
            self._ingresar_usuario()
            self._ingresar_contrasena()
            self._no_mantener_sesion_iniciada()
            self.autentificacion_microsoft_activo = False
            
        self.sap_iniciado = True
        self.mostrar("✅ SAP iniciado correctamente")
        return self.sap_iniciado
    
    def __en_pagina_de_inicio(self) -> bool:
        """
        Verifica si se está en la página de inicio de SAP.

        Comprueba si el título de la página es "Página de inicio", lo que indica que se ha iniciado sesión correctamente.

        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.

        ---
        ### Ejemplo
        ```python
        self.__en_pagina_de_inicio():
        ```
        >>> True
        """
        return self.driver.title == "Página de inicio"
    
    def _autentificacion_http(self) -> bool:
        """
        Verifica si la autenticación HTTP está activa.

        Comprueba si el título de la página es "SAP Logon - SAP GUI for Windows", lo que indica que se requiere autenticación de SAP.

        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.
        
        ---
        ### Ejemplo
        ```python
        self._autentificacion_http():
        ```
        >>> True  # Si la autenticación HTTP está activa
        """
        self.autentificacion_http_activo = True if self.driver.title == "" else False
        return self.autentificacion_http_activo
    
    def _autentificacion_sap(self) -> bool:
        """ 
        Verifica si la autenticación de SAP está activa. 
        
        Comprueba si existe el elemento HTML "<main id="LOGIN_MAIN"></main>", lo que indica que se requiere autenticación de SAP.
        
        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.
        
        ---
        ### Ejemplo
        ```python
        self._autentificacion_sap():
        ```
        >>> True  # Si la autenticación SAP está activa
        """
        try:
            # Verificar si existe el elemento main con id LOGIN_MAIN
            login_main_element = self.encontrar_elemento(By.ID, 'LOGIN_MAIN', tiene_que_estar=False)
            self.autentificacion_sap_activo = login_main_element is not None
            
            if self.autentificacion_sap_activo:
                self.mostrar("🔍 Elemento LOGIN_MAIN detectado - Autenticación SAP requerida")
            
            return self.autentificacion_sap_activo
        except Exception as e:
            self.mostrar(f"❌ Error al verificar autenticación SAP: {str(e)}", True)
            self.autentificacion_sap_activo = False
            return self.autentificacion_sap_activo
    
    def _autentificacion_microsoft(self) -> bool:
        """
        Verifica si la autenticación de Microsoft está activa.
        
        Comprueba si el título de la página es "Iniciar sesión en la cuenta", lo que indica que se requiere autenticación de Microsoft. 
        
        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.
            
        ---
        ### Ejemplo
        ```python
        self._autentificacion_microsoft():
        ```
        >>> True  # Si la autenticación Microsoft está activa    
        """
        self.autentificacion_microsoft_activo = True if self.driver.title == "Iniciar sesión en la cuenta" else False
        return self.autentificacion_microsoft_activo
            
    def _ingresar_usuario(self, tab: bool = False) -> bool:
        """
        Ingresa el usuario de SAP.
        
        En caso de autenticación Microsoft, ingresa el usuario en el campo correspondiente y hace clic en "Siguiente".
        En caso de autenticación SAP, ingresa el usuario en el campo correspondiente y hace clic en "Continuar".
        
        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.
        
        ---
        ### Ejemplo
        ```python
        self._ingresar_usuario():
        ```
        >>> True  # Si el usuario se ingresó correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario SAP no está configurado.
        - Si hay un error al ingresar el usuario de SAP con autenticación Microsoft o SAP.
        """
        self.mostrar("Ingresando usuario de SAP")
        
        # Autenticación Microsoft
        if self.autentificacion_microsoft_activo:
            self.ingresar_texto(By.NAME ,'loginfmt', self.obtener_usuario_sap()) 
            self.click_button("Siguiente", By.ID, 'idSIButton9')
            
            # Pequeña demora para permitir que la página se actualice
            self.demora(1 if self.dev else 2)
            
            if self._ingreso_correcto():
                self.mostrar("Usuario ingresado correctamente")
                return True
            
            raise ValueError("Error al ingresar el usuario de SAP con autenticación Microsoft.")
        
        # Autenticación SAP
        if self.autentificacion_sap_activo:
            try:
                self.ingresar_texto(By.ID, 'USERNAME_FIELD-inner', self.obtener_usuario_sap())
                self.mostrar("Usuario ingresado correctamente")
                return True
            except Exception as e:
                raise ValueError("Error al ingresar el usuario de SAP con autenticación SAP.") from e
        
        if tab:
            import pyautogui
            pyautogui.press('tab')
        
        return False
    
    def _ingresar_contrasena(self, enter: bool = False) -> bool:
        """
        Ingresa la contraseña de SAP.

        En caso de autenticación Microsoft, ingresa la contraseña en el campo correspondiente y hace clic en "Iniciar sesión".
        En caso de autenticación SAP, ingresa la contraseña en el campo correspondiente y hace clic en "Continuar".

        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.

        ---
        ### Ejemplo
        ```python
        self._ingresar_contrasena():
        ```
        >>> True  # Si la contraseña se ingresó correctamente

        ---
        ### Raises
        #### ValueError
        - Si la contraseña SAP no está configurada.
        - Si hay un error al ingresar la contraseña de SAP con autenticación Microsoft o SAP.
        """
        self.mostrar("Ingresando contraseña de SAP")
        
        # Autenticación Microsoft
        if self.autentificacion_microsoft_activo:
            self.ingresar_texto(By.ID, 'i0118', self.obtener_clave_sap())
            self.click_button("Iniciar sesión", By.ID, 'idSIButton9')
            
            # Demora más larga para autenticación (proceso más complejo)
            self.demora(2 if self.dev else 3)
            
            if self._ingreso_correcto():
                self.mostrar("Contraseña ingresada correctamente")
                return True

            raise ValueError("Error al ingresar la contraseña de SAP con autenticación Microsoft.")
            
        # Autenticación SAP
        if self.autentificacion_sap_activo:
            try:
                self.ingresar_texto(By.ID, 'PASSWORD_FIELD-inner', self.obtener_clave_sap())
                self.mostrar("Contraseña ingresada correctamente")
                return True
            except Exception as e:
                raise ValueError("Error al ingresar la contraseña de SAP con autenticación SAP.") from e

        if enter:
            import pyautogui
            pyautogui.press('enter')
        
        return False
    
    def _no_mantener_sesion_iniciada(self) -> None:
        """
        Selecciona la opción de no mantener la sesión iniciada.

        ---
        Se utiliza dentro del método `navegar_inicio_SAP()` y solo cuando en caso de autenticación Microsoft.

        ---
        ### Ejemplo
        ```python
        self._no_mantener_sesion_iniciada():
        ```
        >>> None  # Si la opción de no mantener sesión iniciada se seleccionó correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si hay un error al seleccionar la opción de no mantener sesión iniciada.
        """
        self.mostrar("Seleccionando opción de no mantener sesión iniciada")
        
        self.click_button("No", By.ID, 'idBtn_Back')
        
        # Pequeña demora para que se procese la selección
        self.demora(1 if self.dev else 2)
        
        if self._ingreso_correcto():
            self.mostrar("Opción de no mantener sesión iniciada seleccionada correctamente")
            return

        raise ValueError("Error al seleccionar la opción de no mantener sesión iniciada.")

    def _ingreso_correcto(self) -> bool:
        """
        Verifica que se haya ingresado correctamente cada paso de autenticación.
        
        Este método comprueba si se ha llegado a la página de inicio de SAP o si se ha encontrado un elemento específico que indica que el ingreso fue exitoso.
        
        ---
        Se utiliza dentro de los métodos `_ingresar_usuario()`, `_ingresar_contrasena()` y `_no_mantener_sesion_iniciada()`.
        
        ---
        ### Ejemplo
        ```python
        self._ingreso_correcto():
        ```
        >>> True  # Si el ingreso fue correcto
        """
        # Usar verificación rápida primero
        exitoso, descripcion = self._verificacion_rapida_login()
        
        if exitoso:
            self.mostrar(f"✅ {descripcion}")
            return True
        
        # Si la verificación rápida indica error definitivo, no continuar
        if "error" in descripcion.lower():
            self.mostrar(f"❌ {descripcion}", True)
            return False
        
        # Solo si estamos en estado intermedio, hacer verificación completa pero rápida
        self.mostrar(f"🔍 {descripcion} - Verificando elementos específicos...")
        
        try:
            # Reducir timeout para verificaciones específicas
            timeout_original = self.tiempo_demora
            self.tiempo_demora = 1  # 1 segundo para verificaciones rápidas
            
            # Verificar elementos de éxito específicos
            if self.encontrar_elemento(By.XPATH, '//*[@id="loginHeader"]/div', False):
                return True
            if self.encontrar_elemento(By.XPATH, '//*[@id="lightbox"]/div[3]/div/div[2]/div/div[1]', False):
                return True
                
        finally:
            # Restaurar timeout original
            self.tiempo_demora = timeout_original
        
        return False
    
    def _verificacion_rapida_login(self) -> tuple[bool, str]:
        """
        Verificación rápida y optimizada del estado de login.
        
        Utiliza una estrategia de verificación por prioridad:
        1. Verificación de título (más rápida)
        2. Verificación de URL actual
        3. Búsqueda rápida de elementos clave
        
        Returns:
            tuple[bool, str]: (estado_exitoso, descripcion_estado)
        """
        # 1. Verificación más rápida: título de página
        titulo_actual = self.driver.title
        if titulo_actual == "Página de inicio":
            return True, "Login exitoso - Página de inicio alcanzada"
        
        # 2. Verificación de URL actual para detectar redirecciones
        url_actual = self.driver.current_url.lower()
        if "inicio" in url_actual or "home" in url_actual or "dashboard" in url_actual:
            return True, "Login exitoso - URL de inicio detectada"
        
        # 3. Verificación rápida de elementos de error (timeout muy reducido)
        try:
            timeout_original = self.tiempo_demora
            # Timeout ultra-rápido: 0.3s en dev, 0.5s en prod
            self.tiempo_demora = 0.3 if self.dev else 0.5
            
            if self.encontrar_elemento(By.ID, 'usernameError', False):
                return False, "Error de usuario detectado"
            if self.encontrar_elemento(By.ID, 'passwordError', False):
                return False, "Error de contraseña detectado"
                
        finally:
            self.tiempo_demora = timeout_original
        
        # 4. Verificar si estamos en una página de login/autenticación
        if any(keyword in titulo_actual.lower() for keyword in ["login", "iniciar", "autenticación", "sign"]):
            return False, f"Aún en página de login: {titulo_actual}"
        
        # 5. Verificar indicadores de carga o progreso
        if any(keyword in titulo_actual.lower() for keyword in ["cargando", "loading", "procesando"]):
            return False, f"Página en proceso de carga: {titulo_actual}"
        
        # 6. Si llegamos aquí, asumir progreso pero no confirmar éxito total
        return False, f"Estado intermedio - Título: {titulo_actual}"
                
    def ir_a_transaccion(self, codigo_transaccion: str) -> None:
        """
        Navega a una transacción específica en SAP a través de su código.
        
        Busca la transacción en el mapa de transacciones y navega a la URL correspondiente comprobando el acceso correcto al mismo.
        
        ---
        ### Ejemplo
        ```python
        codigo_transaccion = 'OB08'
        sap = SAP(base_url='https://sap.example.com')
        sap.set_credenciales_usuario('usuario', 'clave')
        sap.navegar_inicio_SAP()
        sap.ir_a_transaccion(codigo_transaccion)
        ```
        >>> None  # Si la transacción se navega correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si SAP no ha sido iniciado
        - Si la transacción no se encuentra en el mapa de transacciones.
        - Si se encuentra una alerta desconocida.
        #### PermissionError
        - Si no se tiene acceso a la transacción.
        - Si los datos están bloqueados para la transacción.        
        """
        
        if self.sap_iniciado is False:
            raise ValueError("SAP no ha sido iniciado. Use navegar_inicio_SAP() primero.")
        
        self.mostrar(f"Navegando a la transacción {codigo_transaccion}")

        transaccion = self.__obtener_transaccion_por_codigo(codigo_transaccion)
        self.navegar(f"{self.base_url}{transaccion}")
        self.__comprobar_acceso_transaccion()
        
        self.mostrar(f"Transacción {codigo_transaccion} navegada correctamente")
        
    def __obtener_transaccion_por_codigo(self, codigo_transaccion: str) -> str:
        """ 
        Obtiene la url relativa de la transacción por su código si es que existe en el mapa de transacciones.
        Si no se encuentra, lanza una excepción.
        
        ---
        Se utiliza dentro del metodo `ir_a_transaccion()`.
        
        ---
        Ejemplo
        ```python
        codigo = 'OB08'
        transaccion = self.__obtener_transaccion_por_codigo(codigo)
        ```
        >>> "Shell-startGUI?sap-ui2-tcode=OB08&sap-system=FIORI_MENU"

        ---
        ### Raises 
        #### ValueError: 
        - Si la transacción no se encuentra en el mapa de transacciones.
        """
        
        transaccion = self.mapa_transacciones.get(codigo_transaccion)
        
        if transaccion is None:
            raise ValueError(f"Transacción {codigo_transaccion} no encontrada en el mapa de transacciones")

        return transaccion
    
    def __comprobar_acceso_transaccion(self) -> None:
        """
        Comprueba el acceso a la transacción.
        
        ---
        Se utiliza dentro del metodo `ir_a_transaccion()`.
        
        ---
        Ejemplo
        ```python
        codigo_transaccion = 'OB08'
        transaccion = self.__obtener_transaccion_por_codigo(codigo_transaccion)
        self.navegar(f"{self.base_url}{transaccion}")
        self.__comprobar_acceso_transaccion()
        ```
        >>> None  # Si el acceso a la transacción se verifica correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si se encuentra una alerta desconocida.
        #### PermissionError
        - Si no se tiene autorización para la transacción.
        - Si los datos están bloqueados para la transacción.
        """
        self.mostrar("Comprobando acceso a la transacción")
        
        alerta = self.__buscar_alertas()
        if alerta:
            self.mostrar(f"Alerta encontrada: {alerta}", True)
            if 'No tiene autorización' in alerta:
                raise PermissionError("No tiene autorización para esta transacción")
            elif 'Datos bloqueados' in alerta:
                raise PermissionError("Datos bloqueados para esta transacción")
            else:
                raise ValueError(f"Alerta desconocida: {alerta}")   
            
        self.mostrar("Acceso verificado correctamente")         
    
    def __buscar_alertas(self) -> str|None:
        """ 
        Busca alertas emergentes en SAP. 
        
        En caso de encontrar una alerta, devuelve el texto de la alerta.
        
        ---
        Se utiliza dentro del metodo `__comprobar_acceso_transaccion()`.
        
        ---
        Ejemplo
        ```python
        alerta = self.__buscar_alertas()
        ```
        >>> "Alerta\\nNo tiene autorización para esta transacción\\nAcepter\\nCancelar"  # Si se encuentra una alerta
        """
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsPWNew', False)
        
        if span_alerta and texto_alerta:
            return texto_alerta.strip().split('\n')[0]
        
        return None
    
    def buscar_alerta_transaccion(self) -> dict[str, bool | str] | None:
        """ 
        Busca una alerta de transacción en SAP.
        
        Busca un elemento con la clase `lsMessageBar` en los iframes de la página y verifica si contiene una alerta de error o una alerta de transacción.  
        En caso de encontrar una alerta, evalua si es un error buscando clases como `lsMessageBar__icon--Error` o `lsMessageBar__image--Error` en los hijos del elemento encontrado.
        
        ---
        Ejemplo
        ```python
        alerta = self.buscar_alerta_transaccion()
        ```
        >>> {'isError': True, 'content': 'Alerta de error encontrada'}
        >>> {'isError': False, 'content': 'Alerta de transacción encontrada'}
        
        """
        self.mostrar("Obteniendo alerta de transacción")
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsMessageBar')
        
        if span_alerta and texto_alerta:
            # Verifica si algún hijo tiene clase de error
            hijos = span_alerta.find_elements(By.XPATH, ".//*")
            for h in hijos:
                clase_hijo = h.get_attribute("class")
                if clase_hijo is not None:
                    if "lsMessageBar__icon--Error" in clase_hijo or "lsMessageBar__image--Error" in clase_hijo:
                        self.mostrar("Alerta de error encontrada", True)
                        isError = True
                        break    
            else:
                self.mostrar("Alerta de transacción encontrada", True)
                isError = False
            
            return {'isError': isError, 'content': texto_alerta.strip().split('\n')[0]}
        
        self.mostrar("No se encontró alerta de transacción", True)
        return None