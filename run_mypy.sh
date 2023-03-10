export MYPYPATH=./tests/functional
cd tests/functional
mypy --strict --explicit-package-bases .
cd ../..

export MYPYPATH=./etl
cd etl
mypy --strict --explicit-package-bases .
cd ..

export MYPYPATH=./fastapi-solution/src
cd fastapi-solution/src
mypy --strict --explicit-package-bases .
