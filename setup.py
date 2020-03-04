import os

homeDir = os.path.expanduser('~')

if not os.path.exists(os.path.join(homeDir, 'MNDU2-2020Server/config')):
    os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/config'))
if not os.path.exists(os.path.join(homeDir, 'MMR-2019Server/assignments')):
    os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/assignments'))
if not os.path.exists(os.path.join(homeDir, 'MNDU2-2020Server/cache')):
    os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/cache'))
    os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams'))
    os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs'))
