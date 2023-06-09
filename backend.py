#!/usr/bin/env python3

from flask import Flask, request
import os
import openai;
import requests;
import json;
import re;
import argparse;
from search_researchers.Retrieve import bot_api;
import sys;
import signal;
import copy

app = Flask(__name__)
func_dict = {}
alarm_dict = {}
alarm_id = ''

'''监听端口，获取QQ信息'''
@app.route('/', methods=["POST"])
def post_data():
    global msg;
    if request.get_json().get('message_type')=='group':
        gid = request.get_json().get('group_id')
        message = request.get_json().get('raw_message')
        handle(str(gid), message);

    return 'OK'

def register_func(name, alarm):
    def decorator(func):
        func_dict[name] = func
        alarm_dict[name] = alarm
        return func
    return decorator

def handler(signum, frame):
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(alarm_id, "操作超时！"));

def handle_exit_signal(signum, frame):
    global group_ids
    for gid in group_ids:
        # requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, "下线了喵～"));
        pass
    exit(0)

def _excute(mode, user_msg, gid):
    alarm=alarm_dict[mode]
    msg=user_msg[len(mode)+1:]
    signal.alarm(alarm);
    try:
        print(f"{func_dict[mode].__name__}({msg}, {gid})\ntimeout: {alarm}");
        func_dict[mode](msg, gid);
        signal.alarm(0);
    except Exception as e:
        alarm_id = gid
        signal.alarm(0);

@register_func(name="restart", alarm=60)
def restart(msg, gid):
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, "正在重启..."));
    python=sys.executable;
    py_argv=copy.deepcopy(sys.argv);
    print(*py_argv);
    for argv in py_argv:
        if "_key" in argv:
            py_argv[py_argv.index(argv)+1]="***";
    py_argv="python "+" ".join(py_argv);
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, py_argv));
    os.execl(python, python, *sys.argv);

@register_func(name="keychange", alarm=10)
def keychange(keymsg, gid):
    keytype, key = keymsg.split(" ")
    try:
        args.__setattr__(f'{keytype}_key', key)
        msg = f"更改{keytype}_key为{key}"
    except:
        msg = "更改失败！"
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, msg))

@register_func(name="chat", alarm=120)
def chat(user_message, gid):
    global msg;
    user_msg_dict={
        "role": "user",
        "content": user_message
    };
    msg[gid].append(user_msg_dict);

    # 结构化数据并进行提交
    completion = openai.ChatCompletion.create(
        # max_tokens = 2,           # 默认inf 最大令牌数
        presence_penalty = 0,       # 惩罚机制，-2.0 到 2.0之间，默认0，数值越小提交的重复令牌[>
        frequency_penalty = 0,      # 意义和值基本同上，默认0，主要为频率
        temperature = 1.0,          # 温度 0-2之间，默认1  调整回复的精确度使用
        n = 1,                      # 默认条数1
        user = "user",              # 用户ID，用于机器人区分不同用户避免多用户时出现混淆
        model = "gpt-3.5-turbo",    # 这里注意openai官方有很多个模型
        messages = msg[gid]
    )
    assi_msg = completion.choices[0].message.content    # chatGPT返回的数据
    assi_msg_dict={
        "role": "assistant",
        "content": assi_msg
    };
    msg[gid].append(assi_msg_dict);

    if len(msg[gid])>10:
        msg[gid] = msg[gid][2:]

    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, assi_msg));

    return;

@register_func(name="setu", alarm=60)
def setu(keyword, gid):
    id=search_pic(keyword);
    if id==-1:
        requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message=已经没有好看的图啦！".format(gid));
        return;
    else:
        path=download_pic(id);
        send_pic(gid, path);

@register_func(name="scholar", alarm=1200)
def scholar(sch_args, gid):
    if args.use_proxy:
        sch_args+=f" --http_proxy {args.proxy_addr}";
        sch_args+=f" --https_proxy {args.proxy_addr}";
    else:
        sch_args+=f" --no_proxy";
    if " --not_save" not in sch_args:
        sch_args+=" --not_save";
    sch_msg=f"传入指令为\'{sch_args}\'";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, sch_msg));
    sch_msg="正在搜索喵～";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, sch_msg));
    try:
        sch_msg=bot_api(sch_args);
    except:
        sch_msg="检索失败了喵！";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, sch_msg));
    return;

