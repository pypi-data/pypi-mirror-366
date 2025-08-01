import pytest
import os
from unittest.mock import patch, MagicMock
from src.glgrpa.transacciones.OB08 import OB08
import pandas as pd
from selenium.webdriver.common.by import By

# Skip tests que requieren navegador en entornos CI/CD
skip_browser_tests = pytest.mark.skipif(
    bool(os.getenv('CI')) or bool(os.getenv('GITHUB_ACTIONS')) or bool(os.getenv('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI')),
    reason="Tests de navegador skipeados en entornos CI/CD"
)


@pytest.fixture
def ob08_dev() -> OB08:
    """Fixture para inicializar la clase OB08 en modo dev"""
    return OB08(
        base_url='https://saplgdqa.losgrobo.com:44302/sap/bc/ui5_ui5/ui2/ushell/shells/abap',
        usuario='usuario.test@losgrobo.com',
        clave='password_test',
        driver=None,
        dev=True
    )


@pytest.fixture
def ob08_prod() -> OB08:
    """Fixture para inicializar la clase OB08 en modo producción"""
    return OB08(
        base_url='https://saplgdqa.losgrobo.com:44302/sap/bc/ui5_ui5/ui2/ushell/shells/abap',
        usuario='usuario.test@losgrobo.com',
        clave='password_test',
        driver=None,
        dev=False
    )


@skip_browser_tests
def test_metodos_formato_divisa(ob08_dev: OB08):
    """Prueba los métodos de formateo de divisas"""
    # Test formato_divisa
    assert ob08_dev.formato_divisa(100.5) == "100,5000"
    assert ob08_dev.formato_divisa("100,50") == "100,5000"
    assert ob08_dev.formato_divisa("1000,5") == "1.000,5000"
    
    # Test formato_tipo_cotizacion
    assert ob08_dev.formato_tipo_cotizacion('compra') == 'G'
    assert ob08_dev.formato_tipo_cotizacion('venta') == 'B'
    assert ob08_dev.formato_tipo_cotizacion('COMPRA') == 'G'
    assert ob08_dev.formato_tipo_cotizacion('VENTA') == 'B'
    
    # Test formato_moneda
    assert ob08_dev.formato_moneda('Dolar U.S.A') == 'USD'
    assert ob08_dev.formato_moneda('Euro') == 'EUR'
    assert ob08_dev.formato_moneda('Real Brasileño') == 'BRL'


@skip_browser_tests
def test_formato_fecha_cotizacion(ob08_dev: OB08):
    """Prueba el método de formateo de fecha (siempre ayer)"""
    from datetime import datetime, timedelta
    
    fecha_esperada = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    fecha_resultado = ob08_dev.formato_fecha_cotizacion()
    
    assert fecha_resultado == fecha_esperada
    
    # Test con formato diferente
    fecha_esperada_corta = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
    fecha_resultado_corta = ob08_dev.formato_fecha_cotizacion('%d%m%Y')
    
    assert fecha_resultado_corta == fecha_esperada_corta


@skip_browser_tests
@patch('src.glgrpa.transacciones.OB08.OB08.click_elemento_en_iframe')
def test_click_entradas_nuevas_elemento_exitoso(mock_click_iframe, ob08_dev: OB08):
    """Prueba que _click_entradas_nuevas_elemento funciona cuando encuentra el elemento"""
    # Configurar mock para que el primer método sea exitoso
    mock_click_iframe.return_value = True
    
    # Ejecutar la función
    resultado = ob08_dev._click_entradas_nuevas_elemento()
    
    # Verificar que retorna True
    assert resultado is True
    
    # Verificar que se llamó click_elemento_en_iframe
    assert mock_click_iframe.called
    
    # Verificar que se usó el primer xpath (title)
    mock_click_iframe.assert_called_with(By.XPATH, '//div[@title="Entradas nuevas (F5)"]')


@skip_browser_tests
@patch('src.glgrpa.transacciones.OB08.OB08.click_elemento_en_iframe')
def test_click_entradas_nuevas_elemento_fallback(mock_click_iframe, ob08_dev: OB08):
    """Prueba que _click_entradas_nuevas_elemento prueba múltiples estrategias"""
    # Configurar mock para que falle en los primeros intentos y tenga éxito en el quinto
    mock_click_iframe.side_effect = [False, False, False, False, True, False, False]
    
    # Ejecutar la función
    resultado = ob08_dev._click_entradas_nuevas_elemento()
    
    # Verificar que retorna True
    assert resultado is True
    
    # Verificar que se llamó click_elemento_en_iframe 5 veces
    assert mock_click_iframe.call_count == 5
    
    # Verificar que se usó el xpath del accesskey (método 5)
    calls = mock_click_iframe.call_args_list
    assert calls[4][0][1] == '//div[@accesskey="E"]'


@skip_browser_tests
@patch('src.glgrpa.transacciones.OB08.OB08.click_elemento_en_iframe')
def test_click_entradas_nuevas_elemento_todos_fallan(mock_click_iframe, ob08_dev: OB08):
    """Prueba que _click_entradas_nuevas_elemento retorna False cuando todos los métodos fallan"""
    # Configurar mock para que todos los métodos fallen
    mock_click_iframe.return_value = False
    
    # Ejecutar la función
    resultado = ob08_dev._click_entradas_nuevas_elemento()
    
    # Verificar que retorna False
    assert resultado is False
    
    # Verificar que se llamó click_elemento_en_iframe 7 veces (todos los métodos)
    assert mock_click_iframe.call_count == 7


