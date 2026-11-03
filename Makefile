#
# ModularService (App-ModularPipeline) - BV-BRC dev_container module Makefile.
#
# Normal use: check this repo out as dev_container/modules/ModularService, source the dev_container
# user-env.sh, then:
#     make                      # dev-container wrappers in $(KB_TOP)/bin (App-ModularPipeline, modpipe)
#     make deploy-service       # install into $(TARGET) (default /kb/deployment)
#     make test                 # unit tests (no container needed)
# Outside dev_container/modules, point TOP_DIR at the dev container:  make TOP_DIR=/path/to/dev_container ...
#
SHELL := /bin/bash
TOP_DIR ?= ../..
include $(TOP_DIR)/tools/Makefile.common

# Python scripts are Python 3 (Makefile.common defaults to the python2 wrapper)
WRAP_PYTHON_TOOL = wrap_python3
WRAP_PYTHON_SCRIPT = bash $(TOOLS_DIR)/$(WRAP_PYTHON_TOOL).sh

SERVICE = modular_pipeline
APP_SERVICE = app_service

DEPLOY_RUNTIME ?= /kb/runtime
TARGET ?= /kb/deployment

SRC_PYTHON = $(wildcard scripts/*.py)
SRC_SERVICE_PERL = $(wildcard service-scripts/*.pl)
BIN_SERVICE_PERL = $(addprefix $(BIN_DIR)/,$(basename $(notdir $(SRC_SERVICE_PERL))))
BIN_PYTHON = $(addprefix $(BIN_DIR)/,$(basename $(notdir $(SRC_PYTHON))))

# Data the engine reads at run time (util._find_root: $KB_TOP/services/modular_pipeline when deployed).
DATA_DIRS = modules types resources pipelines
DATA_FILES = reference/tools/index.json reference/workspace_types_known.json

PYTHON ?= python3

all: bin

bin: $(BIN_SERVICE_PERL) $(BIN_PYTHON)

# Dev-container wrapper for the CLI: points at this checkout's lib/ and data.
$(BIN_DIR)/modpipe: scripts/modpipe.py $(TOP_DIR)/user-env.sh
	export KB_PYTHON_PATH=$(CURDIR)/lib; \
	$(WRAP_PYTHON3_SCRIPT) '$(CURDIR)/scripts/modpipe.py' $@

deploy: deploy-all
deploy-all: deploy-service
deploy-client: deploy-libs deploy-scripts

deploy-service: deploy-dirs deploy-libs deploy-scripts deploy-service-scripts deploy-specs deploy-data

deploy-dirs:
	mkdir -p $(TARGET)/bin $(TARGET)/lib $(TARGET)/plbin $(TARGET)/pybin $(SERVICE_DIR) $(TARGET)/services/$(APP_SERVICE)

# deploy-specs comes from Makefile.common.rules (rsync app_specs -> services/app_service/)

deploy-data:
	for d in $(DATA_DIRS); do mkdir -p $(SERVICE_DIR)/$$d && rsync -a --delete --exclude '*.bak*' $$d/ $(SERVICE_DIR)/$$d/; done
	for f in $(DATA_FILES); do mkdir -p $(SERVICE_DIR)/`dirname $$f` && cp $$f $(SERVICE_DIR)/$$f; done
	date -u +%Y-%m-%dT%H:%M:%SZ > $(SERVICE_DIR)/DEPLOYED_AT

deploy-docs:

# Checks (host python with PyYAML + Jinja2, or inside the container)
test:
	$(PYTHON) -m unittest discover -s tests/unit

lint:
	$(PYTHON) bin/modpipe lint --quiet
	$(PYTHON) tools/check_types.py --quiet
	for p in pipelines/*.json; do $(PYTHON) bin/modpipe validate $$p | tail -1; done

check: lint test

clean:

include $(TOP_DIR)/tools/Makefile.common.rules
