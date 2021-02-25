import requests
import re
import json
import os
import time
from lxml import etree

class Bilibili_spider(object):
    
    def __init__(self, bvid):
        self.bvid = bvid
        self.headers1 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        self.headers2 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
            "host": "",
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/video/%s' %(bvid,),
        }

    def parse_url(self,url,headers,params=''):
        return requests.get(url,headers=headers,params=params).text

    def str_to_json(self,response):
        return json.loads(response)

    def get_title(self,response):
        html = etree.HTML(response)
        title = html.xpath("//h1/span/text()")[0]
        return title

    def get_playurl(self,video_list,playurl_list):
        for video in video_list:
            cid = video["cid"]
            name = video["part"].replace('/','-').replace(' ','')

            play_url = 'https://api.bilibili.com/x/player/playurl'
            params = {
            "cid":cid,
            "bvid":self.bvid,
            "qn": "80",
            "otype": "json",
            # "fourk": "1",
            # "fnver": "0",
            # "fnval": "80"
            }

            play_response = self.str_to_json(self.parse_url(play_url,self.headers1,params=params))
            playurl = play_response["data"]["durl"][0]["url"]
            playurl_list.append([playurl,name])
            self.headers2["host"]  = playurl.split('/')[2]

    def download_file(self,url,path):
        
        r = requests.get(url,headers=self.headers2,stream=True)
            #定义一个1024的字节
        chunk_size=1024*1024
        content_size=int(r.headers['content-length'])
        # print(content_size)

        with open(path,"wb") as f:
            n = 0
            #边下载边存硬盘  chunk_size=chunk_size可修改 单位为B
            for  chunl in r.iter_content(chunk_size=chunk_size):

                f.write(chunl)

                n = n + len(chunl)
                now = (n / content_size) * 100
                print("\r视频下载进度：%d%%(%d/%d)" % (now, n, content_size), end="")



    def run(self):
        #1 准备url地址
        url = 'https://www.bilibili.com/video/%s' %(self.bvid,)
        videolist_url = 'https://api.bilibili.com/x/player/pagelist?bvid=%s&jsonp=jsonp' %(self.bvid,)
        #2 发送请求，获取响应
        title_response = self.parse_url(url,self.headers1)
        #3 解析数据获取视频名字，并以此建立文件夹
        title = self.get_title(title_response)
        if not os.path.exists(title):
            os.mkdir(title)
        #4 从动态请求中获取视频列表数据
        video_list = self.str_to_json(self.parse_url(videolist_url,self.headers1))["data"]
        totel = len(video_list)
        print("共有%s个视频等待下载：" %(totel,)) 
        #5 遍历列表，获取最终的视频文件地址
        playurl_list = []
        self.get_playurl(video_list,playurl_list)
        #6 下载视频文件保存本地
        for playurl in playurl_list:
            path = '%s/%s.flv' %(title,playurl[1])
            if not os.path.exists('%s/%s.flv' %(title,playurl[1])):
                print("%s视频开始下载：" %(playurl[1],))
                
                self.download_file(playurl[0],path)
                
            print()
            totel-=1
            print("success!-------> 还剩%s个视频未下载" %(totel,))
            print('='*50)
            time.sleep(1)


if __name__ == '__main__':
    bilibili = Bilibili_spider('BV1jr4y1K7hf')
    bilibili.run()
    os.system('pause')
