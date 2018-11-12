#!/bin/bash


echo '正在更新系统...'
apt update -y
apt upgrade -y
echo -e '系统更新完毕.\n'


echo '正在安装系统组件...'
BASIC='man gcc make sudo lsof ssh openssl tree vim'
EXT='dnsutils iputils-ping net-tools psmisc sysstat'
NETWORK='curl telnet traceroute wget'
LIBS='libbz2-dev libpcre3 libpcre3-dev libreadline-dev libsqlite3-dev libssl-dev zlib1g-dev'
SOFTWARE='git mysql-server zip p7zip apache2-utils'
apt install -y $BASIC $EXT $NETWORK $LIBS $SOFTWARE
apt autoremove
apt autoclean
echo -e '系统组件安装完毕.\n'


echo '正在安装 pyenv...'
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
echo -e 'pyenv 安装完毕.\n'


echo '正在配置 pyenv...'
echo '
# PyenvConfig
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
' >> $HOME/.bashrc
source $HOME/.bashrc
pyenv update
echo -e 'pyenv 配置完毕.\n'


echo '正在安装 Python 3.6'
pyenv install -v 3.6.6
pyenv global 3.6.6
echo -e 'Python 3.6 安装完毕.\n'


echo '正在安装 Python 包...'
cd `dirname $0`
pip install -U pip
pip install -r ../requirements.txt
cd -
echo -e 'Python 包安装完毕.\n'


echo '正在安装 Nginx...'
DIR=$PWD
cd /tmp/
wget 'http://nginx.org/download/nginx-1.14.0.tar.gz'
tar -xzf nginx-1.14.0.tar.gz
cd nginx-1.14.0
./configure
make
make install
cd ..
rm -rf nginx*
cd -
echo -e 'Nginx 安装完毕.\n'


echo '正在安装 Redis'
cd /tmp/
wget 'http://download.redis.io/releases/redis-4.0.11.tar.gz'
tar -xzf redis-4.0.11.tar.gz
cd redis-4.0.11
make && make install
cd -
echo -e 'Redis 安装完毕.\n'
