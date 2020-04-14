

import simulator

sectors = ["Industrials", "Health Care", "Information Technology", "Consumer Discretionary", "Utilities", "Financials", "Materials", "Real Estate", "Consuemr Staples", "Energy", "Telecommunication Services"]
models = [0,1,2,3 ]

for sector in sectors:
    print(sector) > out.txt
    for model in models:
        print(model) > out.txt
        simulator 0 -s sector -y 2008-2018  > out.txt

