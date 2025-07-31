.PHONY : dist
dist: setup.py
	python3 -m build --sdist --wheel
	auditwheel repair -w dist dist/EXtra_redu-*-linux_x86_64.whl --plat manylinux2014_x86_64
	rm dist/EXtra_redu-*-linux_x86_64.whl

.PHONY : upload-test
upload-test:
	python -m twine upload --repository testpypi dist/*

.PHONY : upload
upload:
	python -m twine upload dist/*

.PHONY : clean
clean:
	rm -rf build dist
