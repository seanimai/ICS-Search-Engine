import re
from collections import defaultdict

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
from duplicate_detection import isNearDuplicate
import requests

countd = dict()
countd[1] = 0

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def tokenize(text):
    result = []
    pattern = re.compile(r"[A-Za-z0-9]+")
    # Time complexity is O(n) for extracting tokens in a line using regex matching
    tokens = re.findall(pattern,text)
    for token in tokens:
        result.append(token.lower())
    return result

def computeWordFrequencies(tokens):
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return d

def get_absolute_url(current_url, resp,next_ref):

    # get the latest redirection url to determine absolute url in case of a relative path
    redirection_history = resp.raw_response.history
    if len(redirection_history) > 0:
        latest_redirection = redirection_history[-1]
        if latest_redirection.headers and "location" in latest_redirection.headers:
            current_url = latest_redirection.headers["location"]

    # add schema to next_ref, if it does not exist
    if next_ref[:4] == "www.":
        return urlparse(current_url).scheme + "://" + next_ref

    next_ref = next_ref.strip()
    next_ref_parse = urlparse(next_ref)

    # if next_ref is a relative path, concatenate the path to current url.
    if not next_ref_parse.netloc:
        next_ref = urljoin(current_url, next_ref)

    # adds www. to the next_ref if it is missing
    elif not next_ref_parse.netloc.startswith("www."):
        next_ref_parse = next_ref_parse._replace(netloc = "www." + next_ref_parse.netloc)
        next_ref = next_ref_parse.geturl()

    return next_ref.strip("/")

def extract_next_links(url, resp):

    next_links = list()
    # check response code. 2XX and 3XX are valid response codes.
    if not (resp.status >= 200 and resp.status <= 399):
        return next_links

    #crawl pages of content-type "text"
    headers = resp.raw_response.headers
    if "content-type" not in headers or headers["content-type"][:5] != "text/":
        return next_links

    # return if there is no content
    if str(resp.raw_response) == "None" or str(resp.raw_response) == "":
        return next_links

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    #TODO check for large page and avoid crawling, threshold to be decided based on testing
    try:
        file_header = requests.head(url)
        if int(file_header.headers['content-length']) > 1073741824:
            return next_links
    except:
        pass

    token_frequencies = computeWordFrequencies(tokenize(soup.get_text(" ", True)))
    # avoid crawling page with low information
    if len(token_frequencies) < 50:
        return next_links

    # simhash check (check if url is similar to others we have already scraped)
    if isNearDuplicate(token_frequencies):
        return next_links

    # clear txt file if we have restarted the crawler
    if countd[1] == 0:
        open('stored_urls.txt', 'w').close()

    # add url to file for later use
    file = open('stored_urls.txt', 'a')
    file.write(url)
    file.write('\n')
    file.close()

    # print the current count of urls added
    countd[1] = countd[1] + 1;
    print("current count : " + str(countd[1]));

    for next in soup.find_all("a", href=True):
        #get absolute url by resolving relative paths
        next_link = get_absolute_url(url , resp , next.get("href").strip())

        #defragmenting the url
        next_link = next_link.split("#")[0]

        next_links.append(next_link)

    return next_links

def is_valid_subdomain(parsed):
    # Check for allowed subdomains
    sub_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]
    netloc = str(parsed.netloc)
    for sub_domain in sub_domains:
        if netloc == sub_domain:
            return True
        elif netloc.endswith("." + sub_domain):
            return True

    # Special case for: today.uci.edu/department/information_computer_sciences/*
    path_start = "/department/information_computer_sciences/"
    if parsed.netloc == "today.uci.edu" and parsed.path[:len(path_start)] == path_start:
        return True

    return False


def is_valid(url):

    try:
        parsed = urlparse(url)

        if not is_valid_subdomain(parsed):
            return False

        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|lif|java|pov)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

if __name__ == '__main__':
    file = open('stored_urls.txt', 'r')
    for line in file:
        print(line)

    file.close()

