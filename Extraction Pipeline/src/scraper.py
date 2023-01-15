from functools import partial
import logging.config
import requests
from inspect import getfile, currentframe
from .write import write_output
import csv
from os import cpu_count
import re
from pathlib import Path
from urllib.parse import urlsplit
from htmldate import find_date  # finding date of webpage
from multiprocessing import Pool
from urllib.request import Request, urlopen
from tqdm import tqdm
from datetime import date
from bs4 import BeautifulSoup
from os.path import exists
import concurrent

##################
# Logging Config
#################
filename = getfile(currentframe())
filename = Path(filename).stem
source = 'logs/' + filename
logging.config.fileConfig('logging.conf', defaults={'logfilename': source})
logger_default = logging.getLogger('pipeline')
logger_issue = logging.getLogger('root')

OLDEST_DATE = str(date(2022, 1, 1))

# EXCLUDED_TITLES = [
#     "EO On This Day"  # not relevant (EOS Start article)
# ]
#


def load_sources(source_loc):
    output_file = "output/output.json"

    if exists(output_file):
        return True

    with open(source_loc, 'r') as f:
        urls = f.read().splitlines()
    init_scrapper(urls)


def init_scrapper(scrape_urls):
    # Let scrape_urls be a file of CSV
    with Pool(cpu_count()) as p:
        list_of_links = p.map(gather_urls, scrape_urls)
    run_scraper(list_of_links)



def run_scraper(url_set):
    '''
    SITE.FRAGMENT: {
        TITLE: {
            URL: "URL_OF_ARTICLE",
            TEXT: "CONTENTS OF ARTICLE"

        }
    }

    '''

    output_folder = "output/"
    output_file = "output/output.json"
    json_data = {}

    for article_source in url_set:
        stop_parsing = False
        extraction_list = []
        article_lists = article_source[list(article_source.keys())[0]]
        base_site = list(article_source.keys())[0]
        json_data.update({base_site: {}})
        for article_lists_key in tqdm(article_lists):
            if  stop_parsing is False:
                with Pool(cpu_count()) as p:
                    extraction_list.append(
                        p.map(partial(process_urls, base_site), article_lists[article_lists_key]))
                    logger_default.info(f"successfully scraped page {article_lists_key} of {base_site}")

                    for element in extraction_list:
                        for item in element:
                            # print(item)
                            if item is False:
                                element.remove(item)
                                stop_parsing = True

        for extraction in extraction_list:
            for dict_obj in extraction:
                json_data[base_site].update(dict_obj)

        logger_default.info(f"{base_site} dictionary successfully build")

    write_output(output_file, output_folder, json_data)


def keep_scraping_article(parent_name, parent_name_order, continuing, allow_list):
    if not continuing:
        if parent_name == 'p':
            continuing = True
        if parent_name == 'footer':
            continuing = False
        return continuing
    else:
        if parent_name not in allow_list:
            continuing = False
        if parent_name and parent_name_order[-2] == 'a':  # if the current and last element were both links stop parsing
            continuing = False
    return continuing


def abbrev_checker(sentences):
    # evaluate string before last split if it contains a capital letter before it hits a space char then the sentence could contain an abbreviation which will need to be evaluated by the NLP
    abbrev_fix_sentences = []
    skip_index = None
    for i, sentence in enumerate(sentences):
        recent_grab = False
        words = sentence.split(" ")
        last_word_of_sentence = words[-1]
        # if the last sentence before the split contains a capital letter or number reattach to original sentence
        if bool(re.match(r'\w*[A-Z]\w*', last_word_of_sentence)) or last_word_of_sentence.isnumeric():
            # print(sentences[normalize])
            try:
                abbrev_fix_sentences.append(sentences[i] + " " + sentences[i + 1] + " ")
                skip_index = i + 1
                recent_grab = True
            except IndexError:
                # occurrence of error is due to capital letter being at the end of a paragraph thus giving out-of-bounds error
                pass
            except Exception as e:
                logger_issue.error(e)

        if i != skip_index and not recent_grab:
            abbrev_fix_sentences.append(sentence)
            # base_logger.Logger.logger()
    return abbrev_fix_sentences


def parse_text(elements):
    # Blocked elements that do not need to be parsed
    allow_list = [
        'p',
        'a',
        'h1',
        'h2',
        'h3',
        'h4',
    ]

    allowed_chars = [
        ' ',
        '.',
        '-',
        '—',
    ]
    sentences = []
    sentence = []
    all_text_parents = []
    scrape = False

    for text in elements:
        scrape = keep_scraping_article(text.parent.name, all_text_parents, scrape, allow_list)
        all_text_parents.extend(text.parent.name)
        if scrape:
            # filtering for NLP
            text = "".join(t for t in text if t.isalpha() or t in allowed_chars)
            if text.find(allowed_chars[2]) != -1:
                text = text.replace(allowed_chars[2], " ")
            if text.find(allowed_chars[3]) != -1:
                text = text.replace(allowed_chars[3], " ")

            sentence.extend(text + " ")

    article_text = " ".join("".join(sentence).split()).split('.')
    sentences.extend(sentence for sentence in map(str.strip, article_text) if
                     sentence != "" and sentence != " ")  # (sentence reconstruction/clean
    sentences = abbrev_checker(sentences)  # evaluate weather strings is an abbreviation

    return sentences


def extract_text_from_page(url_path):
    url_data = url_path
    soup = BeautifulSoup(url_data.text, 'html.parser')
    elements = soup.find_all(text=True)
    text_words = parse_text(elements)
    logger_default.info(f"Successfully extracted text from, {url_data}")
    return text_words


def gather_urls(scrape_url):
    headings = [
        'h1',
        'h2',
        'h3',
        'h4',
    ]
    excluded_tags = [
        'navbar',
        'footer',
        'ul',
        'script',
        'form',
        'nav',
        'footer'
    ]

    base_url = urlsplit(scrape_url, scheme='', allow_fragments=True).netloc
    URL_dict = {}
    URL_dict.update({base_url: {}})
    for i in tqdm(range(15, 20)):  # page numbers
        links = []
        req = Request(scrape_url.format(i))
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, "lxml")

        # Shrinks element size to increase overall speed of topic parse process
        for tag in excluded_tags:
            remove_bad_items = soup.find_all(tag)
            for item in remove_bad_items:
                item.extract()

        # Scrape heading tags for topic urls
        for header in headings:
            find_header = soup.find_all(header)
            if find_header is not None:
                for text in find_header:
                    for item in text.find_all('a'):
                        links.append(item.get('href'))

        URL_dict[base_url].update({i: links})
    logger_default.info(f"successfully parsed all links for the url, {base_url}")
    return URL_dict


def process_urls(original_url, url):
    # print("processing")
    bad_endings = [
        '.php',
        '.asp'
    ]
    parse_doc = True
    # for ending in url:
    if list(url)[0] == '/':
        call_url = f"http://{original_url}{url}"
    else:
        call_url = f"http://{original_url}/{url}"

    if list(url)[-1] == '/':
        call_url = call_url[:-1]

    if call_url.split('.')[-1] in bad_endings:
        return False
        # print(call_url)
    req = requests.get(call_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    title = soup.title.text
    try:
        postdate = find_date(call_url)
        if postdate <= OLDEST_DATE:
            parse_doc = False
            logger_issue.error(f"page {url}, was unable to be grabbed due to being out of date range")

    except ValueError as e:
        logger_issue.error(f"{e} occurred for the site {call_url}")
    if parse_doc:
        return {title: {"url_path": call_url, "text": extract_text_from_page(req)}}
    else:
        return parse_doc
