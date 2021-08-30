from selenium import webdriver
import time
import urllib.request
import cv2
import numpy as np
import os
import math
import argparse
import natsort
import shutil
from PIL import Image

def webcrawling(inputurl, episodelastname, episodenum, outputdir):
    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)
    if not os.path.exists('./' + outputdir + '/Episode' + str(episodenum)):
        os.mkdir('./' + outputdir + '/Episode' + str(episodenum))

    driver = webdriver.Chrome(r"C:/Users/원지윤/chromedriver.exe")
    driver.get(inputurl)
    episode = episodenum    # bonus episode not included, i.e. special edition, ...

    while 1:
        # waiting for loading time
        time.sleep(1)
        title = driver.find_element_by_css_selector(".view h3")
        print(title.text)

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
        if (title.text == episodelastname):
            break
        episode -= 1
        driver.find_element_by_css_selector(".pre").click()
        if not os.path.exists('./' + outputdir + '/Episode' + str(episode)):
            os.mkdir('./' + outputdir + '/Episode' + str(episode))

    driver.close()


def linkimg(inputdir, episodedir):
    imglist = os.listdir('./' + inputdir + '/' + episodedir)

    # sorted with image name
    imgtype = imglist[0][-4:]
    sortedimg = [int(img[0:-4]) for img in imglist]
    sortedimg.sort()

    # entire height of new image
    entire_height = 0
    for img in sortedimg:
        _img = cv2.imread('./' + inputdir + '/' + episodedir + '/' + str(img) + imgtype)
        height, width, _ = _img.shape
        entire_height += height

    # create new image
    newimg = np.zeros((entire_height, width, 3), np.uint8)

    # linking all crawling image
    hp = 0
    for img in sortedimg:
        _img = cv2.imread('./' + inputdir + '/' + episodedir + '/' + str(img) + imgtype)
        height, width, _ = _img.shape
        try:
            newimg[hp:(hp + height), :, :] = _img[:]
        except:
            _, w, _ = newimg.shape
            _img = cv2.resize(_img, dsize=(w, height))
            newimg[hp:(hp + height), :, :] = _img[:]
        hp += height

    # cv2.imwrite("all_cut_.png", newimg)
    return newimg


def cutdetector_rough(inputimg, outputdir, episodedir, episodenum): #outputdir: roughcutdir(cuts), episodedir: elist
    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)
    if not os.path.exists('./' + outputdir + '/' + episodedir):
        os.mkdir('./' + outputdir + '/' + episodedir)

    spt, ept = 0, 0
    val = 0
    cutnum = 1
    for row in range(len(inputimg[:,0,:])):
        if (len(np.unique(inputimg[row, :, :])) != 1) & (val == 0):
            spt = row
            val = 1
        elif (len(np.unique(inputimg[row, :, :])) == 1) & (val == 1):
            ept = row
            val = 0

        if (spt != 0) and (ept != 0) and ((ept - spt - 1) > 0):
            newimg = np.zeros((ept - spt - 1, len(inputimg[0,:,:]), 3), np.uint8)
            newimg[:] = inputimg[spt:ept - 1, :, :]
            cv2.imwrite('./' + outputdir + '/' + episodedir + '/' + episodenum + '_' + str(cutnum) + '.png', newimg)
            spt, ept = 0, 0
            cutnum = cutnum + 1


