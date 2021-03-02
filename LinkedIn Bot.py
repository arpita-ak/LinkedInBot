import os
import time
from time import sleep
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv

filename = input('Enter file name (.csv) to save the data: ')

chromedriver = "E:\Chrome Driver\chromedriver.exe"
driver = wb.Chrome(chromedriver)


def logging_in():
    # Go to Login URL
    driver.get("https://www.linkedin.com/login")

    username = input('Enter LinkedIn username/email-ID: ')
    password = input('Enter password: ')

    try:
        driver.find_element_by_id('username').send_keys(username)
    except:
        print("Trouble finding username element!")

    try:
        driver.find_element_by_id('password').send_keys(password)
    except:
        print("Trouble finding password element!")

    driver.find_element_by_xpath('/html/body/div/main/div[2]/form/div[3]/button').click()
    sleep(3)
    current = driver.current_url
    if current == "https://www.linkedin.com/feed/":
        print("\n Yayyy! Login Successful!")


def withdraw_requests():

    # function is incomplete as the button to "withdraw" is not added yet

    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
    all_profiles = driver.find_elements_by_class_name('invitation-card__details')
    #tryna get the whole thing here
    for link in all_profiles:
        #print(link)
        q = link.find_element_by_tag_name('time')
        from_linkedin = q.text
        from_linkedin = from_linkedin.split()
        #print(from_linkedin)

        given_time = input("Enter the time before which the requests sent should be withdrawn: ")
        #given_time = '3 minutes ago'

        given_time = given_time.split()
        #print(given_time)

        dict = {'second': 1, 'seconds': 1,
                'minute': 2, 'minutes': 2,
                'hour': 3, 'hours': 3,
                'day': 4, 'days': 4,
                'week': 5, 'weeks': 5,
                'month': 6, 'months': 6,
                'year': 7, 'years': 7}

        if dict[from_linkedin[1]] > dict[given_time[1]]:
            print('yes')
            # withdraw request
        elif dict[from_linkedin[1]] == dict[given_time[1]] and int(from_linkedin[0]) >= int(given_time[0]):
            print('yes')
            # withdraw request
        else:
            print('no')
            # do not withdraw request


def customized_message(name):
    message = "Greetings " + name + ", \nHave a good day!"
    return message


def save_the_scraped_data(name, bio, location, connections, profile_url, status):
    file_exists = os.path.isfile(filename)
    writer = csv.writer(open(filename, 'a'))
    if not file_exists:
        writer.writerow(['Profile URL', 'Name', 'Bio', 'College', 'Connection', 'status'])

    writer.writerow([profile_url.encode('utf-8'), name.encode('utf-8'), bio.encode('utf-8'), location.encode('utf-8'),
                     connections.encode('utf-8'), status.encode('utf-8'), time.strftime('%d-%m-%Y %H:%M:%S')])

    print(time.strftime('%d-%m-%Y %H:%M:%S'))
    print("Printing to .csv  successful!\n")


def visit_profile_and_send_customized_message(profile_url):
    driver.get(profile_url)
    sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Scraping of the Details
    try:
        name_div = soup.find('div', {'class': 'flex-1 mr5'})
        name_loc = name_div.find_all('ul')
        name = name_loc[0].find('li').get_text().strip()
        location = name_loc[1].find('li').get_text().strip()
        connections = name_loc[1].find('span').get_text().strip()
        if connections == 'Contact info':
            connections = 'Data Unavailable'
        bio = name_div.find('h2').get_text().strip()

        # printing the output to the terminal
        print('URL: ' + profile_url)
        print('Name: ' + name)
        print('Bio: ' + bio)
        print('Location: ' + location)
        print('connections: ' + connections)
        message = customized_message(name)
        status = " "

        try:
            driver.find_element_by_class_name('pv-s-profile-actions').click()
            driver.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[1]').click()
            sleep(3)
            driver.find_element_by_class_name('ember-text-area').send_keys(message)
            sleep(3)
            driver.find_element_by_class_name('ml1').click()
            print('"', message, '"')
            print("Connection request with message sent successfully!")
            status = "sent"
        except:
            print("Unable to send connection request!")
            status = "Not sent"
            pass
        save_the_scraped_data(name, bio, location, connections, profile_url, status)

    except:
        print("Trouble getting details")


def like_posts_from_feed():
    # Go to Feed URL
    driver.get("https://www.linkedin.com/feed/")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script(
        "(function(){try{for(i in document.getElementsByTagName('button'))"
        "{let el = document.getElementsByTagName('button')[i];"
        "if(el.innerHTML.includes('Like')){el.click();}}}catch(e){}})()")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def get_profiles_url_by_searching():
    page = int(input("Enter the number of pages that you want to keep the search for: "))

    driver.get("https://www.linkedin.com/feed/")
    term = input('Enter the term (In the order- name, company, designation, location) that you want to search for: ')

    profile_IDs = []

    next_url = term.replace(' ', '%20')
    base_url = 'https://www.linkedin.com/search/results/people/?keywords='

    url = base_url + next_url

    for page in range(1, page + 1):
        print('\nPage', page)
        url_page_wise = url + '&origin=GLOBAL_SEARCH_HEADER&page=' + str(page)
        driver.get(url_page_wise)
        sleep(5)
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        sleep(5)
        linkedin_urls = driver.find_elements_by_class_name('search-result__image-wrapper')
        print('%s connections found on page %s' % (len(linkedin_urls), page))
        for link in linkedin_urls:
            try:
                q = link.find_element_by_tag_name('a')
                r = q.get_property('href')
                print(r)
                profile_IDs.append(r)
            except Exception as e:
                print('ERROR: %s' % (e))
            sleep(5)

    return profile_IDs


def get_profile_url_from_linkedin_recommendation():
    driver.get('https://www.linkedin.com/mynetwork/')
    Profile_IDs = []
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(6)
    # wait for 6 seconds for the the page to load
    all_profiles = driver.find_elements_by_class_name('discover-entity-type-card__info-container')
    for link in all_profiles:
        q = link.find_element_by_tag_name('a')
        uid = q.get_attribute('href')
        # print(uid)
        Profile_IDs.append(uid)
    return Profile_IDs


logging_in()
filename = input('Enter the filename (.csv only): ')

while 1:
    print("\n     **** MENU ****\n"
          "Kindly choose from below options\n\n"
          "A. Like the posts in the feed\n"
          "B. Connect to LinkedIn Recommended People\n"
          "C. Search for a person\n"
          "D. Withdraw requests\n")

    ch = input("Enter your choice: ")

    if ch == "A":
        like_posts_from_feed()

    elif ch == "B":
        IDs = get_profile_url_from_linkedin_recommendation()
        serial_number = 1
        l = len(IDs)
        # prints the serial number of the current profile out of the total number of profiles in the current list only
        for ID in IDs:
            print(serial_number, '/', l)
            visit_profile_and_send_customized_message(ID)
            serial_number += 1

    elif ch == "C":
        IDs = get_profiles_url_by_searching()
        serial_number = 1
        # prints the serial number of the current profile out of the total number of profiles in the current list only
        l = len(IDs)
        for ID in IDs:
            print(serial_number, '/', l)
            visit_profile_and_send_customized_message(ID)
            serial_number += 1

    elif ch == "D":
        withdraw_requests()

    else:
        print('Invalid Choice. '
              'Try choosing one of the above choices :)\n')
