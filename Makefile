all: picam/cmaths.pyx
	python setup.py build_ext --inplace

clean:
	rm -rf build picam/cmaths.c*
