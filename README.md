# mobile-food-search-application
*A application that is built to facilitate search functionalities of various mobile food facilities. Currently limited to the scope of San Francisco*


## Requirements

Search by name of applicant. Include optional filter on "Status" field.
Search by street name. The user should be able to type just part of the address. Example: Searching for "SAN" should return food trucks on "SANSOME ST"
Given a latitude and longitude, the API should return the 5 nearest food trucks. By default, this should only return food trucks with status "APPROVED", but the user should be able to override this and search for all statuses.

---

## Running via Docker

One can simply run the application via docker by running the following commands from the root directory:

`docker compose build`

`docker compose up`

The application should then be available on http://localhost:80/

---

## Development Setup

clone the repository to your local machine. e.g. git clone https://github.com/ZeroTrepidation/mobile-food-search-application.git

To build and run the backend, run the following commands:

`cd mobile-food-search-application/backend`

`python -m venv venv`

MacOS/Linux:
`source venv/bin/activate`

Windows:
`venv\Scripts\activate`

`pip install -r requirements.txt`

`uvicorn app.main:app --host 0.0.0.0 --port 8000`

The backend should now be running on http://localhost:8000/

Additionally tests can be run by using:

`pytest`

---

To build and run the frontend, run the following commands (from the root directory):

`cd mobile-food-search-application/frontend`

`npm install`

`npm run dev`

The application should now be running on http://localhost:5173/

---


## Problem

We would like a way to search for mobile food facilities within San Francisco. This data is available via a public 
[government provided](https://data.sfgov.org/Economy-and-Community/Mobile-Food-Facility-Permit/rqzj-sfat) api. This data
features a variety of information about the permits, including the name of the applicant, the street address, the 
status of the permit, and the latitude and longitude of the facility. This application was created to provide a better 
experience for users who may want to filter the data and view it in a more meaningful way. 

Certain logic was added to check for the relevency / validity of the data. This logic can be modified or extended if needed
to better suit the needs of the application. One such example was to exclude coordinates that are equal to 0.0 / 0.0 because
these coordinates are certainly outside the city of San Francisco and not relevent to the user.

## Summary of Approach

The approach taken was to create a small backend API utilizing python and fastapi and then develop a small frontend spa 
in react to provide a simple user interface. The reasoning behind these technologies was because these were lightweight and
easy to use frameworks and also frameworks that I am new to and looking to gain more experience with.

One thing that I was interested in experimenting with was implementing Domain Driven Design principles in Python. Because
of this I chose to go with a OOO approach utilizing the ports and adapters design pattern. Not only did this pattern allow
me to gain experience with DDD in Python, but it also allowed me to develop a more modular and scalable application that
allows for a more plug and play approach when adding or modifying features. 

For the sake of time, some implementations were simplified, e.g. utilizing a in-memory datastore instead of a database, 
and utilizing a basic async task manager instead of something like Celery. This is not a production ready application, 
but it is a good starting point for a more robust application.

## Critiques

Since I'm more used to developing applications in Java, I'm not quite sure if the code structure / style is as pythonic
as it could be. Would be interested in hearing feedback and other ways to organize the code.

Currently the application cannot really be run with multiple workers. Since the background task logic and the REST API 
are bundled in the same process, running multiple workers could result bottlenecks or other issues when persisting / fetching
data from external sources. This results in the application not necessarily being as scalable as it could be. With that being
said, implementing some kind of message queue / task queue such as Celery would allow for a more robust application and 
scalable application that could be set up to run many background jobs to refresh data in parallel.

As mentioned in the summary above, I decided to for now go with a simple in-memory datastore for the sake of time. This was
a deliberate design decision for the sake of simplicity. I chose to do this over just querying the datasource directly so
that we could introduce validation logic, along with avoid potential throttling / rate limiting issues that could arise
from querying the datasource directly. With that being said, it would be fairly easy to wire in a new or even multiple 
external datastores into the application.

Another reason for an in-memory datastore is due to the size of the dataset. Since the dataset is relatively small, 
there was not much downside in terms of memory utilization and performance.

One other thing I'm unsure of is how I handled dependency injection and if this was a good approach in Python. Would be interested
in hearing feedback on this.

As for the frontend, a simple react application was built to provide a simple and clean UI for a user to interact with. 
Originally I was going to use the Google Maps API, but decided to go with a open source approach to avoid any potential 
licensing issues or costs. If needed an alternative Map library could be used.





