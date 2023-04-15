import warnings
from scholarly import scholarly
import sys, os
import shlex

from .utils import *

### 
def main(opt):

    results = {'institution':[], 'researchers':[]}
    infos = []

    os.environ['http_proxy'] = opt.http_proxy
    os.environ['https_proxy'] = opt.https_proxy
    os.system('curl ipinfo.io')

    Orgs = opt.orgs.split(',')
    print(RED + '\n' + 'Start researching!' + RESET)
    rst = ''

    for Org in Orgs:
        print(RED + 'Start searching ' + GREEN + Org + RESET)
        if not os.path.exists(Org) and not opt.not_save:
            os.makedirs(Org)
        try:
            orgs = scholarly.search_org(Org)
            for org in orgs:
                print(RED + 'Start searching ' + GREEN + org['Organization'] + RESET)
                search_by_org(int(org['id']), Org, org['Organization'], opt, infos, results)
        except:
            rst = 'Cannot Fetch from Google Scholar!\nMaybe there is something wrong with the proxy settings！'
            break
    
    for i in range(len(results['researchers'])):
        print(results['researchers'][i])
        rst += extract_names(infos[i], results['institution'][i])
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''

    print(rst)
    return rst

def bot_api(args):

    args = shlex.split(args)
    opt = init_opts(args)
    msg = main(opt)

    return msg

if __name__ == '__main__':

    if not sys.warnoptions:
        warnings.simplefilter("ignore")

    opt = init_opts()
    print(opt)

    main(opt)
