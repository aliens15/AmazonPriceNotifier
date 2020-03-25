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
                for tokens in nItems:
                    if tokens:
                        listTots = tokens.split('|')
                        title = listTots[0]
                        price = float(listTots[1])
                        link = listTots[2]
                        priceTarget = float(listTots[3])

                        page = requests.get(link, headers=headers)
                        soup = BeautifulSoup(page.content, 'html.parser')
                        # check for lower price (all the items in the save.txt are checked)
                        newPrice = checkPrice(soup)
                        # maybe another check or start with windows?
                        if newPrice <= priceTarget:
                            sendMail(newPrice, link)
                            print(title + " Price is good now!")
                        else:
                            print(title + " Price equal or greater")

                        item = Item(title, price, link, priceTarget)
                        items.append(item)

                        if len(title) > 20:
                            title = title[:20]

                        label1 = tk.Label(frame, text=title + ":  " + "Price " + str(
                            price) + " | " + "Price target " + str(priceTarget), bg="grey")
                        label1.pack()


def checkTitle(soup):
    title = None
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
    return title


def checkPrice(soup):
    price = None
    while price is None:
        price = soup.find(id="priceblock_ourprice")

        if price is not None:
            price = price.get_text().split()
            convertedPrice = float(price[0].replace(',', '.'))
            break
        else:
            price = soup.find(id="priceblock_saleprice")

            if price is not None:
                price = price.get_text().split()
                convertedPrice = float(price[0].replace(',', '.'))
                break
            else:
                priceArr = soup.find_all(
                    class_="a-size-medium a-color-price offer-price a-text-normal")
                for el in priceArr:
                    if el is not None:
                        price = el.get_text().split()
                        convertedPrice = float(price[0].replace(',', '.'))
                        break
                else:
                    priceArr = soup.find_all(
                        class_="a-size-medium a-color-price")
                    for el in priceArr:
                        if el is not None:
                            price = el.get_text().split()
                            convertedPrice = float(price[0].replace(',', '.'))
                            break
                    else:
                        priceArr = soup.find_all(
                            class_="a-size-base a-color-price a-color-price")
                        for el in priceArr:
                            if el is not None:
                                price = el.get_text().split()
                                convertedPrice = float(
                                    price[0].replace(',', '.'))
                                break
                        else:
                            priceArr = soup.find_all(
                                class_="a-size-base a-color-price offer-price a-text-normal")
                            for el in priceArr:
                                if el is not None:
                                    price = el.get_text().split()
                                    convertedPrice = float(
                                        price[0].replace(',', '.'))
                                    break
        break
    return convertedPrice


def addLinks():

    price = None
    convertedPrice = None
    title = None

    link = simpledialog.askstring("Insert a link", root)
    if link:
        priceTarget = simpledialog.askinteger("Insert the Target Price", root)
    # getStuff(link)
    page = requests.get(link, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    title = checkTitle(title, soup)
    convertedPrice = checkPrice(price, convertedPrice, soup)

    item = Item(title, convertedPrice, link, priceTarget)
    items.append(item)
    if len(title) > 20:
        title = title[:20]
    label = tk.Label(frame, text=title + ":  " + "Price " +
                     str(convertedPrice) + " | " + "Price target " + str(priceTarget), bg="grey")
    label.pack()


def sendMail(convPrice, URL):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    # from ehlo  command sent by an email server to identify itself
    #           when connecting to another email server to start the
    #           process of sending an email
    server.starttls()  # encrypt the connection
    server.ehlo()
    # in input? and check password
    server.login('albi.benni8@gmail.com', 'woskkonrhirvglqk')

    subject = 'Price fell down!' + str(convPrice)
    body = 'Check the amazon link: ' + URL

    msg = f"Subject: {subject} \n\n {body}"

    server.sendmail(
        'albi.benni8@gmail.com',
        'alby_b_@hotmail.it',
        msg
    )
    print('Email sent!')

    server.quit()


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
