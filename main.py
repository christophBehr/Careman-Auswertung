from datetime import date, datetime
import os
import io
import csv
from numpy.core.fromnumeric import sort
import pandas as pd
import numpy as np
from pandas.core.base import PandasObject
import plotly.express as px

def lese_daten(tmp_txt, export_txt):
    """
    Sucht nach der markierung [1110] in der export.txt, dort befinden sich alle Einträge der durchgeführten Fahrt in einer Zeile.
    Die Datei tmp.txt wird erstellt, die durchgeführten Fahrten werden in je einer Zeile gespeichert. 
    tmp.txt wird bei jedem durchgang überschrieben.
    """

    tmp = open(tmp_txt, "w")
    with io.open(export_txt, "r") as tmp_data:
        roh_data = tmp_data.readlines()
        for lines in roh_data:
            if "[1110]" in lines:
                tmp.writelines([lines])
    tmp.close()

def erstelle_csv(tmp_txt, tmp_csv):
    """
    Erstellt eine temporäre .csv Datei. Jeder, durch ein ";" getrennten Eintrag ergält eine eigene Zelle.
    Die Datei wird nach jedem durchgang überschrieben. 
    """

    with io.open(tmp_txt, "r", encoding="utf8") as text_file, open(tmp_csv, "w", newline="") as csv_file:
        stripped = (line.strip() for line in text_file)
        lines = (line.split() for line in stripped if line)
        writer = csv.writer(csv_file)
        writer.writerows(lines)

def bereinigung_csv(tmp_csv, archiv_csv, arbeitsmappe_csv):
    """
    Liest die Rohdaten aus der temporären csv und schreibt diese in das Archiv. Neue einträge werden angehängt.
    TODO Funktion zur Duplikat entfernung
    Erstellt eine csv und xlsx Datei für die Auslastungsanalyse
    """
    tmp_data = pd.read_csv(tmp_csv, sep=";", header=None, encoding="latin1")
    tmp_frame = pd.DataFrame(tmp_data)

    if not os.path.isfile(archiv_csv):
        tmp_frame.to_csv(archiv_csv, header="column_names", index=None)
    else:
        tmp_frame.to_csv(archiv_csv, mode="a", header=False, index=None)

    frame = tmp_frame.iloc[: , [1, 8, 47, 46 ,48, 74]]
    frame.to_csv(arbeitsmappe_csv, header=None)
    data = pd.read_csv(arbeitsmappe_csv, sep=",", header=None,  names=["Index", "KFZ", "Einsatz Nr.", "Datum", "Start", "Ende", "Infektion"], encoding="utf8")
    data.sort_values(by=["Datum", "KFZ"])
    #Ausgabe csv für debuging
    data.to_csv("data_auswertung.csv", index=False)
    data.to_excel("data_auswertung.xlsx", index = False)

def pie_chart():
    """
    Kuchen Diagramm aller von KFZ durchgeführten Fahrten.
    TODO: Zeitbereichsauswahl GUI Integration
    """

    df = pd.read_csv("data_auswertung.csv", index_col="Index")
    ktw_fahrten = []
    ktw_list = sorted(df.KFZ.unique())
    for ktw in ktw_list:
        df_series = pd.DataFrame(df, columns=["KFZ"])
        series = df_series.squeeze()
        anz_fahrten = series.str.count(ktw).sum()
        ktw_fahrten.append(anz_fahrten)
    df_fahrten = pd.DataFrame(list(zip(ktw_list, ktw_fahrten)), columns=["KFZ", "Anzahl Fahrten"])
    fig_pi = px.pie(df_fahrten, names=ktw_list, values=ktw_fahrten)

    fig_pi.show()    

def balken_datum(start_datum, end_datum):
    """
    Zeitlicher Verlauf der Fahrten von KFZ in einem gewählten Zeitbereich
    TODO:GUI Integration
    """

    df = pd.read_csv("data_auswertung.csv", index_col="Index")
    df = pd.DataFrame(df)
    df["Datum"] = pd.to_datetime(df["Datum"])
    bereich = (df["Datum"] >= start_datum) & (df["Datum"] <= end_datum)
    df_bereich = df.loc[bereich]

    fahrten = df_bereich.groupby(["Datum", "KFZ"]).size()

    fahrten_new = fahrten.to_frame(name="Fahrten").reset_index()
    fig_lines = px.line(fahrten_new, x="Datum", y="Fahrten", color="KFZ")
    fig_lines.show()

def run():
    """
    Führt die Funktionen in Reihenfolge aus.
    TODO GUI
    """

    print("Einlesen von Date j/n ?")
    einlesen = input("")
    if einlesen == "j":
        lese_daten("tmp.txt", "TbExport_3276.txt")
        print("Einlesen abgeschlossen")
    elif einlesen == "n":    
        print("Erstelle csv Datei j/n?")
        erstelle = input("")
        if erstelle == "j":
            erstelle_csv("tmp.txt", "csv_test.csv")
            print("csv Datei erstellt")
        elif erstelle == "n":
            print("Ausgabe der Auswerung.")
            bereinigung_csv("csv_test.csv", "archiv.csv", "arbeitsmappe.csv")
    else:
        quit()


#Wähle Startdatum
start_datum = "2020-10-01"
#Wähle Enddatum
end_datum = "2020-10-31"

pie_chart()
balken_datum(start_datum, end_datum)
#run()
