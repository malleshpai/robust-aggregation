PYTHONPATH := src

.PHONY: run baseline tables check-paper final check-final test all

run:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/run_pipeline.py

baseline:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/build_baseline.py

tables:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/build_paper_tables.py

check-paper:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/check_against_paper.py

final:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/reproduce_final_paper.py

check-final:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/check_final_paper.py

test:
	PYTHONPATH=$(PYTHONPATH) python3 -m unittest discover -s tests -v

all: baseline run tables check-paper final check-final test
