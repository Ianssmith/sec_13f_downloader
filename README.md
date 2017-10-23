## 13F filing Downloader:
### This downloads 13f filings from mutual funds from the SEC.gov search engine based on CIK or ticker.
- It save the xml formatted files and also reformats them into tsv files. 
- The files are created with the date the 13f was filed followed by the requested CIK ticket of the fund.
![alt text](13f_example.png "The website limits requests to 100 filings so the program asks the user to stipulate how many hundreds of files back they would like to search for 13f filings (ie. 1 = 100; 2 = 200; etc)")
