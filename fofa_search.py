# coding=utf-8
import requests, base64
import urllib3
import re
import argparse
import threading
import configparser
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def title():
    print('------------------------------------------------------------------------------------------')
    print('[+]  \033[34mTitle:FOFA_search\033[0m')
    print('[+]  \033[34mVersion: 2023-4-1 \033[0m')
    print('[+]  \033[34mAuthor by Herbert555(https://blog.csdn.net/qq_44657899)\033[0m')
    print('------------------------------------------------------------------------------------------\n')

class fofa_search():
    def __init__(self, search_text='domain="baidu.com"', page=10, type="all", output="res.txt"):
        # 读取fofa_token
        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        fofa_token = cfg.get("FOFA", "fofa_token")
        # 初始化
        self.search_text = search_text
        self.cookie = f"fofa_token={fofa_token}"
        self.page = int(page)
        self.type = type
        self.agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
        self.headers = {"User-Agent": self.agent, "Cookie": self.cookie}    # , "Authorization":Authorization
        self.url = "https://fofa.info/result?qbase64={0}&page={1}&page_size=20"   # https://fofa.info/result?qbase64={0}&page={1}&page_size=20&full=true
        self.target_list = []
        self.threads = []
        self.output = output

    # 获取最大页数
    def get_max_page(self):
        url = self.url.format(base64.b64encode(self.search_text.encode()).decode(), 20)
        req = requests.get(url=url, headers=self.headers,verify=False)  # proxies={"https":"127.0.0.1:8080"}
        # print(req.text)
        try:
            max_page = re.findall("min=\"1\" max=\"(\d+)\"", req.text).pop(-1)
            max_page = int(max_page)
            print("[+] 最大页数 " + str(max_page))
            # 最多读取500页
            max_page = 500 if max_page > 500 else max_page
            return max_page
        except Exception as e:
            print("获取最大页数失败,class:fofa_search->get_max_page:" + str(e))
            return 1

    # 只爬取web资产
    def get_web(self, page=1):
        url = self.url.format(base64.b64encode(self.search_text.encode()).decode(), page)
        req = requests.get(url=url, headers=self.headers, timeout=20, verify=False)
        content = req.text
        targets_http = re.findall(r"<span class=\".*?\"><a href=\"(http.*?)\" target=\"_blank\">", content)
        targets_http = list(set(targets_http))
        print(f"数量:{str(len(targets_http))}\t资产:{', '.join(targets_http)}")
        if len(targets_http) == 20:
            url = self.url.format(base64.b64encode(self.search_text.encode()).decode(), 2)
            req = requests.get(url=url, headers=self.headers, timeout=20, verify=False)
            content = req.text
            targets_http2 = re.findall(r"<span class=\".*?\"><a href=\"(http.*?)\" target=\"_blank\">", content)
            targets_http2 = list(set(targets_http2))
            print(f"数量:{str(len(targets_http))}\t资产:{', '.join(targets_http2)}")
            targets_http = targets_http + targets_http2
        return list(targets_http)

    # 只爬取ip:port资产
    def get_port(self, page=1):
        url = self.url.format(base64.b64encode(self.search_text.encode()).decode(), page)
        req = requests.get(url=url, headers=self.headers, timeout=20,verify=False)
        content = req.text
        targets_http = re.findall(r"<span class=\".*?\">(.*?:\d+)</span>", content)
        targets_http += re.findall(r"<span class=\".*?\"><a href=\"(http.*?)\" target=\"_blank\">", content)
        print(f"资产:{', '.join(targets_http)}")
        return targets_http

    def get_res(self, page):
        try:
            url = self.url.format(base64.b64encode(self.search_text.encode()).decode(), page + 1)
            req = requests.get(url=url, headers=self.headers, timeout=20, verify=False, proxies={"https":"127.0.0.1:8080"})
            content = req.text
            targets_http = []
            # 采集所有
            if self.type == "all":
                targets_http = re.findall(r"<span class=\".*?\">(.*?:\d+)</span>", content)
                targets_http += re.findall(r"<span class=\".*?\"><a href=\"(http.*?)\" target=\"_blank\">", content)
            # url采集
            elif self.type == "url":
                targets_http = re.findall(r"<span class=\".*?\"><a href=\"(http.*?)\" target=\"_blank\">", content)
            # ip+port
            elif self.type == "port":
                targets_http = re.findall(r"<span class=\".*?\">(.*?:\d+)</span>", content)
            print(f"page:{page + 1} 资产数:{len(targets_http)} 线程:{threading.active_count()} 资产:\033[1;34m{', '.join(targets_http[:3])} ... ...\033[0m")
            if targets_http or "[45012]" not in req.text:
                self.target_list += targets_http
            else:
                print("[-] 请求速度过快!!!正在重新获取")
                time.sleep(1)
                self.get_res(page)
        except Exception as e:
            print(f"获取第{str(page+1)}页数据失败,正在重试:" + str(e))
            # self.get_res(page)

    # fofa有请求速度限制，限制线程数
    def control_rate(self):
        if threading.active_count() == 2:
            time.sleep(2)
        elif threading.active_count() == 3:
            time.sleep(2)
        elif threading.active_count() == 4:
            time.sleep(2)
        elif threading.active_count() >= 5:
            time.sleep(3)

    # 多线程执行任务
    def scan(self):
        time_start = time.time()
        max_page = self.get_max_page()
        # 用户指定页数超出最大页数,取最大页数
        self.page = self.page if self.page < max_page else max_page
        for page in range(int(self.page)):
            try:
                t1 = threading.Thread(target=self.get_res, args=(page,))
                self.threads.append(t1)
                t1.start()
                self.control_rate()
                # 线程为5差不多
                while threading.active_count() >= 5:
                    time.sleep(0.5)
            except Exception as e:
                print(e)
                pass
        for t in self.threads:
            t.join()
        print("\n\033[1;31m[+] 本次搜集:" + str(len(self.target_list)) + " 应搜集:" + str((self.page - 1) * 20) + "~" + str(self.page * 20)+"\033[0m")
        time_sum = time.time() - time_start  # 计算的时间差为程序的执行时间,单位为秒/s
        print("\033[1;32m[+] 用时 " + str(time_sum) + "s\033[0m")
        self.save_res(self.target_list)
        return self.target_list

    # 保存结果
    def save_res(self, target_list=[]):
        str1 = "\n"
        file = self.output
        try:
            with open(file, "w") as f:
                f.write(str1.join(target_list))
                print(f"\033[1;34m[+]结果保存至文件:{file}\033[0m")
        except Exception as e:
            print("\033[1;34m [-]写入文件失败,函数:save_res" + str(e) + "\033[0m")


if __name__ == '__main__':
    # print("use type:all port url")
    title()
    parse = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,)
    parse.add_argument('-q', dest='query', type=str, required=True, help='指定查询语法,例:-q \'banner="laravel_session" && country="US"\' (使用单引号包裹语法)')
    parse.add_argument('-p', dest='page', type=str, default=10, help='指定爬取页数,默认爬取10页')
    parse.add_argument('-f', dest='type', choices=['url', 'all'], default='all', type=str, help='url:http://<ip><:port> all:url + <ip><:port> (default: all)')
    parse.add_argument('-o', dest='output', default='target.txt', type=str,
                       help='output result to FILE')

    parse.epilog = 'Examples:\n\t' \
                    'python fofa_search.py -q \'banner="laravel_session" && country="US"\' -p 30 -f full -o res.txt\t\n\t'

    search = parse.parse_args().query
    page = parse.parse_args().page
    type = parse.parse_args().type
    output = parse.parse_args().output
    info = fofa_search(search_text=search, page=page, type=type, output=output).scan()
