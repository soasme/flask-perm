dist:
	python setup.py sdist bdist_wheel
	python setup.py build_sphinx

upload:
	twine upload dist/*$(version)*
	python setup.py upload_sphinx

patch:
	bumpversion --verbose patch
