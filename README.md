# Read in chase bank statements

The Chase bank account app isn't the best for spending use and the app doesn't allow exporting to csv. This repo is to parse the bank staetments that are in pdf form into data that can be used to make plots.

The code requires a strings_to_filter.csv file which is just a list of references you want to exclude in the analysis. Usually this is just where I have transferred across my accounts rather than spending.

Go into the chase app, download the pdf statements and put them in the input data folder.