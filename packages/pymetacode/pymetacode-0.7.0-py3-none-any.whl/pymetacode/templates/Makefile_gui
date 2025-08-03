UIC = pyside6-uic
UI_DIR := ./ui

UI_FILES := $(shell find $(UI_DIR) -name '*.ui')
UIPY_FILES := $(UI_FILES:.ui=.py)

all: uic

uic: $(UIPY_FILES)

$(UIPY_FILES): $(UI_DIR)/%.py: $(UI_DIR)/%.ui
	$(UIC) $< -o $@
