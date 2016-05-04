# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  #The box to be used
  config.vm.box = "ubuntu/trusty64"
  # Port forwarding
  config.vm.network "forwarded_port", guest: 5000, host:5000
  
  #Shell commands
  config.vm.provision "shell", inline: <<-SHELL
     #General updates
	 sudo apt-get update
	 #sudo apt-get -y install python-pip
	 sudo apt-get -y install python3-pip
     
	 #install node.js
	 sudo apt-get -y install nodejs
	 sudo apt-get -y install npm
	 
	 #install npm libraries
	 sudo npm install highcharts
	 sudo npm install jquery
	 
	 #install redis
	 sudo apt-get install build-essential
	 sudo apt-get install tcl8.5
	 wget http://download.redis.io/releases/redis-stable.tar.gz
	 tar xzf redis-stable.tar.gz
	 cd redis-stable
	 make
	 make test
	 sudo make install
	 cd utils
	 sudo ./install_server.sh
	 cd ..
	 cd ..
	 
	 #Install redis-driver
	 #sudo pip install redis
	 sudo pip3 install redis
	 sudo npm install redis
	 
	 #install docker 
	 sudo apt-get -y install docker.io
	 sudo ln -sf /usr/bin/docker.io /usr/local/bin/docker
	 sudo sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io
	 sudo service docker.io restart
	 sudo docker run hello-world
	 adduser vagrant
	 usermod -aG docker vagrant
  SHELL
end
