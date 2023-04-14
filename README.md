# chatNEKO
## English Description
QQ group bot, chat with ChatGPT, and search for pixiv illustrations.
## Usage
1. tmux # start a new tmux session
2. cd cqhttp && chmod +x go-cqhttp
3. ./go-cqhttp # launch go-cqhttp and login with your own bot account
4. press ctrl+b, then press d # quit from tmux window and keep this tmux session running in the backend
5. tmux # start another new tmux session
6. cd ..  # go back to the root dir of this project
7. python backend.py [--qq_id QQ_ID] [--group_id GROUP_ID] [--openai_key OPENAI_KEY] [--use_proxy USE_PROXY] [--proxy_addr PROXY_ADDR]

If you have any question on the usage of paramters, use python backend.py -h to see the help.

## 中文介绍
这是一个QQ聊天机器人，可以与ChatGPT聊天，并可以搜索pixiv的插画。
## 使用方法
1. tmux # 启动一个新的tmux窗口
2. cd cqhttp && chmod +x go-cqhttp
3. ./go-cqhttp # 启动go-cqhttp，并按照提示登陆bot账号
4. press ctrl+b, then press d # 退出tmux窗口并保持该进程在后台运行
5. tmux # 启动另一个新的tmux窗口
6. cd ..  # 回到这个工程的根目录
7. python backend.py [--qq_id QQ_ID] [--group_id GROUP_ID] [--openai_key OPENAI_KEY] [--use_proxy USE_PROXY] [--proxy_addr PROXY_ADDR]

如果对 backend.py 的命令行参数有任何疑问，请使用 python backend.py -h 命令查看帮助。

## REFERENCES
https://github.com/Mrs4s/go-cqhttp