@skip_browser_tests
@patch('src.glgrpa.transacciones.OB08.OB08._click_entradas_nuevas_elemento')
def test_entradas_nuevas_click_directo_exitoso(mock_click_elemento, ob08_dev: OB08):
    """Prueba que entradas_nuevas funciona cuando el click directo es exitoso"""
    # Configurar mocks
    mock_driver = MagicMock()
    mock_driver.title = 'Modificar vista "Tipos de cambio para la conversión": Resumen'
    ob08_dev.driver = mock_driver
    mock_click_elemento.return_value = True

    # Mock para simular cambio de título después del click
    def side_effect(*args):
        mock_driver.title = 'Entradas nuevas: Resumen de entradas añadidas'
        return True

    mock_click_elemento.side_effect = side_effect

    # Ejecutar la función
    resultado = ob08_dev.entradas_nuevas()

    # Verificar que retorna True
    assert resultado is True

    # Verificar que se llamó _click_entradas_nuevas_elemento
    mock_click_elemento.assert_called_once()

@skip_browser_tests
@patch('src.glgrpa.transacciones.OB08.OB08._click_entradas_nuevas_elemento')
@patch('src.glgrpa.transacciones.OB08.OB08.enviar_tecla_ventana')
@patch('src.glgrpa.transacciones.OB08.OB08.demora')
def test_entradas_nuevas_fallback_estrategias(mock_demora, mock_enviar_tecla, mock_click_elemento, ob08_dev: OB08):
    """Prueba que entradas_nuevas usa estrategias de fallback cuando el click directo falla"""
    # Configurar mocks
    mock_driver = MagicMock()
    mock_driver.title = 'Modificar vista "Tipos de cambio para la conversión": Resumen'
    ob08_dev.driver = mock_driver
    mock_click_elemento.return_value = False  # Click directo falla

    # Simular que después de F5 cambia el título
    def side_effect_f5(*args):
        if args[0] == 'F5':
            mock_driver.title = 'Entradas nuevas: Resumen de entradas añadidas'

    mock_enviar_tecla.side_effect = side_effect_f5

    # Ejecutar la función
    resultado = ob08_dev.entradas_nuevas()

    # Verificar que retorna True
    assert resultado is True

    # Verificar que se llamó _click_entradas_nuevas_elemento (estrategia 1)
    mock_click_elemento.assert_called_once()

    # Verificar que se llamó enviar_tecla_ventana con F5 (estrategia 2)
    mock_enviar_tecla.assert_called_with('F5')
    mock_enviar_tecla.assert_called_with('F5')


@skip_browser_tests
def test_armar_tabla_para_sap(ob08_dev: OB08):
    """Prueba la transformación de datos para formato SAP"""
    # Crear DataFrame de prueba
    data = {
        'Fecha': ['Dolar U.S.A', 'Euro'],
        'Compra': [1000.50, 1100.75],
        'Venta': [1005.25, 1105.80]
    }
    df_test = pd.DataFrame(data)
    
    # Ejecutar transformación  
    df_resultado = getattr(ob08_dev, '_OB08__armar_tabla_para_sap')(df_test)
    
    # Verificar estructura del resultado
    columnas_esperadas = [
        'TCot - Tipo de Cotización', 
        'Válido de', 
        'T/C cotizado indirectamente', 
        'X', 
        'Factor (de)', 
        'Moneda procedencia', 
        '=', 
        'T/C Cotizado directamente',
        'XX', 
        'Factor (a)',
        'Moneda de destino'
    ]
    
    assert list(df_resultado.columns) == columnas_esperadas
    
    # Verificar que hay registros (2 monedas x 3 tipos de cotización = 6 registros)
    assert len(df_resultado) == 6
    
    # Verificar tipos de cotización
    tipos_cotizacion = set(df_resultado['TCot - Tipo de Cotización'].unique())
    assert tipos_cotizacion == {'B', 'G', 'M'}
    
    # Verificar monedas de destino
    assert all(df_resultado['Moneda de destino'] == 'ARS')
    
    # Verificar formateo de monedas
    monedas_procedencia = set(df_resultado['Moneda procedencia'].unique())
    assert monedas_procedencia == {'USD', 'EUR'}


@skip_browser_tests
def test_convertir_tabla_sap_a_string(ob08_dev: OB08):
    """Prueba la conversión de DataFrame a string con formato SAP"""
    # Crear DataFrame de prueba simple
    data = {
        'Col1': ['A', 'B'],
        'Col2': ['1', '2'],
        'Col3': ['X', 'Y']
    }
    df_test = pd.DataFrame(data)
    
    # Ejecutar conversión
    resultado = getattr(ob08_dev, '_OB08__convertir_tabla_sap_a_string')(df_test)
    
    # Verificar formato (tabulador como separador, sin headers, sin índice)
    lineas = resultado.strip().split('\n')
    assert len(lineas) == 2  # 2 filas de datos
    
    # Verificar primera línea
    primera_linea = lineas[0].split('\t')
    assert primera_linea == ['A', '1', 'X']
    
    # Verificar segunda línea
    segunda_linea = lineas[1].split('\t')
    assert segunda_linea == ['B', '2', 'Y']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
