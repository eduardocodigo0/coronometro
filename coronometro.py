# -*- coding: UTF-8 -*

import requests
import re
import sqlite3
import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np



class Country:

    def __init__(self, name, infected, deaths, recovered):
        self.name = name
        self.infected = infected
        self.deaths = deaths
        self.recovered = recovered
        self.day = datetime.datetime.today().day
        self.month = datetime.datetime.today().month
        self.year = datetime.datetime.today().year

    def update(self, name, infected, deaths, recovered):
        self.name = name
        self.infected = infected
        self.deaths = deaths
        self.recovered = recovered
        self.day = datetime.datetime.today().day
        self.month = datetime.datetime.today().month
        self.year = datetime.datetime.today().year


def insert(conn, country_list):
    c = conn.cursor()
    sqlite_insert_query = "INSERT INTO country (name, infected, death, recovered, day, month, year) VALUES(?,?,?,?,?,?,?)"

    for country in country_list:
        data_tuple = (country.name, country.infected, country.deaths, country.recovered, country.day, country.month, country.year)
        count = c.execute(sqlite_insert_query, data_tuple)

    conn.commit()
    c.close()

def create_connection():

    conn = None
    try:
        conn = sqlite3.connect("banco.db")

        try:
            sql = '''CREATE TABLE "country" (
                                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                "name"	TEXT NOT NULL,
                                "infected"	INTEGER NOT NULL,
                                "death"	INTEGER NOT NULL,
                                "recovered"	INTEGER NOT NULL,
                                "day" INTEGER NOT NULL,
                                "month" INTEGER NOT NULL,
                                "year" INTEGER NOT NULL
                            );'''
            c = conn.cursor()
            c.execute(sql)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
    finally:
        if conn:
            return conn
        else:
            conn = sqlite3.connect("banco.db")
            return conn



def get_data(countryes):

    data = []
    try:
        s = requests.Session()
        res = s.get("https://corona-stats.online/?source=2")

        for c in countryes:
            country_data = re.findall(r'^.*' + c + r'.*$', res.text.lower(), re.MULTILINE)
            data.append(country_data)
    except():
        print("Verifique sua conexao com a internet")

    return data

def update_objects(countryes, country_list):
    data = get_data(countryes)

    for i,d in enumerate(data):
        d[0] = re.sub(r'[│▲]', '', d[0])
        d[0] = re.sub(r'║', '', d[0])
        d[0] = re.sub(r'\s+', ' ', d[0])
        details = d[0].split(" ")
        country_list[i].update(details[2], details[3], details[5], details[7])


def select_all(conn):

    cur = conn.cursor()
    cur.execute("SELECT * FROM country")
    row = cur.fetchall()

    return row


def alread_requested_today(conn):

    cur = conn.cursor()
    cur.execute("SELECT day, month, year FROM country ORDER BY id DESC LIMIT 1")

    row = cur.fetchall()
    if datetime.datetime.today().day > row[0][0]:
        if datetime.datetime.today().month >= row[0][1] and datetime.datetime.today().year >= row[0][2]:
            return False
        else:
            return True
    else:
        if datetime.datetime.today().month > row[0][1] and datetime.datetime.today().year >= row[0][2]:
            return False
        else:
            return True



def request_data():
    countryes = ["portugal", "brazil", "usa", "china", "italy"]

    country_list = []


    data = get_data(countryes)

    for d in data:

        d[0] = re.sub(r'[│▲]', '', d[0])
        d[0] = re.sub(r'║', '', d[0])
        d[0] = re.sub(r'\s+', ' ', d[0])
        details = d[0].split(" ")
        #print(details)
        country_list.append(Country(details[2], details[3], details[5], details[7]))


    update_objects(countryes, country_list)
    if(not alread_requested_today(create_connection())):
        insert(create_connection(), country_list)




    for i, _ in enumerate(country_list):
        print("Pais: "+country_list[i].name)
        print("Infectados: "+country_list[i].infected)
        print("Mortos: "+country_list[i].deaths)
        print("Recuperados: "+country_list[i].recovered)
        print("------------------------------")



###### GUI #######

def on_closing():
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()
        exit()


request_data()


window = tk.Tk()

window.title("Coronometro 1.0")
window['bg'] = "#191919"
window.geometry('900x600')
window.protocol("WM_DELETE_WINDOW", on_closing)

brazil = []
usa = []
italy = []
portugal = []
china = []

date = []

data = select_all(create_connection())

last_date = ""
for d in data:
    new_date = datetime.datetime(d[7], d[6], d[5], 0, 0)
    if last_date != new_date.strftime("%d%m%y"):
        date.append(new_date.strftime("%d%m%y"))
        last_date = new_date.strftime("%d%m%y")
        print(last_date)

    if d[1] == "brazil":
        brazil.append(d[2])
    if d[1] == "italy":
        italy.append(d[2])
    if d[1] == "portugal":
        portugal.append(d[2])
    if d[1] == "china":
        china.append(d[2])
    if d[1] == "usa":
        usa.append(d[2])


brazil = np.asarray(brazil)
italy = np.asarray(italy)
portugal = np.asarray(portugal)
china = np.asarray(china)
usa = np.asarray(usa)

brazil = np.char.replace(brazil, ",", ".")
italy = np.char.replace(italy, ",", ".")
portugal = np.char.replace(portugal, ",", ".")
china = np.char.replace(china, ",", ".")
usa = np.char.replace(usa, ",", ".")

brazil = brazil.astype(float)
italy = italy.astype(float)
portugal = portugal.astype(float)
china = china.astype(float)
usa = usa.astype(float)

fig = Figure(figsize=(7, 5), dpi=100)

fig.add_subplot(111).set_xlabel("Time Line")
fig.add_subplot(111).set_ylabel("Infected Number(thousands)")
fig.add_subplot(111).plot(date, brazil, color='green')
fig.add_subplot(111).plot(date, italy, color='yellow')
fig.add_subplot(111).plot(date, portugal, color='pink')
fig.add_subplot(111).plot(date, china, color='red')
fig.add_subplot(111).plot(date, usa, color='blue')

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0)

toolbarFrame = tk.Frame(master=window)
toolbarFrame.grid(row=1, column=0)
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()
canvas.get_tk_widget().grid(row=0, column=0)


while len(data) >= 6:
    data.pop(0)


text_frame = tk.Frame(master=window, bg = "#191919")
text_frame.grid(row=0, column=1)

row_count = 0

for i, d in enumerate(data):
    color = []
    if d[1] == "brazil":
        color = "green"
    if d[1] == "italy":
        color = "yellow"
    if d[1] == "portugal":
        color = "pink"
    if d[1] == "china":
        color = "red"
    if d[1] == "usa":
        color = "blue"



    tk.Label(text_frame, text=d[1].upper(), fg=color, bg="#191919", font='Arial 12 bold').grid(row=row_count, column=1,padx=15, pady=2)
    row_count += 1
    tk.Label(text_frame, text="Infectados: " + str(d[2]), fg="white", bg="#191919", font='Arial 11 bold').grid(row=row_count, column=1,padx=5, pady=1)
    row_count += 1
    tk.Label(text_frame, text="Mortos: " + str(d[3]), fg="white", bg="#191919", font='Arial 11 bold').grid(row=row_count, column=1, padx=5, pady=1)
    row_count += 1
    tk.Label(text_frame, text="Recuperados: " + str(d[4]), fg="white", bg="#191919", font='Arial 11 bold').grid(row=row_count, column=1, padx=5, pady=1)
    row_count += 1


window.mainloop()