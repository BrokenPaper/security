# coding=utf-8
import requests
from optparse import OptionParser
import re

url = 'http://192.168.1.100/lms/portal/sp/hz_flag.php'


# 修改为自己登陆后获取到的Cookie


def commit_flag(target_host, target_flag, header):
    res = requests.post(url=url, data={'melee_ip': target_host, 'melee_flag': target_flag}, headers=header)
    return True if re.search(u'成功', res.content) else False


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-t', dest='target', type='string')
    parser.add_option('-f', dest='flag', type='string')

    (options, args) = parser.parse_args()
    header = {
        'cookie': 'SSCSum=39; zlms-sid=olm0tcq4ejtmdrka17vs1rdo85; webcs_test_cookie=lms_cookie_checker; lms_login_name=HZ8'
    }
    commit_flag(options.target, options.flag, header)
