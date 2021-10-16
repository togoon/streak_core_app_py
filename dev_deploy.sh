sudo apt-get update

#sudo apt-get install redis-server
#sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
#echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
#sudo apt-get update
#sudo apt-get install -y mongodb-org

# sudo apt-get install -y pip
sudo apt-get install -y python-pip

To install nginx refere nginx setup file

sudo apt-get install -y uwsgi
# 
# sudo apt-get install -y nginx-full
# sudo apt-get remove nginx nginx-common # Removes all but config files.

# sudo apt-get purge nginx nginx-common # Removes everything.

# sudo apt-get autoremove


# https://github.com/nginx/nginx.git
# REFERENCE LINK TO FOLLOW:

# wget http://nginx.org/download/nginx-1.10.1.tar.gz?_ga=2.211537877.1187780165.1511428081-2044216344.1510337863
# tar -xvf nginx-1.10.1.tar.gz\?_ga\=2.211537877.1187780165.1511428081-2044216344.1510337863
# cd nginx-1.10.1/
# # sudo nano ./configure
# ./configure --with-pcre=/home/ubuntu/ --with-http_stub_status_module


# wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.41.tar.gz
# tar -zxf pcre-8.41.tar.gz
# cd pcre-8.41
# ./configure
# make
# sudo make install

# cd ..
# wget http://zlib.net/zlib-1.2.11.tar.gz
# tar -zxf zlib-1.2.11.tar.gz
# cd zlib-1.2.11
# ./configure
# make
# sudo make install

# cd ..
# wget http://www.openssl.org/source/openssl-1.0.2k.tar.gz
# tar -zxf openssl-1.0.2k.tar.gz
# cd openssl-1.0.2k
# # ./Configure darwin64-x86_64-cc --prefix=/usr
# ./config
# make
# sudo make install

git clone https://github.com/StreakAI/streak_core_app.git


sudo apt-get install -y unzip

cd streak_core_app/
sudo cp ./nginx_config/dev_config/default /etc/nginx/sites-enabled/
sudo cp ./nginx_config/dev_config/default_subdomain /etc/nginx/sites-enabled/
sudo mkdir /etc/nginx/ssl
sudo cp ./nginx_config/dev_config/ssl/* /etc/nginx/ssl/
sudo chmod -R 600 /etc/nginx/ssl/
sudo service nginx restart

curl 127.0.0.1
curl https://127.0.0.1

sudo cp ./nginx_config/dev_config/uwsgi_config_prod.ini /etc/uwsgi/apps-enabled/ 
sudo pip install virtualenv==15.1.0 virtualenvwrapper==4.7.2

echo "export WORKON_HOME=~/ENV" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc

mkvirtualenv PROD

#source ~/ENV/DEV/bin/activate

sudo pip install --upgrade pip

sudo pip install -r requirements.txt
pip install -r requirements.txt

cd streak_core/
sudo python manage.py collectstatic --settings=streak_core.settings.production
sudo python manage.py migrate --settings=streak_core.settings.production

deactivate

uwsgi --ini /etc/uwsgi/apps-enabled/uwsgi_config_prod.ini 

#to install let's encrypt ssl certificate
#links https://certbot.eff.org/#ubuntutyakkety-nginx 
# https://letsencrypt.org/documents/LE-SA-v1.2-November-15-2017.pdf
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx 
sudo certbot --nginx


uwsgi /etc/uwsgi/apps-enabled/uwsgi_config.ini 
