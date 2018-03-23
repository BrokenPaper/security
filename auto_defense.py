# coding=utf-8
# 修改密码,移除后门,移除后门账号,网站加固,端口白名单

from optparse import OptionParser
import pexpect

parser = OptionParser()
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

res = child.expect(['continue connecting (yes/no)?', '[p|P]assword:', pexpect.TIMEOUT], timeout=10)

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

# 不要留下命令历史记录
child.sendline(' set +o history')

# 获取所有后门端口,为之后的攻击做准备
# awk会输出 0.0.0.0:8080 ,sed的作用是获取后面的8080
child.sendline('''
netstat -anpt | grep autorun | awk '{print $4}' |  sed 's/.*:\(.*\)/\1/g' | xargs -I % echo % >> /root/port.txt
''')

# 关闭所有后门
child.sendline('''ps -ef | grep autorun | grep -v grep | awk '{print $2}' | xargs kill -9  ''')

# 测试用,以后会改成复杂的密码
child.sendline('echo root:123456 | chpasswd ')

# 首先把网站里所有文件复制到 /root/website
# 然后将所有文件置空,一般都是直接删除文件的,比赛的规则可能变了所以不直接删
# 最后禁止修改这些文件
child.sendline('''
cd /var/www/html ;
\cp -rf . /root/website ;
find . -type f | awk {'system("cat /dev/null > "$0)'};
chattr +i -R .
 ''')

# 找出除了root以外可以登录shell的用户,输出到 /root/user.txt 文件后删除这些用户
child.sendline('''
cat /etc/passwd | grep -v '^root' |grep -E '/bin/(bash|sh)'|awk -F ':' '{print $1}'| 
xargs -I % sh -c 'echo % >> /root/user.txt ; userdel -fr %'           
''')

# 这个能找出UID大于500的,不一定准确
# child.sendline('''cat /etc/passwd | awk -F ':' '{if ($3>=500) print $1}' | xargs -I {} userdel -fr {}''')


# 可能会导致本程序无法第二次连接,不过已经加固好了就没必要再次连接了
child.sendline('iptables -P INPUT DROP')
child.sendline('iptables -A INPUT -m multiport -p tcp --dport 21,22,23,80 -j ACCEPT')
child.sendline('service iptables save && service iptables restart')

child.sendline('exit')
child.expect(pexpect.EOF)

print 'Finished'

# 完成后可以查看 /root/ports.txt 获得所有后门端口
# 查看 /root/users.txt 获得所有后门账号
