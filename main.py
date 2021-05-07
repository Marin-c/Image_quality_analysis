from scipy import ndimage, stats
import cv2
import PIL.Image
import numpy as np
from skimage import measure
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
from tkfilebrowser import askopendirname
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from statistics import mean, stdev
import os
from os import listdir
from os.path import isfile, join
import pycontrast as pct
from SNRaverage import SNRaverage as snra


def signaltonoise(a, axis=0, ddof=0):
    """Returns the signal-to-noise ratio of a, here defined as the mean divided by the standard deviation"""
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

def modifiedLaplacian(img):
    ''''LAPM' algorithm (Nayar89)'''
    M = np.array([-1, 2, -1], dtype="float64")
    G = cv2.getGaussianKernel(ksize=3, sigma=-1)
    Lx = cv2.sepFilter2D(img, -1, kernelX=M, kernelY=G)
    Ly = cv2.sepFilter2D(src=img, ddepth=cv2.CV_64F, kernelX=G, kernelY=M)
    FM = np.abs(Lx) + np.abs(Ly)
    return cv2.mean(FM)[0]

def tenengrad(img, ksize=3):
    ''''TENG' algorithm (Krotkov86)'''
    Gx = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=ksize)
    Gy = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=ksize)
    FM = Gx**2 + Gy**2
    return cv2.mean(FM)[0]

def plot(STD,SNR,CQ,VLAP,MLAP,TLAP):
    """Function that plot the figure at the end to show the results of the program"""
    #num_bins=10
    #sigma_CQ=stdev(CQ)

    fig1 = plt.figure(constrained_layout=True)
    spec1 = gridspec.GridSpec(ncols=3, nrows=2, figure=fig1)

    f1_ax1 = fig1.add_subplot(spec1[0,0])
    f1_ax1.plot(STD)
    f1_ax1.axhline(mean(STD), color='k', linestyle='dashed', linewidth=1)
    f1_ax1.set_title("Standard deviation : %1.2f" % (mean(STD)))

    f1_ax2 = fig1.add_subplot(spec1[0,1])
    f1_ax2.plot(SNR)
    f1_ax2.axhline(mean(SNR), color='k', linestyle='dashed', linewidth=1)
    f1_ax2.set_title("Signal to noise ratio : %1.2f" % (mean(SNR)))

    f1_ax3 = fig1.add_subplot(spec1[0,2])
    f1_ax3.plot(CQ)
    f1_ax3.axhline(mean(CQ), color='k', linestyle='dashed', linewidth=1)
    f1_ax3.set_title("Contrast quality : %1.2f" % (mean(CQ)))

    f1_ax4 = fig1.add_subplot(spec1[1,0])
    f1_ax4.plot(VLAP)
    f1_ax4.axhline(mean(VLAP), color='k', linestyle='dashed', linewidth=1)
    f1_ax4.set_title("Laplacian variation : %1.2f (<100=blur)" % (mean(VLAP)))

    f1_ax5 = fig1.add_subplot(spec1[1,1])
    f1_ax5.plot(MLAP)
    f1_ax5.axhline(mean(MLAP), color='k', linestyle='dashed', linewidth=1)
    f1_ax5.set_title("Laplacian LAPM : %1.2f" % (mean(MLAP)))

    f1_ax6 = fig1.add_subplot(spec1[1,2])
    f1_ax6.plot(TLAP)
    f1_ax6.axhline(mean(TLAP), color='k', linestyle='dashed', linewidth=1)
    f1_ax6.set_title("Laplacian TENG : %1.2f" % (mean(TLAP)))
"""
    f1_ax4 = fig1.add_subplot(spec1[1,1])
    n, bins, patches = f1_ax4.hist(CQ, num_bins, density=True)
    y_CQ = ((1 / (np.sqrt(2 * np.pi) * sigma_CQ)) * np.exp(-0.5 * (1 / sigma_CQ * (bins - mean(CQ)))**2))
    f1_ax4.plot(bins, y_CQ, '--')
    f1_ax4.set_title("CQ : %1.2f" % (mean(CQ)))
"""
def find_path():
    """Function to display the asking directory frame"""
    root = Tk()
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


if __name__=="__main__":
    """
    Test all images of a folder and have in output :
    - Noise with Standard deviation and SNR

    """
    #Chemin de dossier de l'image
    path=""
    check='no'
    root = Tk()
    root.withdraw()
    messagebox.showinfo("Programme de notation d'image", "Vous allez sélectionner un dossier d'image (uniquement d'images) qui vont être évaluées.")
    root.destroy()
    while check == 'no':
        path = find_path()
        check = control_path()
    print(path)


    #Liste tous les fichiers du dossier
    fichiers = [f for f in listdir(path) if isfile(join(path, f))]
    #print(fichiers)

    #Listes pour toutes les mesures du dossier d'images
    STD=[]
    SNR=[]
    CQ=[]
    SIZ0=[]
    SIZ1=[]
    VLAP=[]
    MLAP=[]
    TLAP=[]

    it=0 #itérations
    for i in fichiers:
        """Boucle sur toutes les images du dossier"""

        path_of_image=join(path,i) #Chemin de l'image
        #print(path_of_image)
        #img = cv2.imread(path_of_image) #Ouverture de l'image
        im = PIL.Image.open(path_of_image)
        img = np.array(im)
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            pass
        #cv2.imshow(i,img)

        std=ndimage.standard_deviation(img) #mesure de la standard deviation
        STD.append(std)

        snr_in_column=signaltonoise(img) #mesure du SNR par colonne de l'image
        #snr=np.mean(snr_in_column) #SNR par image
        snr=snra(img)
        SNR.append(snr)

        siz0, siz1 = img.shape #mesure de la taille des images
        SIZ0.append(siz0)
        SIZ1.append(siz1)

        vlap=cv2.Laplacian(img, cv2.CV_64F).var() #measure of blur by variation of Laplacien of the image
        VLAP.append(vlap)

        mlap=modifiedLaplacian(img)
        MLAP.append(mlap)

        tlap=tenengrad(img)
        TLAP.append(tlap)

        cq=pct.contrast_quality(path_of_image) #mesure de la qualité du contraste basé sur l'entropie de l'image
        CQ.append(cq)

        it += 1
        


    #Print results
    print("***Outputs data***")
    print("Noise characteristic :")
    print("STD : ", "{:.2f}".format(mean(STD)))
    print("SNR : ", "{:.2f}".format(mean(SNR)))
    print("")
    print("Contrast characteristic :")
    print("CQ : ", "{:.2f}".format(mean(CQ)))
    print("")
    print("Sharpness characteristic :")
    print("VLAP : ", "{:.2f}".format(mean(VLAP)))
    print("MLAP : ", "{:.2f}".format(mean(MLAP)))
    print("TLAP : ", "{:.2f}".format(mean(TLAP)))
    print("")
    print("Resolution : ")
    print( "Mean : ", "{:.2f}".format(mean(SIZ0)), " x ", "{:.2f}".format(mean(SIZ1)))
    print("Max : ", "{:.2f}".format(max(SIZ0)), " x ", "{:.2f}".format(max(SIZ1)))
    print("Min : ", "{:.2f}".format(min(SIZ0)), " x ", "{:.2f}".format(min(SIZ1)))

    plot(STD,SNR,CQ,VLAP,MLAP,TLAP)
    plt.show()
    exit()
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()