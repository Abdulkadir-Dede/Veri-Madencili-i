from htmlReader import HTMLReader
from data import Database
from log import Log
import traceback
import re
import os

class Engine():
    def __init__(self) -> None:
        print("Engine is created.")
        self.Log = Log()
        self.Database = Database().Read()
        self.HTMLReader = HTMLReader().InitLog(self.Log).InitDatabase(self.Database)

    def ScanTeknosa(self):
        print("Scanning Teknosa.")
        baseurl = "https://www.teknosa.com/"
        self.HTMLReader.SetBaseUrl(baseurl).GetRequest().GetContent()
        self.HTMLReader.GetAllUrl().SetVisitedUrl(baseurl)
        index= len(self.Database.content[baseurl]["vlinks"])
        while ( 0 < len(self.Database.content[baseurl]["links"])):
            url = self.Database.content[baseurl]["links"][0]
            if(url in self.Database.content[baseurl]["vlinks"] or " " in url):
                self.HTMLReader.SetVisitedUrl(url)
                continue
            if os.path.exists("stop"):
                os.remove("stop")
                break
            self.HTMLReader.SetUrl(url).GetRequest()
            if(self.HTMLReader.url ==""):
                self.HTMLReader.SetVisitedUrl(url)
                continue
            self.HTMLReader.GetContent().GetAllUrl()
            min = len(self.Database.content[baseurl]["vlinks"])
            max = (len(self.Database.content[baseurl]["links"]) +len(self.Database.content[baseurl]["vlinks"]))
            print(min, "|", max , "| %", (min/max)*100 )
            isError=False
            try:
                datas= self.HTMLReader.soup.select_one("#pdp-main > div.pdp-block2.pdpGeneralWidth > div.pdp-details > div.addtocart-component > div > div > div").select_one("button")
                saticiID= datas["data-shopid"]
            except:
                isError = True
            if("-p-" in url and not isError):
                try:
                    datas= self.HTMLReader.soup.select_one("#pdp-main > div.pdp-block2.pdpGeneralWidth > div.pdp-details > div.addtocart-component > div > div > div").select_one("button")
                    saticiID= datas["data-shopid"]
                    satici=datas["data-shop-name"]
                    fiyat= datas["data-product-price"]
                    urunKodu= datas["data-product-id"]
                    urunadi= datas["data-product-name"]
                    category = datas["data-product-category"]
                    marka = datas["data-product-brand"]
                    rate = self.HTMLReader.soup.select_one("#pdp-rating > b").text

                    sourceLines = self.HTMLReader.content.split("\n")
                    i = sourceLines.index("    dataLayer.push({")
                    sourceLines= sourceLines[i:]
                    i = sourceLines.index("    });")
                    sourceLines = sourceLines[:i]

                    for item in sourceLines:
                        if item.startswith("                    'id': '"):
                            urunKodu = item[len("                    'id': '"):-2]
                        if item.startswith("                    'name': '"):
                            urunadi = item[len("                    'name': '"):-2]
                        if item.startswith("                    'brand': '"):
                            marka = item[len("                    'brand': '"):-2]
                        if item.startswith("                    'category': '"):
                            category = item[len("                    'category': '"):-2]
                        if item.startswith("                    'price': '"):
                            fiyat = item[len("                    'price': '"):-2]
                            try:
                                fiyat = re.search("(\d+).",fiyat).group(1)
                            except:
                                fiyat=" "
                
                    
                    if "shops"not  in  self.Database.content[baseurl]:
                        self.Database.content[baseurl]["shops"] = {}
                    
                    if saticiID not in  self.Database.content[baseurl]["shops"]:
                        self.Database.content[baseurl]["shops"][saticiID]={}
                        self.Database.content[baseurl]["shops"][saticiID]["Satıcı Adı"] = satici
                    
                    if category not in self.Database.content[baseurl]["shops"][saticiID]:
                        self.Database.content[baseurl]["shops"][saticiID][category] = {}

                    if marka not in self.Database.content[baseurl]["shops"][saticiID][category]:
                        self.Database.content[baseurl]["shops"][saticiID][category][marka] = {}

                    if urunKodu not in self.Database.content[baseurl]["shops"][saticiID][category][marka]:
                        self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu] = {}


                    print(f"urunKodu: {urunKodu}")
                    print(f"satici: {satici}")
                    print(f"category: {category}")
                    print(f"marka: {marka}")
                    print(f"urunadi: {urunadi}")
                    while(not fiyat or not rate or not urunadi):
                        print("Eksik bilgi! Bilgiler aranıyor...")
                        source = self.HTMLReader.content
                        fiyat = re.search(r"'price':\s*'(\d+\.\d+)",source).group(1)
                        fiyat = re.search(r"(\d+)", fiyat).group(1)
                    self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Adı"]=urunadi
                    print(f"fiyat: {fiyat}")
                    self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Fiyat"]=fiyat
                    print(f"rate: {rate}")
                    self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Puan"]=rate
                    self.Database.Write()
                    self.HTMLReader.SetVisitedUrl(url)
                except Exception as e:
                    print(traceback.print_exc())
                    break
            elif("-p-" in url and isError):
                sourceLines = self.HTMLReader.content.split("\n")
                try:
                    i  = sourceLines.index("    dataLayer.push({")
                except:
                    continue
                sourceLines= sourceLines[i:]
                i = sourceLines.index("    });")
                sourceLines = sourceLines[:i]

                for item in sourceLines:
                    if item.startswith("                    'id': '"):
                        urunKodu = item[len("                    'id': '"):-2]
                    if item.startswith("                    'name': '"):
                        urunadi = item[len("                    'name': '"):-2]
                    if item.startswith("                    'brand': '"):
                        marka = item[len("                    'brand': '"):-2]
                    if item.startswith("                    'category': '"):
                        category = item[len("                    'category': '"):-2]

                
                sourceLines = self.HTMLReader.content.split("\n")
                i = sourceLines.index("    window.insider_object = {")
                sourceLines= sourceLines[i:]
                i = sourceLines.index("    };")
                sourceLines = sourceLines[:i]

                for item in sourceLines:
                    if item.startswith('                    "shop_name": "'):
                        satici = item[len('                    "shop_name": "'):-2]
                    if item.startswith('                    "shop_id": "'):
                        saticiID = item[len('                    "shop_id": "'):-2]
                    if item=='                "unit_price":,':
                        fiyat = " "
                rate = " "
                print(f"urunKodu: {urunKodu}")
                print(f"satici: {satici}")
                print(f"category: {category}")
                print(f"marka: {marka}")
                print(f"urunadi: {urunadi}")
                while(not fiyat or not rate or not urunadi):
                    print("Eksik bilgi! Bilgiler aranıyor...")
                    source = self.HTMLReader.content
                    fiyat = re.search(r"'price':\s*'(\d+\.\d+)",source).group(1)
                    fiyat = re.search(r"(\d+)", fiyat).group(1)

                
                if "shops"not  in  self.Database.content[baseurl]:
                    self.Database.content[baseurl]["shops"] = {}
                
                if saticiID not in  self.Database.content[baseurl]["shops"]:
                    self.Database.content[baseurl]["shops"][saticiID]={}
                    self.Database.content[baseurl]["shops"][saticiID]["Satıcı Adı"] = satici
                
                if category not in self.Database.content[baseurl]["shops"][saticiID]:
                    self.Database.content[baseurl]["shops"][saticiID][category] = {}

                if marka not in self.Database.content[baseurl]["shops"][saticiID][category]:
                    self.Database.content[baseurl]["shops"][saticiID][category][marka] = {}

                if urunKodu not in self.Database.content[baseurl]["shops"][saticiID][category][marka]:
                    self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu] = {}

                self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Adı"]=urunadi
                print(f"fiyat: {fiyat}")
                self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Fiyat"]=fiyat
                print(f"rate: {rate}")
                self.Database.content[baseurl]["shops"][saticiID][category][marka][urunKodu]["Puan"]=rate
                self.HTMLReader.SetVisitedUrl(url)
            else:
                self.HTMLReader.SetVisitedUrl(url)

if __name__ =="__main__":
    engine = Engine()
    engine.ScanTeknosa()

    