def cutdetector(inputdir, outputdir, episodenum): #inputdir: roughcutdir, outputdir: cutdir
    imglist = os.listdir('./' + inputdir)
    sortedimglist = natsort.natsorted(imglist)
    print('all file length', len(sortedimglist))

    if not os.path.exists('./' + outputdir):
        os.mkdir('./' + outputdir)

    if '.DS_Store' in sortedimglist:
        sortedimglist.remove('.DS_Store')
        print('.DS_Store erased!')

    cutnum = 1
    for k in range(len(sortedimglist)):
        try:
            print('{} image processing: {}'.format(k + 1, sortedimglist[k]))
            image = cv2.imread('./' + inputdir + '/{}'.format(sortedimglist[k]), cv2.IMREAD_UNCHANGED)
            print('./' + inputdir + '/{}'.format(sortedimglist[k]))
            if sortedimglist[k] == 'actual':
                continue
            height, width, channel = image.shape

            output = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            canny = cv2.Canny(gray, 3000, 2000, apertureSize=5, L2gradient=True)

            lines = []

            lines = cv2.HoughLines(canny, 0.8, np.pi / 180, 200, srn=100, stn=200, min_theta=0, max_theta=np.pi)


            y_list = []

            if isinstance(lines, np.ndarray):
                for i in lines:
                    rho, theta = i[0][0], i[0][1]

                    if not math.isnan(rho) and not math.isnan(theta):
                        a, b = np.cos(theta), np.sin(theta)
                        x0, y0 = a * rho, b * rho

                        scale = image.shape[0] + image.shape[1]

                        x1 = int(x0 + scale * -b)
                        y1 = int(y0 + scale * a)
                        x2 = int(x0 - scale * -b)
                        y2 = int(y0 - scale * a)

                        if y1 == y2 and 0 <= y1 <= height:
                            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            y_list.append(y1)

            if y_list != []:
                output = output[min(y_list):max(y_list), 0:width]
                # plt.axis('off')
                # plt.imshow(output)
                # plt.show()
                try:                    
                    output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
                    cv2.imwrite('./' + outputdir + '/' + episodenum + '_' + str(cutnum) + '.png', output)
                    
                    if not os.path.exists('./' + outputdir + '/'+'crop'):
                        os.mkdir('./' + outputdir + '/'+'crop')
                    
                    crop=cv2.imread('./' + outputdir + '/' + episodenum + '_' + str(cutnum) + '.png')
                    h=crop.shape[0]
                    w=crop.shape[1]
                    if h>w:
                        dst=crop[int((h-w)/2):int((h+w)/2),0:w]
                    else:
                        dst=crop[0:h,int((w-h)/2):int((h+w)/2)]
                    scale = cv2.resize(dst,(512,512),interpolation=cv2.INTER_LINEAR)
                    cv2.imwrite('./' + outputdir +'/'+'crop'+'/'+episodenum + '_' + str(cutnum) +'.png',scale)
                    cutnum += 1
                except:
                    print("cv2.cvtColor error!")
                    f = open("error_list.txt", 'a')
                    f.write('./' + inputdir + '/{}'.format(imglist[k]) + "\n")
            else:
                print('no image cut')
            print()
        except:
            print('error: ', 'Process finished with exit code -1073741819 (0xC0000005)')
            continue
def cut_crop(path,save_path):
    img=cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
    morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)
    cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnt = sorted(cnts, key=cv2.contourArea)
    print(len(cnt))
    for i in range (len(cnt)):
        border=0
        x,y,w,h = cv2.boundingRect(cnt[i])
        dst = img[y:y+h, x:x+w]
        cv2.imwrite(save_path+'_'+str(i)+".png", dst)
        cutcrop=cv2.imread(save_path+'_'+str(i)+".png")
        if h>w:
            dst_=cv2.copyMakeBorder(cutcrop,0,0,int((h-w)/2),int((h-w)/2),cv2.BORDER_CONSTANT,(255,255,255))
        else:
            dst_=cv2.copyMakeBorder(cutcrop,int((w-h)/2),int((w-h)/2),0,0,cv2.BORDER_CONSTANT,(255,255,255))
        scale = cv2.resize(dst_,(512,512),interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(save_path+'_'+str(i)+".png",scale)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--web_dir', default='webcrawlingimg', type = str,
                        help='webcrawling image directory name.')
    parser.add_argument('--roughcut_dir', default='cuts', type = str,
                        help='rough cut image directory name.')
    parser.add_argument('--cutdector_dir', default='actual', type = str,
                        help='final cut image directory name.')
    #예)1화~100화 추출할 때->start는 100화, end는 1화
    parser.add_argument('--start_website_url', default='https://comic.naver.com/webtoon/detail?titleId=570503&no=366&weekday=thu', type = str,
                        help='start website url. if you want to get episode100~101, put episode 101 url!')
    parser.add_argument('--end_website_title', default='361. 딜레마존 (6) <분기점>', type = str,
                        help='end website title. if you want to get episode100~101, put episode 100 title!')
    parser.add_argument('--start_episode_num', default=362, type = int,
                        help='start episode number.')
    args = parser.parse_args()

    webdir = args.web_dir
    roughcutdir = args.roughcut_dir
    cutdir = args.cutdector_dir
    webcrawling(args.start_website_url, args.end_website_title, args.start_episode_num, webdir)

    episodelist = os.listdir(webdir)
    for elist in episodelist:
        print(elist)
        episodenum = elist[7:]
        linkedIMG = linkimg(webdir, elist)
        cutdetector_rough(linkedIMG, roughcutdir, elist, episodenum)
        cutdetector(roughcutdir + '/' + elist, cutdir, episodenum)
    #delete folder(webcrawlingimp, cuts)
    #shutil.rmtree('./webcrawlingimg')
    #shutil.rmtree('./cuts')d