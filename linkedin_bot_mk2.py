# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 02:10:21 2018

@author: Ayush Lall
"""

# LinkedIn Bot pt. II
# Logic: Uses the link for a page set with specific filters and then
# gets all the jobs relevant for me within those specific filters.
# Then iterates through those list of jobs applying to each and every one
# of them.

# For now, applying to jobs only using LinkedIn's easy apply. No third-party
# job application websites covered.

# Flags for filters:
INTERNSHIP = True
ENTRY_LEVEL = True
ASSOCIATE = True
MID_SENIOR_LEVEL = False
DIRECTOR = False
EXECUTIVE = False
SEARCHTERM = 'Software Developer'

# Flags for program run:
SLEEP = 3
MAX_PAGE_LIMIT = 100


from selenium import webdriver
from bs4 import BeautifulSoup as bsp
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time

###############################################################################
#~~~~ Helper Functions ~~~~#
###############################################################################

# check_exists_by_xpath: Takes in two arguments, the current selenium webdriver 
# object driver, and the xpath of the element in consideration xpath. 
# Checks if that element exists on the driver's current page by using
# find_element_by_xpath and catching if it throws a NoSuchElement exception.
# Warning: May not always throw an exception, even if the element does not exist.
def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

# check_exists_via_bs4: Takes in one argument, the current webdriver driver.
# Uses the beautifulSoup library and a page's source to check if an element 
# exists on a page. 
# Note: beautifulSoup gets the entire source of the page not just what can be
# viewed in the selenium chromedriver. 
def check_exists_via_bs4(driver):
    soup = bsp(driver.page_source, 'lxml')
    alert = soup.find_all('span', {'role' : 'alert'})
    if (len(alert) == 0):
        return False
    return True

# check_exists_by_css: Takes in two arguments, the css selector path css, and
# the current selenium webdriver driver. Does basically the same thing as 
# check_exists_by_xpath but uses a css selector. The css selector function
# for selenium is usually faster and more accurate than the xpath function.
def check_exists_by_css(css, driver):
    try:
        driver.find_element_by_css_selector(css)
    except NoSuchElementException:
        return False
    return True

# create_flag_string: Takes in no arguments. Returns a string that can be added
# to the url to account for search filters. 
def create_flag_string():
    a = ''
    if INTERNSHIP: a += '%3D1'
    if ENTRY_LEVEL: 
        if a == '': a = '%3D2'
        else: a += '%252C2'
    if ASSOCIATE: 
        if a == '': a = '%3D3'
        else: a += '%252C3'
    if MID_SENIOR_LEVEL: 
        if a == '': a = '%3D4'
        else: a += '%252C4'
    if DIRECTOR: 
        if a == '': a = '%3D5'
        else: a += '%252C5'
    if EXECUTIVE:
        if a == '': a = '%3D6'
        else: a += '%252C6'
    return a

# create_filtered_link: Takes in one argument, a link, and adds the 
# flag string to it in order to add search filters
# 77 characters until filter
# 129 characters after filter
def create_filtered_link(link):
    return link[:77] + create_flag_string() + link[-135:]

# keywords: Takes in one argument, link. Adds the keywords to it.
# 110 terms from the start of search locator to the end
# 87 terms from the end of search locator to the end
def keywords(link):
    terms = SEARCHTERM.split()
    final = '%3D' + terms[0]
    for term in terms[1:]:
        final += '%2B' + term
    return link[:-110] + final + link[-87:]

# open_in_new_tab_action: Takes in two arguments, the job which is the element to
# be clicked and it's resulting link to be opened in a new tab, and the current
# selenium webdriver driver. Uses Selenium's ActionChains library to chain the 
# command ctrl + shift + left-click.
# Warning: Also not always accurate (at least what I found)
def open_in_new_tab_action(job, driver):
    ActionChains(driver) \
        .key_down(Keys.CONTROL) \
        .key_down(Keys.SHIFT) \
        .click(job) \
        .perform()

# open_in_new_tab: Takes in one argument only, the job which is the object on the
# page to be clicked and opened in a new tab. Sends the keys ctrl + return to the
# object, which mimicks opening a link on a new page. 
# Warning: For web objects that do not contain a direct href (usually 'a' html objects)
# this may return a 'cannot focus element' execption.
def open_in_new_tab(job):
    job.send_keys(Keys.CONTROL + Keys.RETURN)
    
# scroll_to_bottom: Takes in one required argument the current WebDriver driver. 
# Scrolls(manually) to the bottom of the page. Takes in another (bookkeeping)
# argument that controls how far (in multiples of 200px) we need to scroll to.
# Depth is normally set to 22 as 4200 px / 20 = 21 
def scroll_to_bottom(driver, depth = 22):
    k = 0
    while k < depth:
        driver.execute_script('window.scrollTo(0,' + str(200 * k) + ')')
        k += 1


###############################################################################
#~~~~ Worker Functions* ~~~~#
###############################################################################
# *basically functions that do the main work


# open_all_jobs_in_page: Takes in two arguments, a list of clickable objects jobs,
# and the current selenium webdriver driver. For each object job in jobs, this
# function opens it's link in a new tab on the selenium chromedriver. 
def open_all_jobs_in_page(jobs, driver):
    i = 0
    joblength = len(jobs)
    while (i < joblength):
        time.sleep(SLEEP)
        try:
            open_in_new_tab(jobs[i])
        except:
            print('cannot click on job')
            break
        driver.switch_to_window(driver.window_handles[0])
        i += 1

# apply: Takes in one argument, the current selenium webdriver driver. It iterates
# through all the new tabs open in chromedriver, except the first one.
# First, it checks if the LinkedIn jobs open have been applied to before, and
# moves on if so. Otherwise, it clicks on the big blue 'easy apply' button and 
# then clicks submit on the resulting page (which may be a pseudo pop-up on the
# same page or a new tab)
def apply(driver):
    for window in driver.window_handles[1:]:
        tabs_at_start = len(driver.window_handles)
        driver.switch_to_window(window)
        
        # These both check if the job has been applied to before    
        if (check_exists_via_bs4(driver)):
            driver.close()
            continue
        
        # Click on the easy apply button
        try:
            button = driver.find_element_by_css_selector('span[class="jobs-apply-button__text"]')
            button.click()
        except:
            print('cannot click easy apply button')
        
            
        # If the 'Easy Apply' button opens up a new tab
        # Then go to the newly open tab (top of the stack) and press submit
        if (len(driver.window_handles) > tabs_at_start):
            new_window = driver.window_handles[tabs_at_start]
            driver.switch_to_window(new_window)
            try:
                driver.execute_script('window.scrollTo(0, 500)')
                next_button = driver.find_element_by_css_selector('button[class="continue-btn"]')
                next_button.click()
                time.sleep(SLEEP)
                driver.close()
            except:
                print('cannot click submit - new page')
                
        # If it does not open a new tab, and the job hasn't been applied to yet
        # Then click the submit button on the faux popup
        else:
            next_button = driver.find_element_by_css_selector('button[type="submit"]')
            next_button.click()
            time.sleep(SLEEP)
            driver.close()


    
###############################################################################
#~~~~ Main Code ~~~~#
###############################################################################
            
#~~~~ Open and login to LinkedIn ~~~~#
            
# Get username, password from working directory
# Note: Users can either put username.txt and password.txt files in their 
# working directory or just plug them here.
file_objectu = open('username.txt', 'r')
username = file_objectu.read()
file_objectp = open('password.txt', 'r')
password = file_objectp.read()

# Note: Users need to have a chromedriver in their working directory

# Open a chromedriver, open link and wait
# LinkedIn links are nice - login redirects save job search filter information
# that was given in the original link
original_url = 'https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%26f_LF%3Df_AL%26keywords%3DDinosaur%2BRecruiter%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login'
fill_with_keywords = keywords(create_filtered_link(original_url))

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(chrome_options=options)
driver.get(fill_with_keywords)


# Feed in username and password at the page
username_elem = driver.find_element_by_id('username')
username_elem.send_keys(username)

password_elem = driver.find_element_by_id('password')
password_elem.send_keys(password)

# Click the big blue login button
login_elem = driver.find_element_by_css_selector('button[type="submit"]')
login_elem.click()

#~~~~ Switch to classic view ~~~~#

# For some reason this works
# This instead of clicking on the relevance drop down goes to the one we need
dropdown_elem = driver.find_element_by_css_selector('li-icon[class="jobs-search-dropdown__trigger-icon"]')
dropdown_elem.click()

# Here it's ok as there are only two drop down options available and this command
# picks the first which is classic view
classicview_elem = driver.find_element_by_css_selector('li[class="jobs-search-dropdown__option"]')
classicview_elem.click()

#~~~~ Start Applying! ~~~~#


# I'm putting a maximum upper limit of 100 pages of jobs 
# just in case, the user can change if needed
j = 0
while (j < MAX_PAGE_LIMIT):
    
    scroll_to_bottom(driver)
    
    # Finds all clickable jobs on the page
    jobs = driver.find_elements_by_css_selector('a[class="job-card-search__link-wrapper js-focusable-card ember-view"][tabindex="-1"]')

    # Opens all the job links in new tabs
    open_all_jobs_in_page(jobs, driver)
    
    # Clicks 'Easy Apply' for each of these jobs
    apply(driver)
    driver.switch_to_window(driver.window_handles[0])
    time.sleep(SLEEP)
    try:
        next_page = driver.find_element_by_css_selector('button[class="next"]')
    except NoSuchElementException:
        break

    next_page.click()
    #driver.get('https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3&f_LF=f_AL&keywords=Data%20Scientist&start=' + str(j*25))
    j += 1

print('Done')
# Miscellaneous Notes 
# mobile_login_href = 'https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%252C3%252C4%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login'

# Notes for selenium:
# Selenium does not store tabs in order of the way they appear on Chrome. It
# stores them in a LIFO stack - thus the oldest tab is tab[0] and the newest 
# one is tab[n-1] where the stack is of size n.
    
# Selenium gets page elements by what it can see! That is, all the elements
# on your screen are what it'll fetch and search through. However, it stores 
# elements that were seen previously but are now unavailable because we scrolled
# down. This is why I went for the manual scroll instead of just going to the
# bottom of the page instantly.
    
# LinkedIn's job search pages show 25 jobs at a time. To go to the next page
# the easiest way is to go to the link with the next 25. 
   
# Adding filters:
# https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%252C3%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login
    
    
# Only Internship:
# https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login    

# Internship + Entry Level
# https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login

# NOFILTER
# LinkedIn actually gives you a page with no jobs gg
# https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login

# 77 characters until filter
# 129 characters after filter
# https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D4%252C3%26f_LF%3Df_AL%26keywords%3DDataAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login
    
# Search terms
# 101 terms from the start of search locator to the end
# 87 terms from the end of search locator to the end
# %3D before the first word, %2B for each word after that