sudo apt-get update
sudo apt-get install -y python-pip

sudo apt-get install -y uwsgi

sudo apt-get install -y unzip

sudo pip install virtualenv==15.1.0 virtualenvwrapper==4.7.2

sudo pip install virtualenv==15.1.0 virtualenvwrapper==4.7.2

echo "export WORKON_HOME=~/ENV" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc

mkvirtualenv PROD

cd streak_core/
sudo python manage.py collectstatic --settings=streak_core.settings.crypto_dev

sudo python manage.py migrate --settings=streak_core.settings.crypto_dev