import tkinter as TK
from tkinter import scrolledtext
import bs4
import requests
import re
import os
from shutil import copyfile
import datetime
from pathlib import Path

list_location = 'G:\\Manga\\ZZZ_mangaList_mangaPark.txt'
manga_directory = 'G:\\Manga\\'


# manga functions
def download_image(product_url, manga_dir):

    # so to act like a human
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

    # open url
    res = requests.get(product_url, headers=headers)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    # define location to save images
    data_folder = Path(manga_dir)

    # set name of image
    name = "global"
    for link in soup.select('#img-1'):
        lnk = link["src"]
        name = link["title"] + ".jpg"
        file_to_open = data_folder / name
        with open(file_to_open, "wb") as f:
            try:
                f.write(requests.get(lnk).content)
            except:
                lnk = "http:" + str(lnk)
                f.write(requests.get(lnk).content)
        print_test(str(file_to_open))

    # find next link
    base_link = "https://mangapark.net"
    next_link_find = str(soup.select('div.page > span > a')[1]).split('"')[1]
    next_link = base_link + next_link_find
    # print_test(next_link)

    # update chapter data
    ZZ_dir = manga_dir + "\\" + "ZZ_New.txt"
    update_chapter = open(ZZ_dir, "w")
    # update_chapter.write(chapter_num)
    update_chapter.close()

    return next_link


def download_manga(manga_dir, manga_link):
    next_exists = True
    # define where to store the manga
    manga_dir = manga_directory + manga_dir

    # define a place to store information on what newest chapter is
    ZZ_dir = manga_dir + "\\" + "ZZ_New.txt"
    # try to open data
    try:
        newest_chapter = open(ZZ_dir, "r")
        chapter_num = newest_chapter.read()  # do plus one in the future until bug is fixed
    # if can't open assume new
    except FileNotFoundError:
        newest_chapter = open(ZZ_dir, "w")
        newest_chapter.write("1")
        chapter_num = 1
    newest_chapter.close()

    try:
        print_test(manga_link + "/" + str(chapter_num))
        next_page = download_image(manga_link, manga_dir)
    except IndexError:
        print_test("Up to date, woot indexerror at 78")
        next_exists = False
    except requests.exceptions.HTTPError:
            try:
                next_page = download_image(manga_link + "/" + str(int(chapter_num) + 1), manga_dir)
            except IndexError:
                print_test("Up to date, woot")
                next_exists = False
    while(next_exists):
        try:
            after_page = download_image(next_page, manga_dir)
            next_page = download_image(after_page, manga_dir)
        except IndexError:
            print_test("Up to date, woot")
            next_exists = False


def update_manga():
    # read in manga list
    with open(list_location) as mangaListFile:
        manga_list = [tuple(map(str, i.split(','))) for i in mangaListFile]
    # reverse list since pop is at end
    manga_list.reverse()

    while len(manga_list) != 0:
        manga = manga_list.pop()
        manga_name = manga[0]
        manga_link = manga[1]
        print_test(manga_name)
        download_manga(manga_name, manga_link)


def print_manga_list():
    # read in manga list
    with open(list_location) as mangaListFile:
        manga_list = [tuple(map(str, i.split(','))) for i in mangaListFile]
    i = 0
    manga_list.sort()
    print_test("Current list of manga...")
    while i < len(manga_list):
        print_test(str(manga_list[i][0]))
        i = i + 1


# copies the manga list txt file and add date to it
def manga_list_backup():
    new_file_name = list_location[:-4] + "_backup" + str(datetime.date.today()) + ".txt"
    copyfile(list_location, new_file_name)
    print_test("Backup successful on " + str(datetime.date.today()))


# GUI
window = TK.Tk()
window.title("Manga Downloader")
window.geometry('800x300')

# scroll bar
txt = scrolledtext.ScrolledText(window,width=40, height=10)
txt.grid(column=0, row=0, columnspan=2)
# txt.insert(TK.INSERT, 'You text goes here')


# button test
def print_test(text):
    txt.insert(TK.INSERT, text + "\n")
    txt.update()
    txt.see(TK.END)


instruction_text = TK.Label(window, text="Manga Downloader to download manga from mangapark.com \n"
                                         "created by Andrew Chu")
instruction_text.grid(column=2, row=0, columnspan=3)

btn = TK.Button(window, text="Test", command=lambda: print_test('word'))
btn.grid(column=2, row=2)

btn2 = TK.Button(window, text="Update Manga", command=update_manga)
btn2.grid(column=2, row=1)

btn3 = TK.Button(window, text="Print List", command=print_manga_list)
btn3.grid(column=3, row=1)

btn4 = TK.Button(window, text="Backup List", command=manga_list_backup)
btn4.grid(column=4, row=1)

quitButton = TK.Button(window, text="Quit", command=window.quit)
quitButton.grid(column=4, row=2)

# labels for input box
label1 = TK.Label(window, text="New manga name :")
label1.grid(column=0, row=1)

label2 = TK.Label(window, text="First page link :")
label2.grid(column=0, row=2)

manga_name_entry = TK.Entry(window)
manga_link_entry = TK.Entry(window)

manga_name_entry.grid(column=1, row=1)
manga_link_entry.grid(column=1, row=2)


def retrieve_name_input():
    name_input = manga_name_entry.get()
    return name_input


def retrieve_link_input():
    link_input = manga_link_entry.get()
    return link_input


def add_manga():
    # read in manga list
    with open(list_location) as mangaListFile:
        manga_list = [tuple(map(str, i.split(','))) for i in mangaListFile]
    i = 0
    manga_list.append((str(retrieve_name_input()),str(retrieve_link_input()), "\n"))
    manga_list.sort()
    # print_test(str(manga_list))
    print_test("manga added is " + str(retrieve_name_input()))
    print_test("link added is " + str(retrieve_link_input()))

    manga_list_file = open(list_location, "w")
    while i < len(manga_list):
        manga_list_file.write(str(manga_list[i][0]) + ", " + str(manga_list[i][1]) + ", \n")
        i = i + 1
    manga_list_file.close()

    path = str(manga_directory) + str(retrieve_name_input())
    try:
        os.mkdir(path)
    except OSError:
        print_test("Creation of directory %s failed" % path)
    else:
        print_test("Successfully created the directory %s " % path)


btn5 = TK.Button(window, text="Add Manga", command=add_manga)
btn5.grid(column=5, row=1)


window.mainloop()
