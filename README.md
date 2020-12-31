# Install Notes:

## First time:

- Install Python 3.9 

- [Click to Download](https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-amd64.zip); you should click checkbox, add python to path during installation. 

- Extract code in a folder and run install_pre.bat which will install libraries for the code.

- list.txt should contain the domains.

- info.json contains the information related to credentials for checking out.

## On every run:

- Run fetch_product_listing.bat to fetch products list from the domains (list.txt file). A data.txt file would be created containing the fetched products.
  
- After you have done these steps, you have to open run.bat to do checkout on the fetched products.

