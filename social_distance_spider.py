from bs4 import BeautifulSoup
import requests
import math
from urllib import parse as urlparse
from fieldnames import *

def parseMain(primaryLink):
  session = requests.Session()
  response = session.get(primaryLink)
  soup = BeautifulSoup(response.text, "lxml")
  pageButtons = soup.find_all("p", {"class": "pageButton"})
  lastPage = pageButtons[-1]
  lastUrl = lastPage.find("a").get("href")
  fullLastUrl = urlparse.urljoin(primaryLink, lastUrl)
  parseResult = urlparse.urlparse(fullLastUrl)
  qs = urlparse.parse_qs(parseResult.query)
  maxPages = int(qs["paging"][0])
  del qs["paging"]
  parseWithFormat = parseResult._replace(query=urlparse.urlencode(qs))
  unparsed = urlparse.urlunparse(parseWithFormat)
  unparsed += "&paging={}"
  return session, unparsed, maxPages

def parseLocations(session, link):
  '''
  This gets the locations on one page of the website.
  type link: str
  rtype: [{str}]
  '''
  response = session.get(link)
  data = response.text
  soup = BeautifulSoup(data, "lxml")

  # get container for location data
  locationsContainer = soup.find("div", {"class": "item-container"})

  locations = []

  for locationTag in locationsContainer.find_all("div", {"class": "normal-text list-item"}):
    # location will store location name, phone number, and address
    location = {}

    locationNameTags = locationTag.find_all("div", {"class": "text-left font-weight-bold"})

    # add location names to locations object
    # some locations have two lines
    location[NAME1] = locationNameTags[0].get_text(strip=True)
    if len(locationNameTags) > 1: location[NAME2] = locationNameTags[1].get_text(strip=True)
    
    locationDataTags = locationTag.find("div", {"class": "text-left main-info"})

    locationDataDivs = locationDataTags.findChild().find_all("div")
    #if len(locationDataDivs) > 0: location[PHONE] = locationDataDivs[0].get_text(strip=True)
    if len(locationDataDivs) > 1: location[ADDR1] = locationDataDivs[1].get_text(strip=True)
    if len(locationDataDivs) > 2: location[ADDR2] = locationDataDivs[2].get_text(strip=True)
    
    location[CATEGORY] = locationDataTags.find("div", {"class": "extra-info"}).get_text(strip=True)
    
    infoDataTags = locationTag.find("div", {"class": "info-column"})
    
    pdf = infoDataTags.find("a", {"class": "download-button"}).get("href").replace(' ', '%20')
    urlbase = 'https://saesdp.sccgov.org/sdpdocs/'
    assert pdf.startswith(urlbase) and '-' in pdf, pdf
    location[PDF] = pdf
    location['id'] = int(pdf[len(urlbase):pdf.find('-', len(urlbase))])
    
    extraInfoTags = infoDataTags.find("div", {"class": "extra-info"})
    
    location[REPLACEMENT] = extraInfoTags.find("div").get_text(strip=True)
    dateText = extraInfoTags.find("div", {"class": "text-right"}).get_text(strip=True)
    if dateText.startswith("Date of Protocol Submission: "):
      location[DATE] = dateText[len("Date of Protocol Submission: "):]
    else:
      location[DATE] = dateText

    # store location in list locations
    locations.append(location)
    
  return locations

