from bs4 import BeautifulSoup
import requests
from data import Database
from log import Log
import traceback

class HTMLReader(Database):
    url:str
    def __init__(self) -> None:
        print("HTMLReader created.")
        self.web = requests.Session()

    def InitLog(self, log:Log):
        self.Log = log
        return self

    def InitDatabase(self, database:Database):
        self.Database = database
        return self

    def GetContent(self):
        print("Content gettings.")
        self.soup = BeautifulSoup(self.request.content.decode("utf-8"), "html.parser")
        self.content = str(self.soup.contents)
        return self

    def GetText(self):
        self.content = self.soup.text.replace("I","ı").lower()
        return self
    
    def SetBaseUrl(self,url):
        print(f"Set did baseurl= {url}")
        self.baseUrl = url
        if self.baseUrl not in self.Database.content.keys():
            self.Database.content[self.baseUrl] ={}
            self.Database.Write()
        self.SetUrl(url)
        return self

    def SetUrl(self,url:str):
        if(url.startswith("/")):
            url = self.baseUrl+url[1:]
        print(f"Set did url= {url}")
        self.url = url
        return self

    def GetRequest(self):
        print(f"Requesting: {self.url} ")
        try:
            self.request = self.web.get(self.url)
        except requests.TooManyRedirects:
            self.url =""
            return self
        except Exception as e:
            traceback.print_exc()
            self.GetRequest()
        return self
    
    def GetAllUrl(self):
        print("Tüm urller bulunuyor.")
        if(not hasattr(self, "links")): 
            try:
                self.links = self.Database.content[self.baseUrl]["links"]            
            except:
                self.links = [self.baseUrl]
                self.Database.content[self.baseUrl]["links"] = self.links
        if(not hasattr(self, "vlinks")):
            try:
                self.vlinks = self.Database.content[self.baseUrl]["vlinks"]
            except:
                self.vlinks= []
                self.Database.content[self.baseUrl]["vlinks"] = self.vlinks
        for tag in self.soup.find_all():
            if tag.has_attr("href"):
                href = tag.get("href")
                if "?" in href and "?shopId" not in href:
                    href = href[:href.index("?")]      
                if"&" in href and "?shopId" in href:
                    href = href[:href.index("&")]
                if href not in self.links and href not in self.vlinks:
                    if(self.isValidUrl(href)):
                        self.links.append(href)
                        self.Database.content[self.baseUrl]["links"] = self.links
                        print(f"""Link eklendi[tag=href]: {href}""")
            if tag.has_attr("src"):
                src = tag.get("src")
                if "?" in src and "?shopId" not in src:
                    src = src[:src.index("?")]      
                if"&" in src and "?shopId" in src:
                    src = src[:src.index("&")]
                if src not in self.links and src not in self.vlinks:
                    if(self.isValidUrl(src)):
                        self.links.append(src)
                        self.Database.content[self.baseUrl]["links"] = self.links
                        print(f"""Link eklendi[tag=src]: {src}""")
            if tag.has_attr("data-prod-seller-url"):
                src = tag.get("data-prod-seller-url")
                if "?" in src and "?shopId" not in src:
                    src = src[:src.index("?")] 
                if"&" in src and "?shopId" in src:
                    src = src[:src.index("&")]
                if src not in self.links and src not in self.vlinks:
                    if(self.isValidUrl(src)):
                        self.links.append(src)
                        self.Database.content[self.baseUrl]["links"] = self.links
                        print(f"""Link eklendi[tag=data-prod-seller-url]: {src}""")

                
        self.Database.Write()
        return self

    def SetVisitedUrl(self, url):
        if(not hasattr(self, "vlinks")):
            try:
                self.vlinks = self.Database.content[self.baseUrl]["vlinks"]
            except:
                self.vlinks= []
                self.Database.content[self.baseUrl]["vlinks"] = self.vlinks
        
        if url not in self.vlinks:
            self.vlinks.append(url)
            self.Database.content[self.baseUrl]["vlinks"] = self.vlinks
        if url in self.links:
            del self.links[self.links.index(url)]
        print(f"Site ziyaret edildi: {url}")
        self.Database.Write()
        return self
    
    def isValidUrl(self, url:str):
        if (url.startswith("http")  ):
            if(url.startswith(self.baseUrl)):
                pass
            else:
                return False
        if(url.endswith("webp")):
            return False
        if(url.endswith(".svg")):
            return False
        if(url.endswith(".svg\n")):
            return False
        if(url.endswith(".jpg")):
            return False
        if(url.startswith("data:image")):
            return False
        if(url.startswith("/_ui/")):
            return False
        if(url.startswith("tel:")):
            return False
        if(url=="#"):
            return False
        if(url.startswith("//fonts.googleapis")):
            return False
        if(not url.startswith("/")):
            return False
        if(url=="/"):
            return False
        return True
        
