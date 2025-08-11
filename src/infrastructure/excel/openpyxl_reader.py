from openpyxl import load_workbook
from src.excel_bigquery.core.use_cases.interfaces.excel_reader import excel_reader
import pandas as pd


path = "D://00-Grupo Llyrod//01-Banano//02-Programa//upload_banano_gcp//data//input//1. JPN Weight inspection//0. Nittsu Matias//"


def load_excel(pt):
    excel, warehouse = excel_reader(pt)
    dataframes = []

    for nombre, xls in excel:
        wb_obj = load_workbook(xls)
        sheet_obj = wb_obj.active

        # cell_obj = sheet_obj["A1"]
        # print(cell_obj.value)

        # data = []

        puerto = sheet_obj["G1"].value.upper()
        anio_texto = sheet_obj["A2"].value
        anio = int(anio_texto[4:])
        semana = int(sheet_obj["T1"].value)
        archivo = nombre
        buque = sheet_obj["B1"].value
        n_archivo = sheet_obj["Q1"].value
        id_archivo = f"{puerto}_{anio}_{archivo}_{n_archivo}"


        data = {
            "id_archivo": [id_archivo],
            "archivo": [archivo],
            "warehouse": [warehouse],
            "anio": [anio],
            "semana": [semana],
            "puerto": [puerto],
            "buque": [buque]
        }

        df = pd.DataFrame(data)
        dataframes.append(df)

    # if dataframes:
        result = pd.concat(dataframes, ignore_index=True)
        # print(result)
        return result
    # else:
    #     print("No hay datos para mostrar.")
    #     return pd.DataFrame()

carga = load_excel(path)
print(carga)





















# print(excel)


carga = load_excel(path)

print(carga)



