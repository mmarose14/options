import os
import pandas as pd

def importCSV(filename_in):
    data = pd.read_csv("symbols/" + filename_in)
    data.drop(data.tail(1).index,inplace=True) #Drop last row of extra text
    symbols = data['Symbol'].to_list()
    return symbols


def exportToFile(data, filename_out):
    output = pd.DataFrame(data, columns=['Symbol','Expiration','Strike','Bid','Ask','Volume','Delta','Premium','Net Credit','Timestamp'])

    output.to_csv("output/" + filename_out,index=False)

def exportToWeb(data, filename_out):
    output = pd.DataFrame(data, columns=['Symbol','Expiration','Strike','Bid','Ask','Volume','Delta','Premium','Net Credit','Timestamp'])

    output.to_csv("../mysite/static/csv/" + filename_out + ".csv", index=False)

def exportToJson(data, filename_out):
    output = pd.DataFrame(data, columns=['Symbol','Expiration','Strike','Bid','Ask','Volume','Delta','Premium','Net Credit','Timestamp'])
    print(f"Export: {filename_out}")
    output.to_json("../mysite/static/json/" + filename_out + ".json", orient="records")

    
