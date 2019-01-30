
.PHONY: clean
clean:
	-rm -rf build dist *.egg-info htmlcov .eggs

minor:
	bumpversion minor

major:
	bumpversion major

patch:
	bumpversion patch

publish:
	pip3 install wheel twine
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

upload: clean publish
