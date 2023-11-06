import json


class Json:

    def __init__(self, dataFilePath="data", expendFile="json") -> None:
        self.file = f"{dataFilePath}.{expendFile}"
        print(f"Josn dosyası: {self.file}")

    def Read(self):
        print("Json okutuluyor.")
        with open(self.file, "r",encoding="utf-8") as f:
            veri = json.load(f)
        self.content = veri
        return self

    def Write(self):
        print("Json yazdırılıyor.")
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.content, f,indent=4,ensure_ascii=False)
        return self

class Database(Json):
    def __init__(self):
        super().__init__()

    def  AddWeb(self):
        pass
