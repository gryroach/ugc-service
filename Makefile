include .env

# Запуск всех контейнеров
run-all:
	docker compose up -d --build

# Запуск API-сервиса
run-api:
	docker compose up -d nginx ugc-api

# Запуск MongoDB
run-mongo:
	docker compose up -d --build mongors1n1 mongors1n2 mongors1n3 mongors2n1 mongors2n2 mongors2n3 mongocfg1 mongocfg2 mongocfg3 mongos1 mongos2

# Инициализация шардов MongoDB
init-db:
	@echo "Initializing MongoDB configuration..."
	docker compose exec mongocfg1 mongosh --eval 'load("/docker-entrypoint-initdb.d/init-config.js")'
	@echo "Initializing MongoDB shard 1..."
	docker compose exec mongors1n1 mongosh --eval 'load("/docker-entrypoint-initdb.d/init-shard1.js")'
	@echo "Initializing MongoDB shard 2..."
	docker compose exec mongors2n1 mongosh --eval 'load("/docker-entrypoint-initdb.d/init-shard2.js")'
	@echo "Initializing MongoDB mongos..."
	@echo "Waiting for shards to initialize..."
	@sleep 15
	docker compose exec mongos1 mongosh --eval 'load("/docker-entrypoint-initdb.d/init-mongos.js")'
	@echo "Initialization complete!"

create-dbuser:
	@echo "Creating MongoDBs user..."
	docker compose exec mongos1 mongosh --eval 'db.getSiblingDB("admin").createUser({ user: "$(UGC_MONGO_USER)" , pwd: "$(UGC_MONGO_PASSWORD)", roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]})'
