VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;
COMPONENT_NAME = myrt_desk

configure:
	rm -rf "$(VENV_PATH)"
	python3.12 -m venv "$(VENV_PATH)"
	$(VENV) pip install -r requirements.txt

clean:
	rm -rf venv

lint:
	$(VENV) pylint custom_components/
	$(VENV) ruff check ./custom_components
