from selenium import webdriver
import time
import urllib.request
import os
import argparse


def webcrawling(inputurl, cnt, outputdir):
    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)
    episode = int(inputurl.split("&")[1][3:])
    if not os.path.exists('./' + outputdir + '/Episode' + str(episode)):
        os.mkdir('./' + outputdir + '/Episode' + str(episode))

    driver = webdriver.Chrome(r"C:/Chromedriver/chromedriver.exe")
    driver.get(inputurl)
    

    for _ in range(cnt):
        # waiting for loading time
        time.sleep(1)
        try:
            title = driver.find_element_by_css_selector(".view h3")
            print(title.text)
        except Exception as e:
            print(e)
            continue

        # download image
        for cuts in range(len(driver.find_elements_by_css_selector(".wt_viewer img"))-1):
            imgUrl = driver.find_elements_by_css_selector(".wt_viewer img")[cuts].get_attribute("src")
            print(imgUrl)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent',
                                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(imgUrl, outputdir + '/Episode' + str(episode) + '/' + str(cuts) + '.png')

        # go to the next page
        episode += 1
        try:
            driver.find_element_by_css_selector(".next").click()
        except:
            print("Failed")
            break
        if not os.path.exists('./' + outputdir + '/Episode' + str(episode)):
            os.mkdir('./' + outputdir + '/Episode' + str(episode))

    driver.close()