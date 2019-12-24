import mimetypes
import os
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests import get
import duckduckgo_images_api3.api as ddg3
from urllib3.exceptions import MaxRetryError


class DatasetCreator:
    _root_dir: str
    categories: set

    def __init__(self, root_dir: str, urls: iter, classes: iter):
        self._root_dir = root_dir
        self.categories = set()
        for url in urls:
            response = get(url)
            html_soup = BeautifulSoup(response.text, 'html.parser')
            categories = html_soup.find_all(self._match_class(classes))
            for category in categories:
                self.categories.add(category.text)

    def create_directories(self):
        self._make_dir(self._root_dir)
        for category in self.categories:
            self._make_dir(os.path.join(self._root_dir, category))

    def scrape_data(self, max_request_num=10, keywords=''):
        for category in self.categories:
            results = ddg3.search(keywords=category + ' ' + keywords,
                                  max_request_num=max_request_num)
            for i, result in enumerate(results.search_results):
                try:
                    response = requests.get(result.image,
                                            headers={'Accept': 'image/*'})
                    content_type = response.headers['content-type']
                    extension = mimetypes.guess_extension(content_type, strict=False)

                    # This was made to fix a bug where content type is not resolved properly
                    if extension == '.jpe':
                        extension = '.jpg'
                    if extension is None:
                        extension = os.path.splitext(urlparse(result.image).path)[1]

                    if response.status_code == 200:
                        with open(os.path.join(self._get_directory(category), str(i) + extension), 'wb') as f:
                            f.write(response.content)
                except Exception:
                    pass

    def _get_directory(self, category):
        return os.path.join(self._root_dir, category)

    @staticmethod
    def _match_class(target):
        def do_match(tag):
            classes = tag.get('class', [])
            return all(c in classes for c in target)

        return do_match

    @staticmethod
    def _make_dir(directory):
        try:
            os.mkdir(directory)
            print('Directory', directory, 'created')
        except FileExistsError:
            print('Directory', directory, 'already exists')
