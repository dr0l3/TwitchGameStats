# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 5000, host:5000
  config.vm.provision "shell", inline: <<-SHELL
     #General updates
	 sudo apt-get update
	 sudp apt-get install python-pip
	 #Install redis
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
	 #Install python redis-driver
	 sudo pip install redis
	 #install docker
	 sudo apt-get install docker-engine
	 sudo service docker start
   SHELL
end
