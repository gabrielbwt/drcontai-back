start:
	uvicorn app.main:app --reload

test:
	PYTHONPATH=$(PWD) pytest

install:
	pip install -r requirements.txt

update requirements:
	pip freeze > requirements.txt