SRC = src
EXE = $(SRC)

VENV = .venv
PYTHON = $(VENV)/bin/python3

TRASH = $(SRC)/__pycache__ llm_sdk/__pycache__ __pycache__ $(VENV) .mypy_cache data/output .uv_cache

MYPY_FLAGS = --strict --no-error-summary

# ANSI codes
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[0;33m
BOLD = \033[1m

SUCCESS = \033[1;92m
RESET = \033[0m

install:
	@echo "$(BOLD)Initializing project environment:$(RESET)"

	@echo "$(YELLOW)Creating virtual environment...$(RESET)"
	uv venv $(VENV) --clear > /dev/null 2>&1
	@echo "$(GREEN)Virtual environment setup complete$(RESET)"

	UV_PROJECT_ENVIRONMENT="$(VENV)" \
	uv sync > /dev/null 2>&1 & pid=$$!; \


	@echo "\n$(GREEN)All dependencies successfully installed$(RESET)"
	@echo "\n$(SUCCESS)Project can now be run safely!$(RESET)"

run:
	uv run python -m $(EXE) run_all 1000 $(FLAGS)

lint:
	@echo "$(BOLD)Verifying project source code:$(RESET)"

	@echo "$(YELLOW)Running flake8...$(RESET)"
	@$(PYTHON) -m flake8 src
	@echo "$(GREEN)No norm errors found$(RESET)"

	@echo "\n$(YELLOW)Running mypy...$(RESET)"
	@$(PYTHON) -m mypy ./src $(MYPY_FLAGS)
	@echo "$(GREEN)No typing errors found$(RESET)"

	@echo "\n$(SUCCESS)Success: no errors found in source code!$(RESET)"

debug:
	uv run python -m src run_all 1000 
	chunking files...                                                                                                                              0%
	an error a occured NameError
	name 'chunk_size' is not defined
	$(PYTHON) -m pdb -m $(EXE) $(FLAGS)

clean:
	@echo "$(YELLOW)Initiating cleanup operation...$(RESET)"
	@found=0; \
	for i in $(TRASH); do \
		if [ -d "$$i" ]; then \
			echo " - Removed directory $(RED)'$$i'$(RESET)"; \
			found=1; \
		elif [ "$$i" ]; then \
			echo " - Removed file $(RED)'$$i'$(RESET)"; \
			found=1; \
		fi; \
	done; \
	if [ $$foundq 0 ]; then \
		echo "$(GREEN)Nothing to clean :)$(RESET)"; \
	fi
	@rm -rf $(TRASH)
	@echo "$(SUCCESS)\nCleanup complete!$(RESET)"

cache_clean:
	@echo "$(YELLOW)Initiating cache cleanup operation...$(RESET)"
	@echo "Deleting $(RED)$(UV_CACHE), $(HF_CACHE)$(RESET)"
	@rm -rf $(UV_CACHE_DIR) $(HF_CACHE_DIR)
	@echo "$(SUCCESS)\nCache cleanup complete!$(RESET)"