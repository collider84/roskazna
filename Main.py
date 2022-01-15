#coding: utf-8

import os
import bs4  
import requests
from enum import Enum


# Work mode enum
class Mode(Enum):
    ROOT = 1
    PROM = 2
    CRLS = 3


# Roskazna URL
URL = 'http://crl.roskazna.ru/crl/'
HOME = os.getenv('HOME')

# Folder to save the certificates
ROOT_FOLDER = HOME + '/roots/'
PROMEZ_FOLDER = HOME + '/promez/'
CRLS_FOLDER = HOME + '/crls/'


def certifcate_downloader(folder, links):
    """Download certificates list to particular folder"""
    
    # If folder does not exist - create it
    if os.path.exists(folder) == False:
        os.mkdir(folder)

    # Download certificates
    for link in links:
        print("Save certificate - %s" % link)
        ufr = requests.get(link)
        s = link.split('//')[1]
        fname = folder + s.split('/')[-1]
        fout = open(fname,'wb')
        fout.write(ufr.content)
        fout.close()



def perform_command(folder, mode):
    """Perform command on every file in the folder"""
    
    # ROOT  -> sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mroot -file '/home/ivb/roots/Корневой сертификат ГУЦ ГОСТ 2012.crt'
    # PROM  -> sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mca -file '/home/ivb/roots/Корневой сертификат ГУЦ ГОСТ 2012.crt'
    # CRLS  -> sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mca -file '/home/ivb/crls/ucfk.crl' -crl

    # Gel list of files in the folder
    files = os.listdir(folder)
    
    # Do commands  with files
    for file in files: 
        if mode==Mode.ROOT:
            cmd = "sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mroot -file '%s'" % (ROOT_FOLDER + file)
        elif mode==Mode.PROM:
            cmd = "sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mca -file '%s'" % (PROMEZ_FOLDER + file)
        else:
            cmd = "sudo /opt/cprocsp/bin/amd64/certmgr  -inst -store mca -file '%s' -crl" % (CRLS_FOLDER + file)  

        # Make command
        print("Execute cmd - %s" % cmd)
        os.system(cmd)




if __name__=='__main__':
    # Get web page content
    page = requests.get(URL)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    listAnchors = soup.findAll('a')

    # Get URLs from page
    rootURL = [ URL + name["href"] if name["href"].find('http') == -1 else name["href"] for name in listAnchors if name.text.find('Корневой') != -1 ]
    promURL = [ URL + name["href"] if name["href"].find('http') == -1 else name["href"] for name in listAnchors if name.text.find('Подчиненный') != -1]
    crlURL  = [ URL + name["href"] if name["href"].find('http') == -1 else name["href"] for name in listAnchors if name.text.find('.crl') != -1 ]

    # Download certificates by URLs
    certifcate_downloader(ROOT_FOLDER, rootURL)
    certifcate_downloader(PROMEZ_FOLDER, promURL)
    certifcate_downloader(CRLS_FOLDER, crlURL)    

    # Perform commands
    perform_command(ROOT_FOLDER, Mode.ROOT)
    perform_command(PROMEZ_FOLDER, Mode.PROM)
    perform_command(CRLS_FOLDER, Mode.CRLS)
    