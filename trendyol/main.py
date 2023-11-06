from htmlReader import HTMLReader
from data import Database
from log import Log
import json
import traceback
import re
import os
import time

class Engine():
    def __init__(self) -> None:
        print("Engine is created.")
        self.Log = Log()
        self.Database = Database().Read()
        self.HTMLReader = HTMLReader().InitLog(self.Log).InitDatabase(self.Database)

    def ScanTrendyol(self):
        print("Scanning Trendyol.")
        baseurl = "https://www.trendyol.com/"
        self.HTMLReader.SetBaseUrl(baseurl).GetRequest().GetContent()
        self.HTMLReader.GetAllUrl().SetVisitedUrl(baseurl)
        while ( 0 < len(self.Database.content[baseurl]["links"])):
            url = self.Database.content[baseurl]["links"][0]
            code = self.Mining(baseurl,url)
            if (code==0):
                break
            elif(code==1):
                continue
            
    def Mining(self, baseurl, url):
            if(url in self.Database.content[baseurl]["vlinks"]):
                self.HTMLReader.SetVisitedUrl(url)
                return 1
            if(self.HTMLReader.isSubPageProduct(url)):
                self.Database.content[baseurl]["links"].remove(url)
                return 1
            if os.path.exists("stop"):
                os.remove("stop")
                return 0
            self.HTMLReader.SetUrl(url).GetRequest().GetContent().GetAllUrl()
            min = len(self.Database.content[baseurl]["vlinks"])
            max = (len(self.Database.content[baseurl]["links"]) +len(self.Database.content[baseurl]["vlinks"]))
            print(min, "|", max , "| %", (min/max)*100 )
            if("-p-" in url):
                scripts = self.HTMLReader.WriteContent().soup.find_all("script",type="application/javascript")
                
                for script in scripts:
                    content = script.contents[0]
                    try:
                        content = content[len("window.__PRODUCT_DETAIL_APP_INITIAL_STATE__="):content.index(";window.TYPageName")]
                        data = json.loads(content)
                    except:
                        print("HATA")
                        traceback.print_exc()
                        self.HTMLReader.SetVisitedUrl(url)
                        return 1
                    break
                

                saticiID = data["product"]["merchant"]["id"]
                saticiName = data["product"]["merchant"]["name"]
                categoryID = data["product"]["category"]["id"]
                categoryName = data["product"]["category"]["name"]
                brandID = data["product"]["brand"]["id"]
                brandName = data["product"]["brand"]["name"]
                productID = data["product"]["id"]
                productName = data["product"]["name"]
                productContent = data["product"]
                print("Satici ID:", saticiID)
                print("Satici Name:", saticiName)
                print("Category ID:", categoryID)
                print("Category Name:", categoryName)
                print("Brand ID:", brandID)
                print("Brand Name:", brandName)
                print("Product ID:", productID)
                print("Product Name:", productName)
                print("Product Content:", productContent)

                try:
                    saticiyaSor = self.HTMLReader.soup.select_one("#product-detail-app > div > article.question-wrapper > div > div.question-detail > div.more-questions-wrapper > a").get("href")
                except:
                    saticiyaSor=False
                    traceback.print_exc()
                try:
                    yorumlar = self.HTMLReader.soup.select_one("#product-detail-app > div > article.pr-rnr-w > div > div.pr-rnr-com-w > a").get("href")
                except:
                    yorumlar=False
                    traceback.print_exc()
                if "shops"not  in  self.Database.content[baseurl].keys():
                        self.Database.content[baseurl]["shops"] = {}
                    
                if saticiID not in  self.Database.content[baseurl]["shops"].keys():
                    self.Database.content[baseurl]["shops"][saticiID]={}
                    self.Database.content[baseurl]["shops"][saticiID]["name"]= saticiName
                
                if categoryID not in self.Database.content[baseurl]["shops"][saticiID].keys():
                    self.Database.content[baseurl]["shops"][saticiID][categoryID] = {}
                    self.Database.content[baseurl]["shops"][saticiID][categoryID]["name"] = categoryName

                if brandID not in self.Database.content[baseurl]["shops"][saticiID][categoryID].keys():
                    self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID] = {}
                    self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID]["name"] = brandName

                if productID not in self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID].keys():
                    self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID] = {}
                    self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID]["name"] = productName
                    self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID]["product"] = productContent
                    if(saticiyaSor):
                        self.HTMLReader.SetUrl(saticiyaSor).GetRequest().GetContent()
                        questions = self.HTMLReader.soup.select_one("#questions-and-answers-app > div > div > div > div > div > div.questions-wrapper > div.pr-qna-v2 > div > div")
                        questions_answers = []
                        try:
                            for item in questions.find_all('div', class_='qna-item'):
                            
                                question = item.find('h4').text
                                
                                user_info = item.find('div', class_='user-summary')
                                user_name = user_info.find('span').text
                                date = user_info.find_all('span')[1].text
                                
                                answer_info = item.find('div', class_='seller-info')
                                answered_date = answer_info.find('span', class_='answered-date').text
                                answer = item.find('h5').text

                                qa = {
                                    'question': question,
                                    'user_name': user_name,
                                    'date': date,
                                    'answered_date': answered_date, 
                                    'answer': answer
                                }
                                
                                questions_answers.append(qa)
                            self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID]["questions"] = questions_answers
                        except:
                            self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID]["questions"] = "None"
                            traceback.print_exc()
                        self.HTMLReader.SetVisitedUrl(saticiyaSor)
                    else:
                        self.Database.content[baseurl]["shops"][saticiID][categoryID][brandID][productID]["questions"] = "None"

    
                
                if "items" not  in  self.Database.content[baseurl].keys():
                    self.Database.content[baseurl]["items"] = {}
                
                if categoryID not in self.Database.content[baseurl]["items"].keys():
                    self.Database.content[baseurl]["items"][categoryID] = {}
                    self.Database.content[baseurl]["items"][categoryID]["name"] = categoryName

                if brandID not in self.Database.content[baseurl]["items"][categoryID].keys():
                    self.Database.content[baseurl]["items"][categoryID][brandID] = {}
                    self.Database.content[baseurl]["items"][categoryID][brandID]["name"] = brandName

                if productID not in self.Database.content[baseurl]["items"][categoryID][brandID].keys():
                    self.Database.content[baseurl]["items"][categoryID][brandID][productID] = {}
                    self.Database.content[baseurl]["items"][categoryID][brandID][productID]["name"] = productName

                    try:
                        self.HTMLReader.SetUrl(yorumlar).GetRequest()
                        timeOut=0
                        oldHeight=self.HTMLReader.GetScrollHeight()
                        while(timeOut < 40):
                            timeStart = time.time()
                            if(oldHeight!=self.HTMLReader.GetScrollHeight()):
                                ## Yeni yorum eklendi
                                timeOut=0
                                oldHeight=self.HTMLReader.GetScrollHeight()
                                print("Yeni yorumlar bulunuyor.")
                            else:
                                ## Yeni yorum bulunmaya çalışıyor.
                                time.sleep(0.5)
                                self.HTMLReader.SetScrollHeight(oldHeight-2000)
                            timeEnd = time.time()
                            timeOut+=timeEnd-timeStart

                        print("30 saniye yorum aşımı yaşandı. Yorumlar okunuyor.")

                        comments = []
                        yorumlarlist=self.HTMLReader.GetContent().soup.select_one("#rating-and-review-app > div > div > div > div:nth-child(3) > div > div > div.reviews-content")
                        for comment in yorumlarlist.find_all('div', class_='comment'):

                            rating = len(comment.find('div', class_='full').find_all('div'))
                            
                            name = comment.find('div', class_='comment-info-item').text
                            date = comment.find_all('div', class_='comment-info-item')[1].text
                            
                            text = comment.find('div', class_='comment-text').text    

                            seller = comment.find('span', class_='seller-name-info').text
                            
                            c = {
                                'rating': rating,
                                'name': name,
                                'date': date,  
                                'comment': text,
                                'seller': seller
                            }
                            
                            comments.append(c)

                        self.Database.content[baseurl]["items"][categoryID][brandID][productID]["comments"] = comments
                    except:
                        traceback.print_exc()
                        self.Database.content[baseurl]["items"][categoryID][brandID][productID]["comments"] = "None"

                    self.HTMLReader.SetVisitedUrl(yorumlar)
                
                self.HTMLReader.SetVisitedUrl(url)
            else:
                self.HTMLReader.SetVisitedUrl(url)

if __name__ =="__main__":
    engine = Engine()
    engine.ScanTrendyol()

    