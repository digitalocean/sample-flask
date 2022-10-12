class tiposDeArchivo():
    def __init__(self,file,file_extension):
        self.file = file
        self.file_extension = file_extension


    def leerExel(self):
        from pandas import pandas as pd
        if self.file_extension == 'xlsx':
            df = pd.read_excel(self.file, engine='openpyxl')
        elif self.file_extension == 'xls':
            df = pd.read_excel(self.file,header = 0)
        elif self.file_extension == 'csv':
            df = pd.read_csv(self.file,header = 0)
        else:
            raise Exception("File not supported")
        return df

lector = tiposDeArchivo('order.csv',"csv")
df = lector.leerExel()
for x in df:
    print(df.maxRow())
    