# Django Backend Server

<!-- ## Features-->
<!---->
<!--- [ ] Restful Structure-->
<!--- [ ] MongoDB Integration-->
<!--- [ ] Machine Learning Library Integration-->
<!--- [ ] Facebook API Integration-->
<!--- [ ] Google API Integration-->
<!--- [ ] Admin Panel-->
<!--- [ ] Python 3.x support-->
<!--- [ ] Error Handling-->
<!--- [ ] Tests-->
<!--- [ ] Logging-->

## Setup
- Install Mongodb (confirmed to work with MongoDB version 3.4.5)
    - Setup testing database
       ```
       use django_test
       db.createUser( { user: "admin", pwd: "password", roles: [ { role: "clusterAdmin", db: "admin" }, { role: "readAnyDatabase", db: "admin" }, "readWrite"] })
       ```
- Create and activate virtualenv

- `pip install -r requirement.txt`

- `python manage.py runserver`

## Libraries
- [Django](https://github.com/django/django)
- [MongoEngine](https://github.com/MongoEngine/mongoengine)
- [Django-rest-framework](https://github.com/encode/django-rest-framework/tree/master)
- [Django Rest Framework Mongoengine](https://github.com/umutbozkurt/django-rest-framework-mongoengine)
<!--- [Facebook Python SDK](https://github.com/mobolic/facebook-sdk)-->
<!--- [facepy](https://github.com/jgorset/facepy)-->
<!--- [google-api-python-client](https://github.com/google/google-api-python-client)-->

