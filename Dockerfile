FROM ubuntu:latest

RUN apt-get update
RUN apt-get -y install rsyslog
RUN apt-get -y install cron
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip3 install redis

ENV dbAddress=redis_twitch

ADD crontab /etc/cron.d/hello-cron
ADD start-cron.sh /usr/bin/start-cron.sh
ADD updateDatabaseWithDailyUpdates.py /usr/bin/updateDatabaseWithDailyUpdates.py
ADD updateDatabaseWithHourlyUpdates.py /usr/bin/updateDatabaseWithHourlyUpdates.py
ADD getviewersandsavetodb.py /usr/bin/getviewersandsavetodb.py
RUN chmod +x /usr/bin/start-cron.sh
RUN chmod 600 /etc/cron.d/hello-cron
RUN touch /var/log/cron.log

CMD /usr/bin/start-cron.sh