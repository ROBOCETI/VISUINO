Assuming that the sphinx scripts ARE on the PATH enviroment variable (for instance, through 'C:\PythonXX\scripts' on Windows machines), you can:

(i) Generate the docs with:

> make clean
> make html

(ii) Update the whole api documentation with:

> sphinx-apidoc -f -o . ../visuino ../visuino/resources