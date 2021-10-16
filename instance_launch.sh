#sh -c 'echo "export APP_ENV=staging" >> /home/ubuntu/.bashrc' 

#source /home/ubuntu/.bashrc

# sudo ansible-playbook -i localhost, /home/ubuntu/streak_core_app/deploy_scrips/coreapp.yml

# sudo sh -c 'sudo cat /home/ubuntu/streak_core_app/streak_core/streak_core/settings/production.py > /home/ubuntu/streak_core_app/streak_core/streak_core/settings/curr.py'

# sudo sh -c 'cat /home/ubuntu/streak_core_app/nginx_config/dev_config/uwsgi_config_prod.ini > /etc/uwsgi/apps-enabled/uwsgi_config_prod.ini'

# sudo supervisorctl restart coreapp


#!/bin/bash
sudo ansible-playbook -i localhost, /home/ubuntu/streak_core_app/deploy_scrips/coreapp.yml

sudo sh -c 'cat /home/ubuntu/streak_core_app/streak_core/streak_core/settings/production.py > /home/ubuntu/streak_core_app/streak_core/streak_core/settings/curr.py'

sudo sh -c 'cat /home/ubuntu/streak_core_app/nginx_config/dev_config/uwsgi_config_prod.ini > /etc/uwsgi/apps-enabled/uwsgi_config_prod.ini'

sudo supervisorctl restart coreapp