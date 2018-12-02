# *-* coding=utf-8 *-*
"""
妹子图有反爬虫机制，主要在于其headers必须有if-none-match和referer
这两项不为空即可
"""

import requests
from multiprocessing import Pool, Queue
from lxml import html
import os

main_url = "https://www.mzitu.com"
headers = {'if-none-match': "hhhh",  # 可以为任意字符串
           'referer': 'https://www.mzitu.com'  # 可以为任意字符串
           }


class MztScrapy(object):
    # count = 0

    def __init__(self):
        self.chepai = None
        self.max_pics = int()  # 记录套图所包含图片数
        self.group_name = None  # 保存套图名
        self.count = 1
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
            # 车牌无误情况下判断该组图片的最大页码
            self.max_pics = int(check_page.xpath('/html/body/div[2]/div[1]/div[4]/a[5]/span/text()')[0])
            self.group_name = check_page.xpath('/html/body/div[2]/div[1]/h2/text()')[0]
            print('车牌%s对应的套图为:%s,共计%s张！' % (self.chepai, self.group_name, self.max_pics))
            try:
                os.mkdir('Download/'+self.group_name)
            except FileExistsError:
                pass

    def down(self, num):
        # print('a')
        # 获取套图每张图的地址并下载
        if self.count <= self.max_pics:

            # q.put(' ')

            # q.get()
            page = requests.get(url=main_url + '/' + str(self.chepai) + '/' + str(num)).content
            print('正在下载第%d张。' % num)
            page = html.fromstring(page)
            pic_url = page.xpath("/html/body/div[2]/div[1]/div[3]/p/a/img//@src")  # 获取图片的网址
            pic_name = page.xpath('/html/body/div[2]/div[1]/h2/text()')  # 获取图片的命名
            pic_content = requests.get(pic_url[0], headers=headers).content
            f = open('Download/'+self.group_name+'/'+pic_name[0] + '.jpg', 'wb')
            # print('Download/'+self.group_name+'/'+pic_name[0] + '.jpg')
            f.write(pic_content)
            f.close()
            self.count += 1

    # 启用多线程下载
    def multi_down(self):
        q = Queue(1)  # 锁定页码变更，一次只能有一个页码调用
        p = Pool(3)  # 创建进程池
        for i in range(self.max_pics):
            p.apply_async(self.down, args=(i, ))
        print("----start----")
        p.close()
        p.join()
        print("----stop----")


def main():
    client = MztScrapy()  # 创建下载器
    client.check_chepai()
    client.multi_down()


if __name__ == "__main__":
    main()
