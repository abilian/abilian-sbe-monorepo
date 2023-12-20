#!/bin/sh

mkdir -p "${HOME}"/Maildir/{cur,new,tmp}
chmod 0700 "${HOME}"/Maildir/{cur,new,tmp}

mkdir -p ./src/instance

#clamav_db: sudo /etc/init.d/clamav-freshclam start
#clamav_server: sudo /etc/init.d/clamav-daemon start

flask assets build
#tailwind: flask tailwind start

flask initdb
flask createuser --role admin --name admin ${ADMIN_MAIL} ${ADMIN_PASSWORD}
