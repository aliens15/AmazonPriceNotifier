import tkinter as tk  # per la gui
import win32ctypes.pywin32
import requests
from bs4 import BeautifulSoup
import smtplib
import time
# file per prendere l'app e text per text
from tkinter import filedialog, Text, simpledialog
import os  # per fare funzionare l'app

root = tk.Tk()  # dove attaccare ...

firstTurn = True

items = []
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}


class Item:

    def __init__(self, title, price, link, priceTarget):
        self.price = price
        self.title = title
        self.link = link
        self.priceTarget = priceTarget

# open file saved


def readFileSaved():
    if os.path.isfile('save.txt'):
        with open('save.txt') as f:
            if os.stat('save.txt').st_size != 0:
                # bisogna inserire il controllo su | come carattere per staccare le stringhe nel foglio txt
                tempApps = f.read()
                nItems = tempApps.split('~')
                print(len(nItems))
                for tokens in nItems:
                    if tokens:
                        listTots = tokens.split('|')
                        title = listTots[0]
                        price = float(listTots[1])
                        link = listTots[2]
                        priceTarget = float(listTots[3])

                        item = Item(title, price, link, priceTarget)
                        items.append(item)

                        if len(title) > 15:
                            title = title[:15]

                        label1 = tk.Label(frame, text=title + ":  " + "Price " + str(
                            price) + " | " + "Price target " + str(priceTarget), bg="grey")
                        label1.pack()
                        print(title)
                        print(price)
                        print(link)
                        print(priceTarget)


def addLinks():

    price = None
    title = None

    link = simpledialog.askstring("Insert a link", root)
    if link:
        priceTarget = simpledialog.askinteger("Insert the Target Price", root)
    # getStuff(link)
    page = requests.get(link, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    while title is None:
        title = soup.find(id="productTitle")
        if title is not None:
            title = title.get_text()
            title = title.strip()
            break
        else:
            title = soup.find(id="ebooksProductTitle")
            if title is not None:
                title = title.get_text()
                break

    while price is None:
        price = soup.find(id="priceblock_ourprice")

        if price is not None:
            price = price.get_text()
            convertedPrice = float(price[:-3].replace(',', '.'))
            break
        else:
            price = soup.find(id="priceblock_saleprice")

            if price is not None:
                price = price.get_text()
                convertedPrice = float(price[:-3].replace(',', '.'))
                break
            else:
                priceArr = soup.find_all(
                    class_="a-size-medium a-color-price offer-price a-text-normal")
                for el in priceArr:
                    if el is not None:
                        price = el.get_text()
                        price = price.strip()
                        # price = price.replace(" ", "") #altro metodo
                        try:
                            convertedPrice = float(
                                price[4:-1].replace(',', '.'))
                        except:
                            convertedPrice = float(
                                price[:-3].replace(',', '.'))
                        while convertedPrice == 0:
                            i = -3
                            convertedPrice = float(
                                price[:-i].replace(',', '.'))
                            i -= 1
                        break
                else:
                    priceArr = soup.find_all(
                        class_="a-size-medium a-color-price")
                    for el in priceArr:
                        if el is not None:
                            price = el.get_text()
                            price = price.strip()
                            # price = price.replace(" ", "") #altro metodo
                            convertedPrice = float(
                                price[4:-1].replace(',', '.'))
                            break
                    else:
                        priceArr = soup.find_all(
                            class_="a-size-base a-color-price a-color-price")
                        for el in priceArr:
                            if el is not None:
                                price = el.get_text()
                                price = price.strip()
                                # price = price.replace(" ", "") #altro metodo
                                convertedPrice = float(
                                    price[:-1].replace(',', '.'))
                                break
                        else:
                            priceArr = soup.find_all(
                                class_="a-size-base a-color-price offer-price a-text-normal")
                            for el in priceArr:
                                if el is not None:
                                    price = el.get_text()
                                    price = price.strip()
                                    # price = price.replace(" ", "") #altro metodo
                                    convertedPrice = float(
                                        price[:-1].replace(',', '.'))
                                    break
        break
    item = Item(title, convertedPrice, link, priceTarget)
    items.append(item)
    if len(title) > 20:
        title = title[:20]
    label = tk.Label(frame, text=title + ":  " + "Price " +
                     str(convertedPrice) + " | " + "Price target " + str(priceTarget), bg="grey")
    label.pack()
    print(items[0].price)
    print(items[0].title)
    print(items[0].priceTarget)


# def getStuff(link):
# build the item object
# item = Item(convertedPrice, title, link)
# items.append(item)
canvas = tk.Canvas(root, height=500, width=500, bg='#263D42')
canvas.pack()

frame = tk.Frame(root, bg="#D3D3D3")

frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.075)
# rel + x/y indica le x o le y
readFileSaved()

inserLink = tk.Button(root, text="Insert Link", padx=10, pady=5,
                      fg="white", bg="#263D42", command=addLinks)

inserLink.pack()


root.mainloop()

# save datas in a file, if not empty he erase it and recreate
with open('save.txt', 'w') as f:
    if os.stat('save.txt').st_size != 0:
        f.truncate()
    for item in items:
        # scrivere in un file le app nell-array
        f.write(item.title + '|' + str(item.price) + '|' +
                item.link + '|' + str(item.priceTarget) + '~')
