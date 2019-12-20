# Requirements
- Python 3.7
- Scrapy 1.6.0
- PyTorch 1.3.1
- AllenNLP 0.9.0
- BeautifulSoup 4.8.1
- PyMongo 3.9.0
- Flask
- tqdm
- MongoDB 4.2.2

# Run MongoDB
- Download MongoDB binary (https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1804-4.2.2.tgz) and extract it to a directory `<MONGODB_PATH>`.
- Create a directory `<DB_PATH>` for the database
- Run `<MONGODB_PATH>/bin/mongod -port 12180 -dbpath <DB_PATH>`

# Run Crawler
- Download this repo and extract it to `<PROJ_PATH>`
- Run `export PATHONPATH=<PROJ_PATH>`
- `cd` to `<PROJ_PATH>/src/crawl/news`
- Run `scrapy crawl bbc`

# Run Name Tagger
- Download our data from https://drive.google.com/file/d/1QdOSLNd5a98Cm4VxjbyJi2w6YI6aPE8z/view?usp=sharing and extract it to `<DATA_PATH>`
- Change line 11 in `src/ner/process_batch.py` to 'DATA_PATH = <DATA_PATH>'
- Run 'python src/ner/process_batch.py'

# Run Analyzer
- Import GeoNames entries: change line 33 in `src/crawl/database/geonames.py` to 'DATA_PATH = <DATA_PATH>' and run 'python src/crawl/database/geonames.py'
- Run 'python src/analyzer/analyze_batch.py'

# Run Demo
- Run `python app.py` and visit `<YOUR_IP_ADDRESS>:12181` or delete the host argument in line 43 and visit `127.0.0.1:12181`
