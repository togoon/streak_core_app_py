sudo apt-get update

#sudo apt-get install redis-server
#sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
#echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
#sudo apt-get update
#sudo apt-get install -y mongodb-org

sudo apt-get install -y pip
sudo apt-get install -y python-pip
sudo apt-get install -y uwsgi
sudo apt-get install -y nginx
sudo apt-get install -y unzip

sudo cp ./nginx_config/dev_config/default_1 /etc/nginx/sites-enabled
sudo cp ./nginx_config/dev_config/default /etc/nginx/sites-enabled
sudo mkdir /etc/nginx/ssl
sudo cp ./nginx_config/dev_config/ssl/* /etc/nginx/ssl/
sudo chmod -R 600 /etc/nginx/ssl/
sudo service nginx restart

sudo cp ./nginx_config/dev_config/uwsgi_config.ini /etc/uwsgi/apps-enabled/ 
sudo pip install virtualenv==15.1.0 virtualenvwrapper==4.7.2

echo "export WORKON_HOME=~/ENV" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc

mkvirtualenv DEV

#source ~/ENV/DEV/bin/activate

sudo pip install --upgrade pip

sudo pip install -r requirements.txt
pip install -r requirements.txt

cd streak_core/
sudo python manage.py collectstatic --settings=streak_core.settings.dev
sudo python manage.py migrate --settings=streak_core.settings.dev

deactivate

uwsgi --ini /etc/uwsgi/apps-enabled/uwsgi_config.ini