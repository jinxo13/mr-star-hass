VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;
COMPONENT_NAME = myrt_desk
VERSION = 0.1.0

.PHONY: configure
configure:
	rm -rf "$(VENV_PATH)"
	python3.12 -m venv "$(VENV_PATH)"
	$(VENV) pip install -r requirements.txt

.PHONY: clean
clean:
	@rm -rf venv

.PHONY: lint
lint:
	$(VENV) pylint custom_components/
	$(VENV) ruff check ./custom_components

.PHONY: publish
publish:
	@$(MAKE) lint
	git add Makefile
	git commit -m "chore: release $(VERSION)"
	git tag -a v$(VERSION) -m "release $(VERSION)"
	git push && git push --tags
