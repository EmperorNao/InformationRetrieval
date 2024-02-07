import os
import json
from collections import deque
import requests
from bs4 import BeautifulSoup


class WikiParser:
    LINKS_CAP = 100_000
    BLACKLIST = ["Файл:", "Википедия:", "Категория:", "некорректный url"]

    def __init__(self,
                 file_dir,
                 max_words=1_000_000):
        self.max_words = max_words
        self.file_dir = file_dir

    @staticmethod
    def _filename(idx):
        return f"{idx}.txt"

    @staticmethod
    def _parse(content):
        soup = BeautifulSoup(content, 'html.parser')

        body = soup.find(id="bodyContent")
        title = soup.find('title')

        links = soup.find(id="bodyContent").find_all("a")
        wiki_links = list(
            map(lambda x: x["href"],
            filter(lambda x: x.get("href") and x["href"].find("/wiki/") != -1, links))
        )

        return {
            "title": title.text,
            "body": body.text,
            "links": wiki_links
        }

    def __call__(self,
                 start_link,
                 verbose=True):

        if not os.path.exists(self.file_dir):
            os.mkdir(self.file_dir)

        visited = set()

        number_of_words = 0
        kv = {}

        queue = deque()
        queue.append(start_link)

        while queue and number_of_words < self.max_words:
            url = queue.popleft()
            if url in visited:
                continue
            print(url)
            visited.add(url)
            try:
                response = requests.get(url=url)
            except: # noqa
                continue

            if response.status_code != 200:
                continue

            if verbose:
                print(f"{len(queue)} in queue, {len(kv)} number of docs, "
                      f"{number_of_words} / {self.max_words} status")

            parsed = WikiParser._parse(response.content)

            stop = False
            for blackpart in WikiParser.BLACKLIST:
                stop = stop or blackpart in parsed['title']
            if stop:
                continue

            body = parsed['body']
            words = list(filter(lambda x: x and x.isalpha(), map(lambda x: x.strip().lower(), body.strip().split())))
            number_of_words += len(words)

            for link in parsed["links"]:
                if link in visited or len(queue) >= WikiParser.LINKS_CAP:
                    continue
                queue.append("https://ru.wikipedia.org" + link)

            with open(os.path.join(self.file_dir, WikiParser._filename(len(kv))), "w") as fw:
                print(body, file=fw)
            kv[WikiParser._filename(len(kv))] = parsed['title']

        with open(os.path.join(self.file_dir, "index.json"), "w") as index:
            json.dump(kv, index)


if __name__ == "__main__":
    parser = WikiParser("./words")
    parser("https://ru.wikipedia.org/wiki/Веб-скрейпинг", verbose=True)
