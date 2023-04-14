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
