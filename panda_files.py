import pandas as pd


def exportToFile(data, filename_out):
    output = pd.DataFrame(data, columns=['Symbol','Expiration','Strike','Bid','Ask','Volume','Delta','Premium','Net Credit'])

    output.to_csv("output/" + filename_out,index=False)