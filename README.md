# Django Crypto Currencies Portfolio Management
Portfolio Management for crypto currencies using Django DRF &amp; Cellery

## This application allows following functionality:

01. Sign-up / Login / Account Management.
02. Add / Remove crypto currencies to portfolio.
03. Detailed trade order of individual currencies.
04. Profit / Loss per scripe and portfolio.
05. Reports of Holdings and Trade.
06. Charts displaying Portfolio allocation / Investment analysis & Scripe price movement.
07. DRF rest api for performing CRUD operations on portfolio allocations.


## Application details:
* This is Portfolio Management Webapp for realtime crypto currencies.  
* Application is built with Django Framework, DRF( Django Rest Framework ) is used for web APIs.
* Application UI built with bootstrap 4 
* Django allauth is used for user authentication and token authentication for APIs.
* ReportLab with pisa for report generation.
* Chart.js and canvas for chart generation.
* Celery and celery-beat along with redis for getting current crypto currencies price from external API.


## Technology Stack:
01. Python / Django / DRF
02. django-allauth
03. Bootstrap 4
04. xhtml2pdf / html5lib & reportLab
05. Chart.js
06. Celery & celery-beat
07. Redis



## For testing:
01. Clone the repo
02. Create virtual environment
03. Run - pip install -r requirements.txt
04. Setup django project and app.
05. Install celery - pip install django-celery-beat
06. Install redis server - pip install redis
07. Start redis , celery worker and celery-beat 
    celery -A [project-name] worker --loglevel=info
    celery -A [project-name] beat -l --loglevel=debug
08. Run migrations & start the Django server
09. Application should accessible at http://host:port

## Screenshots:
