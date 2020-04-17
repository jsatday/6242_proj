# 6242_proj

## Installing Dependancies
Python2
```
pip install kaggle
pip install scipy
pip install mplcursors
pip install ta
pip install matplotlib
pip install numpy
pip install scipy
```
Python3
```
pip3 install kaggle
pip3 install scipy
pip3 install mplcursors
pip3 install ta
pip3 install matplotlib
pip3 install numpy
pip3 install scipy
```

## Usage
To see the usage:
```python3 simulator.py -h```

### CHOOSE A MODEL:  
0 (macd_cross), 1 (macd_diff_smooth), 2 (macd_cross_slope), or 3 (rsi)  

### TICKER or SECTOR:  
-t: Specify a ticker to analyse  
-- OR --  
-s: Specify a sector to analyse  

### List of sectors:  
Industrials, HealthCare,InformationTechnology, ConsumerDiscretionary  
Utilities, Financials, Materials, RealEstate, ConsumerStaples  
Energy, TelecommunicationServices  

### OPTIONAL:  
-y: Specify a year or range of years to analyse over  
-e: Specify a file to export the overall results to  
-p: Plot the graph (Use the microscope on the graph to zoom into parts of the plot)  
-v: Show more verbose results (recommended when using -t)  

## Run Examples
The base program requires the use of a model (0-3), a ticker (-t) or sector (-s):  
```python3 simulator.py 0 -t msft -v```  
```python3 simulator.py 1 -s Energy -v```  

To test a year or a range of years:  
```python3 simulator.py 3 -t aapl -y 2012 -v```  
```python3 simulator.py 2 -t aapl -y 2006 2012 -v -p```  
```python3 simulator.py 0 -s Industrials -y 2006 2012```  

Get a range of results across a sector and store it in a file:  
```python3 simulator.py 0 1 2 3 -s HealthCare -y 2005 -e health_care_results```  

## API Documentation
### Kaggle Python API Documentation
https://github.com/Kaggle/kaggle-api  
https://technowhisp.com/kaggle-api-python-documentation/  

### Technical Analysis Python Library
https://github.com/bukosabino/ta/blob/master/README.md  

## Kaggle Database
https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs#aaba.us.txt  

### Maybe look at this later
https://www.kaggle.com/borismarjanovic/daily-and-intraday-stock-price-data  

## Stocks with Sectors
https://datahub.io/core/s-and-p-500-companies#resource-s-and-p-500-companies_zip  
