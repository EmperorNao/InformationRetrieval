import os
from collections import deque
import requests
from bs4 import BeautifulSoup


class WikiParser:
    LINKS_CAP = 100_000

    def __init__(self,
                 file_dir,
                 words_buffer_size=10_000,
                 max_words=1_000_000):
        self.words_buffer_size = words_buffer_size
        self.max_words = max_words
        self.file_dir = file_dir

    @staticmethod
    def _filename(number_of_blocks):
        return f"{number_of_blocks}.txt"

    @staticmethod
    def _load_to_file(words, max_size, file_path):
        s = "\n".join(words[:max_size])
        with open(file_path, "w") as fp:
            print(s, file=fp)
        return words[max_size:]

    @staticmethod
    def _parse(content):
        soup = BeautifulSoup(content, 'html.parser')

        body = soup.find(id="bodyContent")

        links = soup.find(id="bodyContent").find_all("a")
        wiki_links = list(
            map(lambda x: x["href"],
            filter(lambda x: x.get("href") and x["href"].find("/wiki/") != -1, links))
        )
        words = list(filter(lambda x: x and x.isalpha(), map(lambda x: x.strip().lower(), body.text.strip().split())))
        return {
            "words": words,
            "links": wiki_links
        }

    def __call__(self,
                 start_link,
                 verbose=True):

        if not os.path.exists(self.file_dir):
            os.mkdir(self.file_dir)

        visited = set()

        number_of_words = 0
        number_of_blocks = 0
        words = []

        queue = deque()
        queue.append(start_link)
        visited.add(start_link)

        while queue and number_of_words < self.max_words:
            url = queue.popleft()
            visited.add(url)
            try:
                response = requests.get(url=url)
            except: # noqa
                continue

            if response.status_code != 200:
                continue

            if verbose:
                print(f"{len(queue)} in queue, {number_of_blocks} prepared blocks, "
                      f"{number_of_words} / {self.max_words} status")

            parsed = WikiParser._parse(response.content)
            words.extend(parsed["words"])
            number_of_words += len(parsed["words"])

            for link in parsed["links"]:
                if link in visited or len(queue) >= WikiParser.LINKS_CAP:
                    continue
                queue.append("https://ru.wikipedia.org" + link)

            while len(words) >= self.words_buffer_size:
                words = WikiParser._load_to_file(
                    words,
                    self.words_buffer_size,
                    os.path.join(self.file_dir, WikiParser._filename(number_of_blocks))
                )
                number_of_blocks += 1


if __name__ == "__main__":
    parser = WikiParser("./words")
    parser("https://ru.wikipedia.org/wiki/Веб-скрейпинг", verbose=True)
