#CAR SLOT #
A car park slot allocating system,primary built-on django python,which allow 
individuals to get an allocated parking space by inputting their car plate number

## Setup/Configuation procedure: ###
* Install the project requirements using "pip install -r requirements.txt"
* Change / modify the parking slot size inside .env ,however the input supplied  must be an integer ,
if not the system will throw ImproperlyConfigured error

* run python manage.py runserver to start the project with access the project through the following endpoint
- 127.0.0.1:8000
- Swagger / Documentation endpoint
    http://127.0.0.1:8000/swagger/
    http://127.0.0.1:8000/redoc/
    
 
#AVAILABLE API ENDPOINTS#
TO CREATE A SLOT 
- METHOD: POST
- URL:  http://127.0.0.1:8000/park/

TO GET SLOT INFORMATION
-METHOD: GET
-URL: http://127.0.0.1:8000/park/fetch_slot/

TO DE-ALLOCATE A SLOT
-METHOD: DELETE
-URL: http://127.0.0.1:8000/park/delete_slot/


- GITHUB
https://github.com/Emizy/carslot

### Requirements: ###
This project requirements can be found in the requirements.txt file
which include but not limited to the following:


*Django==3.1
*djangorestframework==3.12.1
*drf-yasg==1.20.0
*coreapi==2.3.3
