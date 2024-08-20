cmd?=up -d

build:
	docker build -t msa-api -f ./dockerfile .
compose:
	docker-compose -f ./docker-compose.yml $(cmd)
