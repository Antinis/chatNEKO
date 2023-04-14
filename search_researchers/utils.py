import time, datetime
from scholarly import scholarly
import sys, os
import pandas as pd
import argparse


GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def init_opts(opts=None):

    parser = argparse.ArgumentParser(description='Google Scholar Crawler')

    parser.add_argument('--orgs', type=str, default='zju,tokyo', 
                        help='Organizations, use \',\' to split, eg: \'zju,tokyo\'')
    parser.add_argument('--no_proxy', action='store_true', help='Do not use proxy')
    parser.add_argument('--http_proxy', type=str, default='127.0.0.1:1080', 
                        help='The http proxy address, eg: 127.0.0.1:1080')
    parser.add_argument('--https_proxy', type=str, default='127.0.0.1:1080', 
                        help='The https proxy address, eg: 127.0.0.1:1080')
    parser.add_argument('--interests', type=str, default='Computer_Vision,Machine_Learning', 
                        help='The research fields, use \',\' to split, eg: Computer_Vision,Machine_Learning')
    parser.add_argument('--min_cit', type=int, default=500, help='Minimum number of citations')
    parser.add_argument('--not_save',action='store_true', help='Do not save results')

    if opts is None:
        opt = parser.parse_args()
    else: 
        opt = parser.parse_args(opts)
    opt.interests = opt.interests.replace('_', ' ').split(',')
    if opt.no_proxy:
        opt.http_proxy = ''
        opt.https_proxy = ''
        print(YELLOW + 'No proxy!!!' + RESET)
    return opt


def search_by_org(org_id, Org, tmporg, opt, infos, results):

    result = scholarly.search_author_by_organization(organization_id=org_id)
    affiliation = []
    info = pd.DataFrame({'Name':[], 'Affiliation':[], 'Interests':[], f'citedby({opt.min_cit})':[]})
    start = datetime.datetime.now()
    i = 0
    
    while True:

        elapse = datetime.datetime.now() - start
        info_msg = info.to_string()
        num = str(len(affiliation))
        msg = RED + '\n' + 'Searching ' + GREEN + f'{tmporg}...' + RESET + '\n' + \
              'Start  Time:  ' + start.strftime('%Y-%m-%d %H:%M:%S') + '\n' + \
              'Elapse Time:  ' + str(elapse) + '\n' + \
              f'Found {num} in {i}' + '\n' + \
              info_msg.index('\n') * '-' + '\n' + info_msg + '\n' * 3
        sys.stdout.write(msg)
        sys.stdout.flush()
        time.sleep(1e-2)

        try:
            author = next(result)
            i += 1
            if author['citedby'] < opt.min_cit:
                break
            interests = ' & '.join(set([i.lower() for i in opt.interests]) & set([j.lower() for j in author['interests']]))
            if interests == '':
                continue
            else:
                affiliation.append(author['affiliation'])
                new_info = {'Name':author['name'], 'Affiliation':author['affiliation'], 
                            'Interests':interests, f'citedby({opt.min_cit})':author['citedby']}
            info = info.append(new_info, ignore_index=True)
        except:
            break

    results['institution'].append(tmporg)
    results['researchers'].append(msg)
    infos.append(info)
    print(f'Found {num} in total!')

    if num != '0'and not opt.not_save:
        affiliation = min(affiliation, key=len)
        save_dir = os.path.join(Org, affiliation)
        for interest in opt.interests:
            save_dir += '_{}'.format(interest.replace(' ', '')) if interest != '' else ''
        while os.path.exists(save_dir + '_' + str(opt.min_cit) +'.xls'):
            save_dir += '_'
        save_dir = save_dir + '_' + str(opt.min_cit) +'.xls'
        info.to_excel(save_dir)
        print(f'Saving results to {save_dir}')


def extract_names(info, inst):

    names = ' & '.join([name for name in info['Name']])

    return f'{inst}\n{names}\n\n'