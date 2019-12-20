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
- 
