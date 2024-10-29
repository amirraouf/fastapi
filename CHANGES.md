## Changes

### models:
- changed balance and transfer amout to be REAL with 2 decimal places
- fixed updated_at to be updated_on

### dependencies:
- slowapi for ratelimiting
- option for unifing business logic and data access layer responses

### structure:
- added a new folder for business logic and data access layer
- added a new folder for tests - Tests are not working properly because dependencies overriding is not working properly and time is out for more debugging now

### Enhancements:
- Ensure application is set up with connection pooling. SQLAlchemy allows configuring a connection pool, which helps handle bursts of requests by reusing established database connections, thus reducing overhead.
- Implement a rate limiter to prevent abuse of the API. Rate limiting is a common technique to prevent abuse of APIs. It allows you to limit the number of requests a client can make in a given time frame.


### suggestions
- Add caching layer for transactions if it's been frequently accessed, that required lot of monitoring to make right descision

### code:
- Added formatting using ruff and pre-commit hooks