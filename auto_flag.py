# coding=utf-8
import requests
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-t', dest='target', type='string')
parser.add_option('-f', dest='flag', type='string')

(options, args) = parser.parse_args()

url = 'http://192.168.1.100/lms/portal/sp/hz_flag.php'
cookie = 'SSCSum=39; zlms-sid=olm0tcq4ejtmdrka17vs1rdo85; webcs_test_cookie=lms_cookie_checker; lms_login_name=HZ8'
header = {
    'cookie': cookie
}

target_ip = options.target
target_flag = options.flag

response = requests.post(url=url, data={'melee_ip': target_ip, 'melee_flag': target_flag},
                         headers=header)
content = response.content
#print content
import re

if re.search(u'成功', content):
    print '%s 提交成功' % target_ip
else:
    print '%s 提交失败' % target_ip
