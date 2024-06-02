import threading
import datetime
from gnews import GNews
import signal
from dateutil.parser import parser


class YahooNewsCrawler():
    def __init__(self, search: str, site: str, start_date, end_date, index = 0):
        self.interface = GNews(language='en', country='US', start_date=start_date, end_date=end_date)
        self.search = search
        self.site = site
        self.thread_index = index
        
        self.found_news = []
        self.articles = []
        self.is_end = False    
        self.total_count = 0
        
        self.search_thread = threading.Thread(target=YahooNewsCrawler.__search_job, args=(self,))
        self.search_thread.start()
        
        print("Crawler created : [ start_date: ", start_date, ", end_date: ", end_date, ']')
        
    def __search_job(self):
        query = f'/search?q={self.search}+site:{self.site}'
        self.found_news = self.interface._get_news(query)
        self.total_count = len(self.found_news)
        
        for news_index in self.found_news:
            # print(f"[{self.thread_index}] Reading article.. [{news_index['title']}]")
            article = self.interface.get_full_article(news_index['url'])
            article.title = news_index['title']
            article.url = news_index['url']
            article.publish_date = parser().parse(news_index['published date'])
            self.articles.append(article)

        self.is_end = True
        
    def join(self, timeout: float):
        self.search_thread.join(timeout)
        return not self.search_thread.is_alive()
        

class MultiThreadedYahooNewsCrawler():
    def __init__(self, search: str, site: str, start_date: datetime.datetime, end_date: datetime.datetime):
        self.crawlers: list[YahooNewsCrawler] = []
        start = start_date
        end = end_date
        crawler_index = 0
        
        while start < end:
            checkpoint = start + datetime.timedelta(weeks=4)
            if (checkpoint > end):
                checkpoint = end
            
            crawler = YahooNewsCrawler(search, site, self.__convert_datetime_to_tuple(start), self.__convert_datetime_to_tuple(checkpoint), crawler_index)
            crawler_index = crawler_index + 1

            start = checkpoint + datetime.timedelta(days=1)
            self.crawlers.append(crawler)
            
        print(f"Total {len(self.crawlers)} crawler object has been created.")
        
    
    def __convert_tuple_to_datetime(self, dates):
        return datetime.datetime(year=dates[0], month=dates[1], day=dates[2])
    
    def __convert_datetime_to_tuple(self, datetime):
        return (datetime.year, datetime.month, datetime.day)
    
    def wait_for_end(self, timeout: float):
        if timeout < -1:
            timeout = 86400
        
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=timeout)
        
        for crawler in self.crawlers:
            if crawler.join((float)((end_time - datetime.datetime.now()).seconds)) == False:
                return False

        return True
    
    @property
    def articles(self):
        article_list = []
        for crawler in self.crawlers:
            article_list.extend(crawler.articles)
        return article_list
        
    def save_as_csv(self, filepath: str):
        self.wait_for_end(-1)
        
        lines = [ 'title,publish_date,full_text,url' ]
        for article in self.articles:
            try:
                text = (str(article.text).replace('\"', '\"\"'))
                lines.append(f'\"{str(article.title)}\",\"{str(article.publish_date)}\",\"{text}\",\"{str(article.url)}\"')
            except:
                text = ''
        
        filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(filepath, 'w') as file:
            file.write('\n'.join(lines))
            
    def get_progress(self):
        total = 0
        current = 0
        
        for crawler in self.crawlers:
            total = total + crawler.total_count
            current = current + len(crawler.articles)
            
        return (total, current)