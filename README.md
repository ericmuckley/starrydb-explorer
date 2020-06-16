# Hosted dashboard

This is a template for a dashboard with interactive plotting that is hosted online for remote viewing. It uses the Plotly Dash framework built on top of Flask for Python.

## Testing locally

To test locally: `python app.py`. This will open the Dash page at the localhost: `http://127.0.0.1:8050/`

To stop running the application, use `ctrl + c`


## File description

* **app.py**: Main Python file which creates the dashboard application
* **stylesheet.css**: CSS stylesheet which is called by **app.py** for styling the dashboard. This file must be in a directory called *assets*
* **requirements.txt**: Requirements file for installing app dependencies with pip. This is also used by the application host
* **Procfile**: file which Heroku uses to launch app
* **runtime.txt**: file which Heroku uses to determine which Python runtime version to use
* **XX.csv**: any files with **.csv** extension are data files which are called by **app.py** for plotting



## Setup for development on Linux or MacOS

Install / upgrade pip: `python3 -m pip install --user --upgrade pip`

Test pip version: `python3 -m pip --version`

Install virtualenv: `python3 -m pip install --user virtualenv`

To create a virtual environment, navigate to the project folder and run: `python3 -m env <env>`, where `<env>` is the name of your new virtual environment.

Before installing packages inside the virtual environment, activate the environment: `source <env>/bin/activate`, where `<env>` is the name of your virtual environment.

To deactivate the environment: `deactivate`

Once the environment is activated, use pip to install libraries in it.

To export the list of installed packages as a `requirements.txt` file: `pip freeze > requirements.txt`

To install packages from the requirements file: `pip install -r requirements.txt`



## Free web hosting on Heroku

Before deploying to the web, make sure that the app is not configured in `debug` mode. This is done by setting the line `app.run_server(debug=False)` in `app.py`.

To host the application on the web using Heroku, first put it in a Github repository. Then follow these steps:

* Setup account on Heroku
* Create a new app in Heroku
* Open your new app and go to **Deploy**
* Choose Github as the deployment method, and connect to your Github repository
* Scroll to the bottom of the page and click **Deploy now** under the **Manual deploy** section
* To make changes, edit your files in the Github repo, then re-deploy on Heroku
