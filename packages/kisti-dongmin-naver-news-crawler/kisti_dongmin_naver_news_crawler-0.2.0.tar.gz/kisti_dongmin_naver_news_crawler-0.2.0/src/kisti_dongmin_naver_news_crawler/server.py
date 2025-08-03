from mcp.server.fastmcp import FastMCP

import requests
from bs4 import BeautifulSoup


# Initialize FastMCP server
mcp = FastMCP("weather")


@mcp.tool()
def get_crawling(keyword: str, numofpages: int) -> str:
    """
    Naver News collects the number of news article pages related to keywords requested by users and saves them in the naver-crawling.txt file.
    
    Args:
        keyword (str): Keywords requested by users for Naver News search.
        numofpages (int): Number of Naver news pages to collect as requested by the user.
    
    Returns:
        str: A message indicating the completion of the crawling process.
    """
    
    base_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + keyword + '&start='
    pages = numofpages * 10 + 1  

    file = open('D:\\naver-crawling.txt', 'w')
    
    for i in range(1, pages + 1, 10) :
        url = base_url + str(i)

        response = requests.get(url, headers={'User-Agent':'Moailla/5.0'})

        soup = BeautifulSoup(response.text, 'html.parser')

        headlines = soup.find_all('span', {'class' : 'sds-comps-text sds-comps-text-ellipsis sds-comps-text-ellipsis-1 sds-comps-text-type-headline1'})

        for headline in headlines:
            title = headline.text + '\n'
            file.write(title)

    file.close()
    
    return "Crawling completed and saved to naver-crawling.txt"


def main() -> None:
    # Initialize and run the server
    print("Starting Naver News Crawler server...")
    mcp.run(transport='stdio')


if __name__ == "__main__":
   main() 