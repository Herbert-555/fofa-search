# fofa-search
特色：无需API、多线程爬取

usage:

```
usage: fofa_search.py [-h] -q QUERY [-p PAGE] [-f {url,all}] [-o OUTPUT]

optional arguments:
  -h, --help    show this help message and exit
  -q QUERY      指定查询语法,例:-q 'banner="laravel_session" && country="US"' (使用单引号包裹语法)
  -p PAGE       指定爬取页数,默认爬取10页
  -f {url,all}  url:http://<ip><:port> all:url + <ip><:port> (default: all)
  -o OUTPUT     output result to FILE

Examples:
        python fofa_search.py -q 'banner="laravel_session" && country="US"' -p 30 -f all -o res.txt
```

初始化：

将cookie中fofa_token部分放入config.ini中即可。

<div align="center">
  <img src="https://github.com/h4cker-369/fofa-search/blob/main/data/2.png">
</div>

<div align="center">
  <img src="https://github.com/h4cker-369/fofa-search/blob/main/data/3.png">
</div>

登录时选择保持登录可以维持很久。

<div align="center">
  <img src="https://github.com/h4cker-369/fofa-search/blob/main/data/4.png">
</div>

常用命令：

```
python .\fofa_search.py -q 'title="Admin Web"' -p 10 -o res.txt
```

-q 指定查询语法（使用单引号包裹）。

-p 指定爬取页数

-o 资产输出文件（一行一个）。

<div align="center">
  <img src="https://github.com/h4cker-369/fofa-search/blob/main/data/1.png">
</div>

默认搜集所有资产，如果只想搜集url资产，可指定-f url

```
python .\fofa_search.py -q 'title="Admin Web"' -p 10 -o res.txt -f url
```

不搜集http资产 -f port

```
python .\fofa_search.py -q 'title="Admin Web"' -p 10 -o res.txt -f port
```

