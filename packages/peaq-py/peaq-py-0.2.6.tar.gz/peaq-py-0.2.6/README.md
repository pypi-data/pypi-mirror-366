# peaq-py
Follow documentation for detailed overview of feature and functionalities of peaq SDK.

# TODO
1. Use the OO structure
2. Think about the test cases because some of them tested in the peaq-bc-test
3. Add the SDK documentation

# How to publish
rm -rf build dist
python setup.py sdist bdist_wheel
twine upload dist/*
