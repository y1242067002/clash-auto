import os, yaml, base64, requests, socket, time
from urllib.parse import urlparse, unquote

sources_file = "sub/sources.txt"
out_main = "output/merged.yaml"

ping_timeout = 0.6

def fetch(url):
    try:
        return requests.get(url, timeout=15).text
    except:
        return ""

def decode(c):
    try:
        return base64.b64decode(c).decode()
    except:
        return c

def parse(line):
    try:
        if line.startswith("vmess://"):
            d = yaml.safe_load(base64.b64decode(line[8:] + "==").decode())
            return {"name": d.get("ps","vmess"),"type":"vmess","server":d["add"],"port":int(d["port"]),"uuid":d["id"],"alterId":0,"cipher":"auto"}
        if line.startswith("trojan://"):
            p=urlparse(line[9:])
            return {"name":unquote(p.fragment) or "trojan","type":"trojan","server":p.hostname,"port":p.port,"password":p.username}
        if line.startswith("vless://"):
            p=urlparse(line[8:])
            return {"name":unquote(p.fragment) or "vless","type":"vless","server":p.hostname,"port":p.port,"uuid":p.username}
    except:
        return None

def ping(h,p):
    try:
        s=socket.socket()
        s.settimeout(ping_timeout)
        t=time.time()
        s.connect((h,p))
        s.close()
        return (time.time()-t)*1000
    except:
        return None

os.makedirs("output",exist_ok=True)

nodes=[]
for u in open(sources_file):
    for l in decode(fetch(u.strip())).splitlines():
        n=parse(l.strip())
        if n and n.get("server"):
            d=ping(n["server"],n["port"])
            if d:
                n["delay"]=d
                nodes.append(n)

nodes=sorted(nodes,key=lambda x:x["delay"])[:30]

names=[n["name"] for n in nodes] or ["占位"]

cfg={
"port":7890,
"mode":"rule",
"proxies":nodes,
"proxy-groups":[{"name":"🚀 自动选择","type":"url-test","url":"http://www.gstatic.com/generate_204","interval":120,"proxies":names}],
"rules":["MATCH,🚀 自动选择"]
}

yaml.safe_dump(cfg,open(out_main,"w"),allow_unicode=True,sort_keys=False)
