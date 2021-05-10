import cv2
import PIL.Image
import numpy as np
from resizeimage import resizeimage
from skimage import measure
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
    messagebox.showinfo("image resize", "Vous allez sélectionner un dossier d'image (uniquement d'images) qui vont être modifiées.")
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
        file, ext = os.path.splitext(path_of_image)
        im = PIL.Image.open(path_of_image)
        img = np.array(im)
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            pass
        #cv2.imshow(i,img)

        print(img.shape)

        choice = str(input("Crop or upscale ?"))
        if choice == "crop":
            sf_in = img.shape[0]*img.shape[1]
            top = int(input("Shift from top ?"))
            left = int(input("Shift from left ?"))
            width = int(input("Width of the image ?"))
            height = int(input("Height of the image ?"))
            img2 = img[top:top+height, left:left+width]
            sf_out = img2.shape[0]*img2.shape[1]
            
            crp = sf_in/sf_out
            name = file + "_cropped%1.1f" %crp + ext
            print(name)   

        elif choice == "upscale":
            incr = float(input("Which increase size multipilicator do you want ?"))
            img2_size=(int(img.shape[1]*incr), int(img.shape[0]*incr))
            print(img2_size)
            #img2 = img1.resize(img2_size, resample=PIL.Image.NEAREST)
            img2 = cv2.resize(img, img2_size, interpolation=cv2.INTER_LANCZOS4)
            name = file + "_upscale%1.1f" %incr + ext
            print(name) 
        
        img_final = PIL.Image.fromarray(img2)
        img_final.save(name)
        #img2.show()
        it += 1
exit()