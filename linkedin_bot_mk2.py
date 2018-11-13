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
        time.sleep(2)
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
                time.sleep(2)
                driver.close()
            except:
                print('cannot click submit - new page')
                
        # If it does not open a new tab, and the job hasn't been applied to yet
        # Then click the submit button on the faux popup
        else:
            next_button = driver.find_element_by_css_selector('button[type="submit"]')
            next_button.click()
            time.sleep(2)
            driver.close()


    
###############################################################################
#~~~~ Main Code ~~~~#
###############################################################################
            
#~~~~ Open and login to LinkedIn ~~~~#
            
# Get username, password from working directory
file_objectu = open('username.txt', 'r')
username = file_objectu.read()
file_objectp = open('password.txt', 'r')
password = file_objectp.read()

# Note: Users need to have a chromedriver in their working directory

# Open a chromedriver, open link and wait
# LinkedIn links are nice - login redirects save job search filter information
# that was given in the original link
mobile_login_href = 'https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%252C3%252C4%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login'
login_url = 'https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%252C3%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login'
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(chrome_options=options)
driver.get(login_url)


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

# Scrolls down by 400 px (?)
driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

driver.get('https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3&f_LF=f_AL&keywords=Data%20Scientist&start=25')


# TODO: Need to find a way to really iterate through jobs

i = 0
j = 0
# Right now I've put basically arbitrary loop size just so it works
# I should fix that
# TODO: Find a way to show that the list of jobs has ended 
# and really find a way to iterate
while (j < 10):
    while (i < 5):
        # driver.execute_script('window.scrollTo(0,' + str(400 * (i + 1)) + ')')
             
        # Finds all jobs available on the (viewable) page
        # data-control-name: A_jobssearch_job_result_click
        jobs = driver.find_elements_by_css_selector('a[class="job-card-search__link-wrapper js-focusable-card ember-view"][tabindex="-1"]')
        
        # Opens all the job links in new tabs
        open_all_jobs_in_page(jobs, driver)
        
        # Clicks 'Easy Apply' for each of these jobs
        apply(driver)
        driver.switch_to_window(driver.window_handles[0])
        i += 1
   
    driver.get('https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3&f_LF=f_AL&keywords=Data%20Scientist&start=' + str(j*25))
    j += 1
    i = 0

# Miscellaneous Notes 
# mobile_login_href = 'https://www.linkedin.com/uas/login?session_redirect=%2Fjobs%2Fsearch%2F%3Ff_E%3D1%252C2%252C3%252C4%26f_LF%3Df_AL%26keywords%3DData%2BAnalyst%26bypassMobileRedirects%3Dfalse&emailAddress=&fromSignIn=&trk=jobs_mobile_chrome_login'

# Notes for selenium:
# Selenium does not store tabs in order of the way they appear on Chrome. It
# stores them in a LIFO stack - thus the oldest tab is tab[0] and the newest 
# one is tab[n-1] where the stack is of size n.
    
# LinkedIn's job search pages show 25 jobs at a time. To go to the next page
# the easiest way is to go to the link with the next 25. 