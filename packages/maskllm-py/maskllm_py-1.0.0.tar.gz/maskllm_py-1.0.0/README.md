Run `docker-compose up` to start a local pypi server then in the project you can use

# Download and install hosted packages.

pip install --extra-index-url http://localhost:8082 maskllm_py

# Note that pip search does not currently work with the /simple/ endpoint.

To generate the dist , run

`python setup.py sdist`

For documentation

Will build `make html`
Will watch `sphinx-autobuild source build/html`


