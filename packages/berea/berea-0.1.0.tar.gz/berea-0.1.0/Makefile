benchmark:
	hyperfine --warmup 3 'bible Genesis 3 3'

build:
	hatch build

clean:
	hatch clean dist

publish-test:
	hatch publish --repo test

install-test:
	pip install -i https://test.pypi.org/simple/ berea