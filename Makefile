DC=docker-compose -f docker-compose.yaml -f mongo-docker-compose.yaml -f redis-docker-compose.yaml -f minio-docker-compose.yaml

help: ## 지금 보고계신 도움말
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

prepare: ## 컨테이너 실행 전 준비
	$(DC) up -d mongodb-palm
	$(DC) up -d redis-palm
	$(DC) up -d minio-palm


build: # 이미지 빌드
	$(DC) build $(service)

build-no-cache: # 이미지 빌드 (캐시된 레이어 무시)
	$(DC) build $(service) --no-cache

down: ## 컨테이너 종료
	$(DC) down --remove-orphans

up: prepare ## 컨테이너 실행
	[[ -z "$(service)" ]] && { $(DC) up $$($(DC) config --services | grep -Ev '(mongo|minio|redis)'); true; } || $(DC) up $(service)

ps: ## 컨테이너 상태 확인
	$(DC) ps

rib:
	@[[ -z "$(service)" ]] && { echo "service=foo required"; exit 1; } || true
	$(DC) run --service-ports -it $(service) bash

sh: ## 컨테이너 쉘 접속
	@[[ -z "$(service)" ]] && { echo "service=foo required"; exit 1; } || true
	$(DC) exec -it $(service) bash

logs: ## 컨테이너 로그 확인
	$(DC) logs $(service)

format: ## 코드 포맷팅
	poetry run black . && poetry run isort .

deploy: ## 배포
	flyctl deploy --config fly.toml

clean: ## 불필요한 리소스 정리 (cache, ...)
	rm -rf `find . -name '__pycache__'`
	rm -rf `find . -name '*.pyc'`
	rm -rf `find . -name '.DS_Store'`