@register_func(name='generate', alarm=180)
def generate(prompt, gid):

    save_dir = "generate"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    generated_imgs = os.listdir(save_dir)
    while len(generated_imgs) > 100:
        os.remove(save_dir + '/' + generated_imgs[-1])
        generated_imgs.pop()

    base_prompt = ', ((masterpiece)), (super delicate),(illustration),(extremely delicate and beautiful),(dynamic angle), (beautiful and delicate eyes), (clear hand details), looking at viewers DSLR photography, sharp focus, Unreal Engine 5, Octane Render, Redshift, ((cinematic lighting)), f/1.4, ISO 200, 1/160s, 8K, RAW, unedited, symmetrical balance, in-frame'
    prompt += base_prompt
    try:
        headers = {"Content-Type": "application/json"}
        payload = {'key': args.stable_diffusion_key, 
                   'model_id': 'anything-v4', 
                   'prompt': prompt , 
                   'negative_prompt': 'painting, (extra fingers), (mutated hands), (poorly drawn hands), poorly drawn face, (deformed), ugly, blurry, bad anatomy, bad proportions, (extra limbs), cloned face, skinny, glitchy, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs, bad posture, (wrong human body), anime', 
                   'width': '1080', 'height': '1080', 'samples': '1', 
                   'num_inference_steps': '30', 'seed': None, 
                   'guidance_scale': 7.5, 'webhook': None, 'track_id': None}
        diffusion_url = "https://stablediffusionapi.com/api/v3/dreambooth"
        while True:
            try:
                response = requests.post(diffusion_url, headers=headers, data=json.dumps(payload))
                response_json = response.json()
                if response_json['status'] == 'success':
                    break
                elif response_json['status'] == 'processing':
                    diffusion_url = response_json['fetch_result']
            except:
                pass
        print(response.text)
        img_link = response_json['output'][0]
        img_path = os.path.join(save_dir, img_link.split('/')[-1])

        sr_url = "https://appyhigh-ai.p.rapidapi.com/rapidapi/enhancer/2k"
        sr_payload = {"source_url": img_link,
	               "filename": ""}
        sr_headers = {"content-type": "application/json",
	                  "X-RapidAPI-Key": args.x_rapid_key,
	                  "X-RapidAPI-Host": "appyhigh-ai.p.rapidapi.com"}
        while True:
            try:
                response = requests.post(url=sr_url, headers=sr_headers, json=sr_payload)
                response_json = response.json()
                if response_json['message'] == 'Accepted':
                    break
            except:
                pass
        ori_link = img_link
        img_link = response_json['data']['2k']['url']
        pre_ext = img_path.split('.')[-1]
        cur_ext = img_link.split('/')[-1].split('.')[-1]
        img_path = img_path.replace(pre_ext, cur_ext)
        
        while True:
            try:
                img = requests.get(img_link)
                with open(img_path, 'wb') as f:
                    f.write(img.content)
                if os.path.getsize(img_path)/1024 < 50:
                    img_link = ori_link 
                else:
                    break
            except:
                pass

        send_pic(gid, img_path);
        return
    
    except Exception as e:
        print(response_json)
        requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, f"生成失败了喵\n{response.text}"));

    return

@register_func(name='anime', alarm=60)
def anime(msg, gid):

    cfg = "./anime.json"
    with open(cfg, 'r') as f:
        anime = json.load(f)
    url = "https://nyaa.si/?p={page}"
    format = r"{raw_name}</a>\n\t\t\t\t</td>\n\t\t\t\t<td class=\"text-center\">\n\t\t\t\t\t<a href=\"/download/(\d+).torrent\"><i class=\"fa fa-fw fa-download\"></i></a>\n\t\t\t\t\t<a href=\"magnet:\?xt=urn:btih:(.+?)&amp"
    bd = {'(': '\(', ')': '\)', '[': '\[', ']': '\]'}

    EPISODE = anime['episode']
    if msg in anime['anime']:
        raw_name = anime['anime'][msg]
        for bdfh in bd:
            raw_name = raw_name.replace(bdfh, bd[bdfh])
        raw_name = raw_name.replace(EPISODE, '(\d+)')
        page = 1
        pattern = format.format(raw_name=raw_name)
        while True:
            page_url = url.format(page=page)
            m = requests.get(page_url)
            eps = re.findall(pattern, m.text)
            # print(eps)
            if len(eps) > 0:
                anime_msg = {'episode': eps[0][0], 
                            'view': eps[0][1], 
                            'magnet': eps[0][2]}
                print(anime_msg)
                break
            page += 1
        return_msg = "name: {}\nmagnet: {}".format(raw_name.replace('(\d+)', eps[0][0]), eps[0][2])
        print(return_msg)
        requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, return_msg));
    else:
        requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, f"{msg}不在搜索范围喵"));

def search_pic(keyword):
    if args.use_proxy:
        proxies={
            'http':args.proxy_addr,
            'https':args.proxy_addr
        };
    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 1000users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            try:
                with open("used.txt",mode="a") as f:
                    f.write(id+"\n");
            except:
                os.makedirs("used.txt");
                with open("used.txt",mode="a") as f:
                    f.write(id+"\n");
            return id;

    # 没有搜索到热门插画，降低搜索标准继续搜索
    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 500users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;

    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 100users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;

    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword;
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;
    
    return -1;

