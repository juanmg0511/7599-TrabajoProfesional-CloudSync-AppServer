#!/usr/bin/env bash

#Operations for application database
echo '##MONGODB init script: creating application user and db'
mongo ${MONGODB_DATABASE} \
        --host localhost \
        --port 27017 \
        -u ${MONGO_INITDB_ROOT_USERNAME} \
        -p ${MONGO_INITDB_ROOT_PASSWORD} \
        --authenticationDatabase admin \
        --eval "db.createUser({user: '${MONGO_NON_ROOT_USERNAME}', pwd: '${MONGO_NON_ROOT_PASSWORD}', roles:[{role:'dbOwner', db: '${MONGODB_DATABASE}'}]});"

#Operations for logs database
echo '##MONGODB init script: creating logs user and db'
mongo ${MONGODB_LOG_DATABASE} \
        --host localhost \
        --port 27017 \
        -u ${MONGO_INITDB_ROOT_USERNAME} \
        -p ${MONGO_INITDB_ROOT_PASSWORD} \
        --authenticationDatabase admin \
        --eval "db.createUser({user: '${MONGO_NON_ROOT_USERNAME}', pwd: '${MONGO_NON_ROOT_PASSWORD}', roles:[{role:'dbOwner', db: '${MONGODB_LOG_DATABASE}'}]});"
