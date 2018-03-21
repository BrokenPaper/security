# coding=utf-8
import requests
from optparse import OptionParser
import re

url = 'http://192.168.1.100/lms/portal/sp/hz_flag.php'

# 修改为自己登陆后获取到的Cookie
header = {
    'cookie': 'SSCSum=39; zlms-sid=olm0tcq4ejtmdrka17vs1rdo85; webcs_test_cookie=lms_cookie_checker; lms_login_name=HZ8'
}


def commit_flag(target_host, target_flag):
    try:
        res = requests.post(timeout=3, url=url, data={'melee_ip': target_host, 'melee_flag': target_flag}, headers=header)
        print '[√] 已成功提交Flag值' if re.search(u'成功', res.content) else '[X] 提交Flag值失败'
    except:
        print '[X] 提交过程中发生了错误'

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-t', dest='target', type='string')
    parser.add_option('-f', dest='flag', type='string')

    (options, args) = parser.parse_args()

    commit_flag(options.target, options.flag)
