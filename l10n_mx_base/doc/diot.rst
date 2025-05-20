========================================================
DECLARACIÓN INFORMATIVA DE OPERACIONES CON TERCEROS DIOT
========================================================

La declaración informativa de operaciones con terceros es una obligación
fiscal prevista en la Ley del Impuesto al Valor Agregado (IVA), que
consiste en proporcionar mensualmente al Servicio de Administración
Tributaria (SAT), información sobre las operaciones con sus proveedores.

Deben presentarla todos los contribuyentes persona físicas y morales que
sean sujetos del IVA.

CUÁNDO DEBE PRESENTARSE Y MEDIANTE QUÉ FORMATO
----------------------------------------------

La información deberá ser presentada mediante el formato electrónico A-29.

Las personas físicas y morales presentarán la DIOT, durante el mes
inmediato posterior al que corresponda dicha información.

Más información en https://goo.gl/5JmPQu

Configuration
=============

To configure this module, you need to:

#. Ir a configuraciones de contabilidad, activar el campo
   `Allow Tax Cash Basis` para permitir que se generen movimientos de iva
   efectivamente pagado, y seleccionar el diario en el campo
   `Tax Cash Basis Journal` el cual se asignará a los movimientos de iva.

   .. image:: accounting_settings_en.png
   .. image:: accounting_settings_es.png

#. Ir a cada uno de los impuestos que afectan el iva efectivamente pagado,
   de compras, activar el campo `Use Cash Basis` para indicar que generará
   movimiento de iva, y colocar la cuenta en el campo `Tax Received Account`
   que será la que se afectara en estos. Para impuestos de retención debe
   colocarse la categoría IVA-RET, para impuestos exentos la categoría
   IVA-EXENTO y para cualquier impuesto, ya sea 0 o 16, la categoría IVA,
   esto para tener el agrupado en las lineas para dichos impuestos.

   .. image:: accounting_settings_en.png
   .. image:: accounting_settings_es.png

#. Para el DIOT es necesario colocar alguna información en el proveedor, la
   cual será utilizada para llenar el reporte.

   .. image:: partner_configuration_en.png
   .. image:: partner_configuration_es.png

   Para saber si el proveedor es nacional o extranjero, se hace en base al país
   México, a lo cúal todos los direfentes a este, son extranjeros.

   La nacionalidad se hace en base al país, con un campo ya definido en este,
   ya se encuentra cargada la informacion de nacionalidades.

   De igual manera el código del país ya esta cargado en el registro, y es de
   hay donde se esta tomando.

   El campo tipo de operación hay que definirlo directamente, de acuerdo a las
   operaciones que se realicen con ese proveedor.

Usage
=====

To use this module, you need to:

El DIOT trabaja con las poliazas de iva efectivamente pagado, las cuales
se generan al momento de pagar una factura.

#. Para obtener el reporte del DIOT, hay que ir al menú de reportes
   contables, y entrar al repote `Transactions with third parties [ DIOT ]`

   En el cual se visualiza el reporte antes de ser exportado a TXT, que
   es como el SAT lo require.

   .. image:: diot_report_en.png
   .. image:: diot_report_es.png

#. Para filtrar por el periodo a reportar se tiene la opción de filtrar por
   mes, o por fechas especificas:

   .. image:: report_period_en.png
   .. image:: report_period_es.png

#. Antes de obtener el TXT a envíar al SAT, se pueden ver en el reporte
   los movimientos que estan generando los montos, esto deslegado cada una
   de las lineas que se agregarón en el reporte.

   .. image:: diot_lines_en.png
   .. image:: diot_lines_es.png

   Como se observa en la captura, algunas cantidades tienen su monto en
   negativo, lo cual idica que ese movimiento fue generado desde una nota
   de credito, y se resta al monto total a reportar.

#. Aunque el reporte del DIOT es requerido en TXT únicamente, se cuenta
   con la opción de imprimir el reporte en PDF o XLS. Para obtener el
   TXT basta con presionar el botón con esa opción, y un archivo será
   descargado.

   .. image:: diot_txt.png

#. Para asegurar que la información a envíar en el reporte del DIOT esta
   completa, se tienen algunas validaciones, como lo son:

   - Verificar que la información en el proveedor esta completa,
   - Verificar que no se reporten movimientos sin valor en ninguna
     de las columnas,
   - Verificar que no se reporten movimientos sin proveedor.

   Se agregarón estas validaciones al momento de intentar obtener el TXT, por
   lo tanto, en caso de aguna de estas excepciones, en lugar de obtener el
   TXT, se enviará al usuario a la vista relacionada para que aplique las
   correciones antes de exportar el documento.

   Si alguno de los movimientos no tiene proveedor relacionado, se obtendrá
   esta vista:

   .. image:: lines_wo_partner_en.png

   Para el caso que el proveedor no tenga la información completa para el DIOT,
   se obtendrá esta vista:

   .. image:: partner_wo_info_en.png

   Y para los casos donde no se este reportando ningún monto en el reporte, la
   vista a mostrar es la siguiente:

   .. image:: lines_wo_amount_en.png

   Si en este caso, se desea que el movimiento no se considere en el reporte
   del DIOT, por cualquier razón, se cuenta con el campo `Not consider in DIOT`,
   si este campo esta activo, no será mostrado ni exportado en el TXT.

   .. image:: diot_not_consider_en.png
   .. image:: diot_not_consider_es.png

