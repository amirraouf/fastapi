# Backend Task

This exercise involves building a FastAPI app that will serve an API. We expected you should spend around 3 hours to implement it.

## Getting Started

The exercise requires [Python](https://www.python.org/) to be installed. The instructions below assume you're using Poetry to manage dependencies, but you can use whatever you want. If you don't have Poetry installed, you can follow the instructions [here](https://python-poetry.org/docs/#installation).

1. Start by creating a local repository for this folder.

2. In the repo root directory, run `poetry install` to install dependencies.

3. Run `export PYTHONPATH=.` to set the python path.

4. Run `poetry run alembic upgrade head` to apply the migrations.

5. Run `poetry run python app/seed.py` to seed the database.

6. Run `poetry run fastapi dev app/main.py` to start the server on port 8000.

❗️ **Make sure you commit all changes to the main branch!**

## Technical Details

- The database in use is SQLite, and the ORM used is [SQLAlchemy](https://www.sqlalchemy.org/). Please spend some time reading the SQLAlchemy documentation before starting the exercise. [Alembic](https://alembic.sqlalchemy.org/) is used for migrations.
- The database schema is already created and can be found under `app/models.py`. If you wanna change the schema, you can do so by changing the models file, but please explain why you did so. You can also add indexes, constraints, etc..
- To authenticate users use the `get_current_user` FastAPI dependency that is located under `app/dependencies/get_current_user.py`. Users are authenticated by passing `user_id` in the request header.
- The project structure is not set in stone, feel free to change it if you think it will make your application more organized.
- The application should be able to handle fractional amounts of money.
- The application should be able to handle errors and return the correct status codes.
- The application should be able to handle concurrent requests.

## APIs To Implement

1. **_GET_** `/transfers` - This API is already created, but it only returns the correct data when the user is the receiver of a transfer. You should update it to return the correct data when the user is the sender of a transfer as well.

2. **_GET_** `/transfers/:id` - Get a transfer by id, the user should be able to get a transfer only if he is the sender or the receiver of the transfer.

3. **_POST_** `/transfers/:id/accept` - Allows the receiver of a transfer to accept it. The amount should be moved from the sender's balance to the receiver's balance. Thndr gets a 2% fee on the transfer amount.

4. **_POST_** `/transfers/:id/reject` - Rejects the transfer, the amount should be available again in the sender's balance.

5. **_POST_** `/deposit` - Deposits money into the user's balance.

6. **_POST_** `/withdraw` - Withdraws money from the user's balance.

7. **_GET_** `/leaderboard/top-transfers` - Returns the top users who have made or have the received the most transfers, the consumer of the API can specify the number of users to return, and they can specify if they want to get the top users with the most transfers as a count or the top users with the most transferred amount.

## Submitting the Assignment

When you have finished the assignment, zip your repo (make sure to include .git folder) and send us the zip.
Do not forget to include a md file with any notes you want to share with us.
If you have some extra time on your hands, feel free to go the extra mile to show off your skills. You can, for example, build a simple frontend that consumes the API or write tests for the application. We appreciate any extra effort you put into the assignment.
If you find any issues or have any questions, please let us know.

**Important:** Do not share the repo on GitHub or any other public platform.

Good luck! 🍀
