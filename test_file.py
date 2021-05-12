import cv2
import PIL.Image
import numpy as np
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
from tkfilebrowser import askopendirname, askopenfilenames
import os
from os import listdir
from os.path import isfile, join

def find_path():
    """Function to display the asking directory frame"""
    root = Tk()
    root = Toplevel()
    path = askopendirname(parent=root, initialdir='/', initialfile='tmp')
    root.destroy()
    return path

def control_path():
    """Function that display the control of the images directory"""
    root = Tk()
    root.withdraw()
    check = messagebox.askquestion("Find folder","Le chemin du dossier d'image est-il correct ? \n %s" %path, icon="question")
    root.destroy()
    return check

def find_files():
    """Function to display the asking files directory frame"""
    root = Tk()
    root = Toplevel()
    files = askopenfilenames(parent=root, initialdir='/', initialfile='tmp')
    root.destroy()
    return files

def control_files():
    """Function that display the control of the images selection"""
    root = Tk()
    root.withdraw()
    check = messagebox.askquestion("Find files","Les images sélectionnées sont-elles correctes ? \n %s" %files, icon="question")
    root.destroy()
    return check



if __name__=="__main__":
    """
    Test all images of a folder and have in output :
    - Noise with Standard deviation and SNR

    """
    #Chemin de dossier de l'image
    global path
    global files
    path=""
    files=""
    check='no'
    root = Tk()
    root.withdraw()
    messagebox.showinfo("Programme de notation d'image", "Vous allez sélectionner un dossier d'image (uniquement d'images) qui vont être évaluées.")
    root.destroy()
    while check == 'no':
        root = Tk()
        root.withdraw()
        selection = messagebox.askquestion("Which source","Si vous préférez sélectionner des images individuelles cliquez sur #oui, si vous voulez sélectionner un dossier d'images cliquez sur #non", icon="question")
        root.destroy()
        if selection == "yes":
            fichiers = find_files()
            print(fichiers)
            check = control_files()
        else:
            #Liste tous les fichiers du dossier
            path = find_path()
            fichiers = [f for f in listdir(path) if isfile(join(path, f))]
            print(fichiers)
            print(path)
            check=control_path()

    it=0 #itérations
    for i in fichiers:
        """Boucle sur toutes les images du dossier"""

        path_of_image=join(path,i) #Chemin de l'image
        #print(path_of_image)
        #img = cv2.imread(path_of_image) #Ouverture de l'image
        img = cv2.imread(path_of_image)
        #img = np.array(im)
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            pass
        cv2.imshow(i,img)
        input("wait")