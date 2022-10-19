import re, os
import json
import requests
import time, glob
import csv
import traceback
import random
random.uniform(6,10)

# read csv
def write_csv(filepath, data, head=None):
    if head:
        data = [head] + data
    with open(filepath, mode='w', encoding='UTF-8-sig', newline='') as f:
        writer = csv.writer(f)
        for i in data:
            writer.writerow(i)


# write csv
def read_csv(filepath):
    data = []
    if os.path.exists(filepath):
        with open(filepath, mode='r', encoding='utf-8') as f:
            lines = csv.reader(f)  # #此处读取到的数据是将每行数据当做列表返回的
            for line in lines:
                data.append(line)
        return data
    else:
        print('filepath is wrong：{}'.format(filepath))
        return []


def grab_img_baidu(_url, _headers=None):
    if _headers == None:
        # 设置请求头 request header
        headers = {
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            "Referer": "https://map.baidu.com/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
    else:
        headers = _headers
    response = requests.get(_url, headers=headers)

    if response.status_code == 200 and response.headers.get('Content-Type') == 'image/jpeg':
        return response.content
    else:
        return None


def openUrl(_url):
    # 设置请求头 request header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    response = requests.get(_url, headers=headers)
    if response.status_code == 200:  # 如果状态码为200，寿命服务器已成功处理了请求，则继续处理数据
        return response.content
    else:
        return None


def getPanoId(_lng, _lat):
    # 获取百度街景中的svid get svid of baidu streetview
    url = "https://mapsv0.bdimg.com/?&qt=qsdata&x=%s&y=%s&l=17.031000000000002&action=0&mode=day&t=1530956939770" % (
        str(_lng), str(_lat))
    response = openUrl(url).decode("utf8")
    # print(response)
    if (response == None):
        return None
    reg = r'"id":"(.+?)",'
    pat = re.compile(reg)
    try:
        svid = re.findall(pat, response)[0]
        return svid
    except:
        return None


# 官方转换函数
# 因为百度街景获取时采用的是经过二次加密的百度墨卡托投影bd09mc (Change wgs84 to baidu09)
def wgs2bd09mc(wgs_x, wgs_y):
    # to:5是转为bd0911，6是转为百度墨卡托
    url = 'http://api.map.baidu.com/geoconv/v1/?coords={}+&from=1&to=6&output=json&ak={}'.format(
        wgs_x + ',' + wgs_y,
        'mYL7zDrHfcb0ziXBqhBOcqFefrbRUnuq'
    )
    res = openUrl(url).decode()
    temp = json.loads(res)
    bd09mc_x = 0
    bd09mc_y = 0
    if temp['status'] == 0:
        bd09mc_x = temp['result'][0]['x']
        bd09mc_y = temp['result'][0]['y']

    return bd09mc_x, bd09mc_y
  
  path=r'C:\Users\Administrator\OneDrive - whu.edu.cn\旅游视角与街景视角的认知偏见\BaiduStreetViewSpider-main\dir2\images'

res_files=[]
import os
for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
        # print(os.path.join(root, name))
        res_files.append( name)

tdata={'x':[],'y':[],'tmp':[]}
for i in res_files:
    try:
        tmp=i.split('_')
        tdata['x'].append(tmp[0])
        tdata['y'].append(tmp[1])
        tdata['tmp'].append(tmp[0]+','+tmp[1])
    except:
        print(i)
tdata['tmp'][0]

new_files=[]
for i in res_files:
    tmp=i.split('_')
    new_files.append(tmp[0]+','+tmp[1])
len(new_files)    


root = r'.\dir2'
read_fn = r'whpos.csv'
# read_fn=r'error_road_intersection.csv'

error_fn = r'error_road_intersection2.csv'
dir = r'images'
filenames_exist = glob.glob1(os.path.join(root, dir), "*.png")

# 读取 csv 文件
data = read_csv(os.path.join(root, read_fn))
# 记录 header
header = data[0]
# 去掉 header
data = data[1:]
# 记录爬取失败的图片
error_img = []
# 记录没有svid的位置
svid_none = []
# headings = ['0', '90', '180', '270'] # directions, 0 is north
pitchs = '0'

count = 1
# while count < 210:


for i in range(len(data)):
    try:
        # print('Processing No. {} point...'.format(i + 1))
        # gcj_x, gcj_y, wgs_x, wgs_y = data[i][0], data[i][1], data[i][2], data[i][3]


        wgs_x, wgs_y = data[i][4], data[i][3] #data[i][15], data[i][16]

        if wgs_x+','+wgs_y not in tdata['tmp']:
            try:
                bd09mc_x, bd09mc_y = wgs2bd09mc(wgs_x, wgs_y)
            except Exception as e:
                print(str(e))  # 抛出异常的原因
                continue
            flag = True
            headings=[data[i][-1],data[i][-2],data[i][-3],data[i][-4]]
            for k in range(len(headings)):
                flag = flag and "%s_%s_%s_%s.png" % (wgs_x, wgs_y, headings[k], pitchs) in filenames_exist

            # If all four files exist, skips
            if (flag):
                continue
            svid = getPanoId(bd09mc_x, bd09mc_y)
            print(svid)
            for h in range(len(headings)):
                save_fn = os.path.join(root, dir, '%s_%s_%s_%s.png' % (wgs_x, wgs_y, headings[h], pitchs))
                url = 'https://mapsv0.bdimg.com/?qt=pr3d&fovy=90&quality=100&panoid={}&heading={}&pitch=0&width=480&height=320'.format(
                    svid, headings[h]
                )
                img = grab_img_baidu(url)
                if img == None:
                    data[i].append(headings[h])
                    error_img.append(data[i])

                if img != None:
                    # print(os.path.join(root, dir))
                    with open(os.path.join(root, dir) + r'\%s_%s_%s_%s.png' % (wgs_x, wgs_y, headings[h], pitchs),
                                "wb") as f:
                        f.write(img)

            # 记得睡眠6s，太快可能会被封
            time.sleep(random.uniform(4,7))
            count += 1
    except Exception as e:
        print(e)
        if e=='TimeoutError':
            time.sleep(1000)
        else:
            time.sleep(600)
# 保存失败的图片
if len(error_img) > 0:
    write_csv(os.path.join(root, error_fn), error_img, header)
    
data={'x':[],'y':[]}
for i in res_files:
    try:
        tmp=i.split('_')
        data['x'].append(tmp[0])
        data['y'].append(tmp[1])
    except:
        print(i)

data={'x':[],'y':[]}
for i in res_files:
    try:
        tmp=i.split('_')
        data['x'].append(tmp[0])
        data['y'].append(tmp[1])
    except:
        print(i)
 
