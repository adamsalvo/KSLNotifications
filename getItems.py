from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pprint import pprint

filename = "itemsList.txt"
yourEmail = ""
emailUserName = "YOUR USERNAME"
emailPassword = "YOUR EMAIL PASSWORD"


# Go to: https://www.ksl.com/auto/
# then enter in the search parameters you want. Then grab that url and put it here
links = "https://classifieds.ksl.com/search/?keyword=pixel&zip=&miles=25&priceFrom=%2480&priceTo=%24350&marketType%5B%5D=Sale&city=&state=&sort=0"

server = smtplib.SMTP( "smtp.gmail.com", 587 )
server.ehlo()
server.starttls()
server.login( emailUserName, emailPassword )

opts = Options()
opts.set_headless()
opts.add_argument("--enable-javascript")
assert opts.headless
browser = Chrome(options=opts)

jsonListings = []
toPrint = []
print("loading")
browser.get(links)
print("finished Loading")
listings = browser.find_elements_by_class_name('listing-item')


for list in listings:

	listArray = {}
	listArray["link"] = list.find_element_by_class_name("listing-item-link").get_attribute('href')
	listArray["title"] = list.find_element_by_class_name("item-info-title-link").text
	listArray["price"] = list.find_element_by_class_name("item-info-price").text
	listArray["img"] = list.find_element_by_tag_name('img').get_attribute('src')
	listArray["address"] = list.find_element_by_class_name('address').text
	jsonListings.append(listArray)


with open(filename, "r+") as itemsFile:
	if itemsFile.readline().rstrip() != "":
		itemsFile.seek(0, 0)
		item = json.loads(itemsFile.readline().rstrip())
	else:
		item = {}
		item["title"] = 0
	itemsFile.seek(0, 0)

	for listing in jsonListings:
		if item["title"] == listing["title"]:
			print("found")
			break
		else:
			print("not found")
			toPrint.append(listing)
	if len(toPrint) > 0:
		content = itemsFile.read()
		itemsFile.seek(0, 0)
		for listing in toPrint:
			print(json.dumps(listing, sort_keys=True), file=itemsFile)
		itemsFile.write(content)

	itemsFile.close()
# you can customize this to be whatever email you want
if len(toPrint) > 0:
	# Price - listingTitle 
	for listing in toPrint:
		

		title = "Title: " + str(listing["title"]) + "\n"
		price = "Price: " + str(listing["price"]) + "\n"
		address = "address: " + str(listing["address"]) + "\n"
		link = str(listing["link"]) + "\n"


		msg = MIMEMultipart('alternative')

		msg['Subject'] = str(listing["price"]) + " - " + str(listing["title"])
		msg['From'] = yourEmail
		msg['To'] = yourEmail


		text =  link + title + price + address
		htmlStart = "<html><head></head><body>"
		htmlEnd = "</body></html>"


		body = """
	<a href="{link}">
		<img src="{img}">
	</a>
	<h1>{title}</h1>
	<h2>Price: {price}</h2>
	<h2>Location: {address}</h2>
""".format(link=listing["link"], img=listing["img"], title=listing["title"], price=listing["price"], address=listing["address"])

		

		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(htmlStart + body + htmlEnd, 'html')

		msg.attach(part1)
		msg.attach(part2)
		pprint(msg.as_string())
		server.sendmail(yourEmail, yourEmail, msg.as_string())


browser.close()
browser.quit()