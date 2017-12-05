# Spider

## Setup
 
* install scrpay: `pip install Scrapy`
* clone repository
* go to the cloned folder: `cd vks`
* run command `scrapy crawl vk -o users.jl -a group=%group_url%`
  - where `%group_url%` a group url, without any quotes, like `-a group=https://domain.com/eminlive`

* quick check lines in file `wc -l users.jl`
* quick check for duplicate entires `awk -F "\"" '{print $4}' users.jl | sort | uniq -c | sort -bgr | less`

### Notes

* Tested on python 3.6.1
