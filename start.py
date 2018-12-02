# uer/bin/env python3
# *-* coding=utf-8 *-*

"""
妹子图有反爬虫机制，主要在于其headers必须有if-none-match和referer
这两项不为空即可
"""

import requests
from multiprocessing import Pool, Manager
from lxml import html
import os

main_url = "https://www.mzitu.com"
headers = {'if-none-match': "hhhh",  # 可以为任意字符串
           'referer': 'https://www.mzitu.com'  # 可以为任意字符串
           }


class MztScrapy(object):
    count = 0

    def __init__(self):
        self.chepai = None
        self.max_pics = int()  # 记录套图所包含图片数
        self.group_name = None  # 保存套图名
        self.count = [1]

    # 检测所给番号是否有误
    def check_chepai(self):
        chepai = input("请输入车牌号：")
        if chepai == 'exit':
            exit()
        self.chepai = chepai
        # 妹子图官网可以接受任何的车牌，故这里不对车牌类型做检测
        check_page = requests.get(main_url + '/' + str(self.chepai)).content
        check_page = html.fromstring(check_page)
        if check_page.xpath('/html/body/div[2]/div[1]/div[1]/text()')[0] == '404! 没有这个妹子,以下为您随机推荐几组妹子图':
            print("输入的番号有误！请重新输入!(输入exit退出)")
            return self.check_chepai()  # 车牌有误的情况下重新输入
        else:
            # 车牌无误情况下判断该组图片的最大页码并创建文件夹
            self.group_name = check_page.xpath('/html/body/div[2]/div[1]/h2/text()')[0]
            self.max_pics = int(check_page.xpath('/html/body/div[2]/div[1]/div[4]/a[5]/span/text()')[0])
            print('车牌%s对应的套图为:%s,共计%s张！' % (self.chepai, self.group_name, self.max_pics))
            try:
                os.mkdir('Download/'+self.group_name)
                # print('Download/'+self.group_name+'['+str(chepai)+']')
            except FileExistsError:
                pass

    def down(self, num, q):
        # 获取套图每张图的地址并下载
        if MztScrapy.count < self.max_pics:
            page = requests.get(url=main_url + '/' + str(self.chepai) + '/' + str(num)).content
            page = html.fromstring(page)
            pic_url = page.xpath("/html/body/div[2]/div[1]/div[3]/p/a/img//@src")  # 获取图片的网址
            pic_name = page.xpath('/html/body/div[2]/div[1]/h2/text()')  # 获取图片的命名
            # 文件存在则跳过改文件
            if not os.path.exists('Download/'+self.group_name+'/'+pic_name[0] + '.jpg'):
                pic_content = requests.get(pic_url[0], headers=headers).content
                f = open('Download/'+self.group_name+'/'+pic_name[0] + '.jpg', 'wb')
                f.write(pic_content)
                f.close()
            MztScrapy.count += 1
            q.put("...")

    # 启用多线程下载
    def multi_down(self):
        q = Manager().Queue()
        p = Pool(20)  # 创建进程池
        for num in range(self.max_pics):
            p.apply_async(self.down, args=(num, q, ))
        print("----start----")
        print('下载...', end='')
        p.close()
        # p.join()
        comle_count = 0
        while True:
            q.get()  # 做阻塞用，保证每个线程完成后再做完成率计算
            comle_count += 1
            # print(comle_count)
            # print(type(comle))
            down_rate = comle_count/self.max_pics * 100
            print('\r【%s】已经下载完成%0.2f%%(完成%d张，还剩%d张)...' % (self.group_name, down_rate, comle_count, self.max_pics-comle_count), end=' ')
            if down_rate >= 100:
                print('\r【%s】已经下载完成(%d张).' % (self.group_name, self.max_pics))
                break

        print("----end----")


def scrapy_method():
    print("请输入想要爬取的方式：")
    print("")
    print("序号\t\t爬取类型")
    print("-"*20)
    print("01\t\t首页")
    print("02\t\t性感妹子")
    print()


def main():


    client = MztScrapy()  # 创建下载器
    client.check_chepai()
    client.multi_down()


if __name__ == "__main__":
    # main()
    scrapy_method()
