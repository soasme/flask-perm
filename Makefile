distribute_package:
	python setup.py sdist bdist_wheel

distribute_doc:
	python setup.py build_sphinx

distribute: clean distribute_package distribute_doc

upload_package:
	twine upload dist/*$(version)*

upload_doc:
	python setup.py upload_sphinx

upload: upload_package upload_doc

patch:
	bumpversion --verbose patch

clean:
	python setup.py clean --all
	rm -rf docs/_build/
