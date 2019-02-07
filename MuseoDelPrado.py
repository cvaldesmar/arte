import time
import logging
import glob
import os
import pathlib
import time
import json
import shutil
import wget
from threading import Thread

from selenium import webdriver as swd
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER


def saveJson(json_param, file):
    json.dump(json_param, open(file, 'w'), indent=1, sort_keys=True)


def loadJson(path):
    aux = json.load(open(path))
    return aux

class MuseoDelPrado:
    def __init__(self, headlessMode):
        self.initDriverParams(headlessMode)
        self.explore = {}

    def initDriverParams(self, headlessMode):
        LOGGER.setLevel(logging.CRITICAL)
        profile = swd.FirefoxProfile()
        profile.set_preference("browser.download.panel.shown", False)
        profile.set_preference("browser.helperApps.neverAsk.openFile", "image/jpeg")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/jpeg")
        profile.set_preference("browser.download.folderList", 2);
        # profile.set_preference("browser.download.dir", "C:\\Users\\Cesar\\GitHub\\arte\\fullBackup\\cache")

        profile.set_preference('permissions.default.image', 2)
        profile.set_preference("media.autoplay.enabled", False)
        profile.set_preference("media.webm.enabled", False)
        profile.set_preference('network.http.pipelining', True)
        profile.set_preference('network.http.max-connections', 96)
        profile.set_preference('network.http.max-connections-per-server', 32)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.disk.smart_size.enabled", False)
        profile.set_preference("browser.cache.disk.capacity", 0)
        profile.set_preference("dom.webnotifications.enabled", False)
        self.profile = profile
        if os.path.isfile(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"):
            self.binary = FirefoxBinary(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe")
        else:
            self.binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")
        options = Options()
        if (headlessMode):
            options.add_argument("--headless")
        self.options = options

    def createNewWebdriver(self, posx, posy, little):
        aux = swd.Firefox(firefox_options=self.options, firefox_binary=self.binary, firefox_profile=self.profile)
        aux.set_window_position(posx, posy)
        if little:
            aux.set_window_size(0, 0)
        return aux

    def museoDelPradoDataExport(self, filename):
        testDriver = self.createNewWebdriver(0, 0, little=0)
        urlBase = "https://www.museodelprado.es/coleccion/obras-de-arte?cidoc:p2_has_type@@@pm:objectTypeNode=http://museodelprado.es/items/objecttype_"
        # urlContinuations = ["20", "6", "155", "154", "3", "8", "25", "180", "31", "179"]
        urlContinuations = ["25"]
        for id in urlContinuations:
            test = []
            newUrl = urlBase+id
            testDriver.get(newUrl)
            li = testDriver.find_element_by_id("panListadoFiltros").find_element_by_tag_name("li")
            a = li.find_element_by_tag_name("a")
            testDriver.execute_script("var element = arguments[0];element.parentNode.removeChild(element);", a)
            tipoDeObra = li.get_attribute("innerText")
            numResults = int(testDriver.find_element_by_id("panNumResultados").find_element_by_tag_name("strong").get_attribute("innerText"))
            testDriver.execute_script("scroll(0, document.body.scrollHeight)")
            footer = testDriver.find_element_by_tag_name("footer")
            testDriver.execute_script("var element = arguments[0];element.parentNode.removeChild(element);", footer)

            while(len(test)<numResults):
                figures = testDriver.find_elements_by_tag_name("figure")
                figuresNum = len(figures)
                max = figuresNum if len(test) + len(figures) == numResults else figuresNum - 1
                print("MAX :" + str(max))
                for i in range(0,max):
                    figure = figures[i]
                    test.append(figure)
                    captions = figure.find_element_by_tag_name("figcaption")
                    enlace = captions.find_element_by_tag_name("a")
                    href = enlace.get_attribute("href")
                    paintingNamePreview = enlace.get_attribute("innerText")
                    soporteYaño = captions.find_element_by_class_name("soporte")
                    autor = captions.find_element_by_class_name("autor")
                    testDriver.execute_script("var element = arguments[0];element.parentNode.removeChild(element);", figure)

            # while(1):
            #     figures = testDriver.find_elements_by_class_name("presentacion-mosaico")
            #     print(len(figures))
            #     for figure in figures:
            #         testDriver.execute_script("var element = arguments[0];element.parentNode.removeChild(element);", figure)


            time.sleep(20)
            searchResults = testDriver.find_element_by_class_name("searchresults")
            results = searchResults.find_elements_by_class_name("link-teaser")
            for result in results:
                url = result.get_attribute("href")
                author = result.find_element_by_tag_name('p').get_attribute("innerHTML")
                paintingNameAndYear = " ".join(result.find_element_by_tag_name('h3').get_attribute("innerHTML").split())
                split = paintingNameAndYear.rsplit(',',1)
                paintingNamePreview = split[0]
                paintingYear = split[1].strip()
                if paintingYear:
                    try:
                        int(paintingYear)
                    except ValueError:
                        secondSplit = paintingYear.split(" - ")
                        if(len(secondSplit) != 2):
                            print("ERROR DE TAMAÑO DEL SPLIT: " + str(secondSplit))
                            print(paintingNameAndYear)
                        else:
                            try:
                                int(secondSplit[0])
                                int(secondSplit[1])
                            except ValueError:
                                print("FECHAS NO NUMERICAS: " + str(secondSplit))
                                print(paintingNameAndYear)

                paintingYear = "Sin fecha" if not paintingYear else paintingYear
                paintingNamePreview = "Sin título" if not paintingNamePreview else paintingNamePreview
                author = "Sin autor" if not author else author
                if not author in self.explore:
                    self.explore[author] = {}
                if not paintingYear in self.explore[author]:
                    self.explore[author][paintingYear] = []
                self.explore[author][paintingYear].append({"paintingNamePreview": paintingNamePreview, "url": url})
                saveJson(self.explore, filename)
        testDriver.quit()

    def museoDelPradoExploration(self, filename):
        testDriver = self.createNewWebdriver(0, 0, little=0)
        json = loadJson(filename)
        basePath = "fullBackup"
        saltos = 0
        for author in json:
            for year in json[author]:
                for painting in json[author][year]:
                    currentDir = os.path.join(basePath, author, year)
                    paintingNamePreview = painting["paintingNamePreview"]
                    url = painting["url"]
                    if not glob.glob(os.path.join(currentDir,paintingNamePreview) + ".*"):
                        testDriver.get(url)
                        try:
                            testDriver.find_element_by_class_name("icon-download")
                        except:
                            continue
                        testDriver.execute_script("document.getElementsByClassName('icon-download')[0].click()")
                        downloadURL = testDriver.find_element_by_class_name("rounded-right").get_attribute("href")
                        paintingName = testDriver.find_element_by_tag_name("strong").get_attribute("innerHTML").strip()
                        thread = Thread(target=self.downloadAndSave, args=(downloadURL, url, currentDir, paintingName))
                        thread.start()
                    else:
                        saltos += 1
                        print("SALTO " + str(saltos))

    def downloadAndSave(self, downloadURL, originalUrl, currentDir, paintingName):
        if not os.path.exists(currentDir):
            os.makedirs(currentDir)
        fileName = wget.download(downloadURL)
        cacheExtension = pathlib.Path(fileName).suffix
        cacheFilePath = fileName
        paintingName = paintingName.replace(":", ";").replace("?", "¿").replace('"', "'")
        finalFileName = paintingName + cacheExtension
        # if any(item in paintingName for item in ['|', '\\', '/', ':', '*', '?', "'", '<', '>']):
        #     print("ERROR DE NOMBRE " + paintingName + " - "+ originalUrl)
        finalFilePath = os.path.join(currentDir, finalFileName)

        # try:
        shutil.move(cacheFilePath, finalFilePath)
        # except:
        #     print("ERROR RENAMING " + cacheFilePath + " TO " + finalFilePath)

        # time.sleep(10)




