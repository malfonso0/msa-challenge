cmd?=up -d

build:
	docker build -t msa-api -f ./dockerfile .
compose:
	docker-compose -p msa-challenge -f ./docker-compose.yml $(cmd)
