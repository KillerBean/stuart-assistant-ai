#!/bin/bash

# Atualiza os requisitos do projeto Stuart AI
pip freeze | sort > requirements-sorted.txt
sort requirements.txt -o requirements.txt
comm -13 requirements.txt requirements-sorted.txt > requirements-sorted-exclusive.txt
cat requirements.txt requirements-sorted-exclusive.txt | grep -v 'setuptools' | grep -v 'pip-tools' | sort > requirements-updated.txt
mv requirements-updated.txt requirements.txt
rm requirements-sorted.txt requirements-sorted-exclusive.txt
pip-compile -v --output-file=requirements-compiled.txt requirements.txt