def _exists(id):
    usedIDtxt="";
    try:
        with open("used.txt",mode="r") as f:
            usedIDtxt=f.read();
    except:
        pass;
    usedIDList=usedIDtxt.split();

    flag=False;
    for used_id in usedIDList:
        if used_id==id:
            flag=True;
            break;
    
    if flag==True:
        return True;
    else:
        return False;

def download_pic(id):
    mainpage_url='http://www.pixiv.net';
    UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29';
    Headers={
        'Referer': mainpage_url,
        'User-Agent': UA,
        'Referer': 'https://www.pixiv.net/'
    };
    if args.use_proxy:
        proxies={
            'http':args.proxy_addr,
            'https':args.proxy_addr
        };

    showurl="https://www.pixiv.net/artworks/"+id;
    if args.use_proxy:
        r=requests.get(showurl, headers=Headers, proxies=proxies);
    else:
        r=requests.get(showurl, headers=Headers);
    html=r.text;
    
    comp=re.compile(r'"original":"(?P<picurl>.*?)"},"tags":.*?',re.S);
    res=comp.finditer(html);
    fullpicurl="";
    for i in res:
        fullpicurl=i.group("picurl");
    if args.use_proxy:
        r=requests.get(url=fullpicurl, headers=Headers, proxies=proxies);
    else:
        r=requests.get(url=fullpicurl, headers=Headers);
    if(r.status_code!=200):
        return -1;
    
    mode=fullpicurl.split(".")[-1];
    path="";
    if mode=="jpg":
        path="img/"+str(id)+".jpg";
    elif mode=="png":
        path="img/"+str(id)+".png";
    else:
        print("Invalid image type!");
        exit();
    
    with open(path, mode="wb") as f:
        f.write(r.content);

    return path;

def send_pic(gid, path):
    dir=os.getcwd();
    path="file:///{}/{}".format(dir, path);
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message=[CQ:image,file={},id=40000]".format(gid, path));
    return;

def handle(gid, message):
    global group_ids
    if gid in group_ids:   # 目前只向特定群提供服务
        if "[CQ:at,qq={}]".format(args.qq_id) in message:  # 呼出bot
            user_msg=message.replace("[CQ:at,qq={}] ".format(args.qq_id), ""); # 切掉信头

            mode=user_msg.split(" ")[0];
            if user_msg=="chat clear":       # 清除chatGPT上下文指令
                    global msg;
                    msg[gid] = [];
                    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, "已清除上下文"));
                    return;
            if mode in func_dict:
                _excute(mode, user_msg, gid)
                return;

            requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(gid, 
            "这里是chatNEKO喵，使用方法：\n\n" + 
            "1. chatGPT聊天\n   @chatNEKO chat *聊天内容*\n\n" + 
            "2. 清除chatGPT上下文并开始新会话\n   @chatNEKO chat clear\n\n" + 
            "3. pixiv插画搜索\n   @chatNEKO setu *关键词*\n\n" + 
            "4. Google Scholar 快速检索\n   @chatNEKO scholar *搜索指令*，用法请参考search_researchers/README.md\n\n" + 
            "5. Stable Diffusion 生成插画\n   @chatNEKO generate *关键词*\n\n" + 
            "6. nyaa动画种子搜索\n   @chatNEKO anime *配置文件anime.json中的名字*\n\n" + 
            "7. 重启chatNEKO\n  @chatNEKO restart\n\n" + 
            "请注意，“@chatNEKO”标识符只有在手动键盘输入并选择用户时才能生效。直接从剪贴板粘贴“@chatNEKO”无效。同时@自带空格，无需手动输入。\n\n" + 
            "Github项目地址为 https://github.com/Antinis/chatNEKO 希望更多功能或建议请联系作者Antinis zhangyunxuan@zju.edu.cn\n\n快来跟我玩喵~"));

signal.signal(signal.SIGALRM, handler)
signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)
parser=argparse.ArgumentParser(description='test')
parser.add_argument('--qq_id', default=False, type=int, help='QQ id of the bot')
parser.add_argument('--group_ids', default=False, type=str, help='Which QQ group do you want to arrange this bot?')
parser.add_argument('--openai_key', default=False, type=str, help='The key of OpenAI ChatGPT API')
parser.add_argument('--stable_diffusion_key', default=False, type=str, help='The key of Stable Diffusion API')
parser.add_argument('--x_rapid_key', default=False, type=str, help='The key of X-RapidAPI')
parser.add_argument('--use_proxy', default=False, type=bool, help='Whether to use proxy server? If you are using Chinese network service and you want to use pixiv illustration searching function, you may set this argument as True.')
parser.add_argument('--proxy_addr', default=False, type=str, help='The address and port of proxy server.')
args=parser.parse_args()

if args.openai_key:
    openai.api_key=args.openai_key;

global msg;
msg={};
group_ids = args.group_ids.split(',')

for group_id in group_ids:
    # requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(group_id, "chatNEKO 已启动"));
    msg.update({group_id:[]})

app.run(debug=False, host='127.0.0.1', port=5701);
