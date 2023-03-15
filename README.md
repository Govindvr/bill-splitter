# bill-splitter

Python version used : 3.10.6

## Installation
First clone this repo
Create a venv and activate it(optional)
To install the required packages
```bash
pip  install -r requirements.txt
```
## Run
To update database
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
To Run the app
```bash
python manage.py runserver
```
The app will be availiable on http://localhost:8000/
<br>
<br>
### Usage

A bill-splitting app where users can split bills among other users. The application have features like

·Users can sign up/sign in.

· A user can Add/Delete/Update bills split against another user(s).

· A user can form groups and split bills among group members as a whole or selectively.

· The bill being split could be based on a percentage/specific amount.

· There would be a summary screen which lists the amount the user owes to everyone based on the bill-splitting activity till now. Users can settle bills, and this would start over again.