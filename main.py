from fastapi import FastAPI

import models
from database import Base, engine
from routers import posts, users


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# FASTAPI APP
# =========================

app = FastAPI()


# =========================
# INCLUDE ROUTERS
# =========================

app.include_router(posts.router) #the api endppints are in the router now no need to write in the main code itself the main code must be clean and not too big to handle 
app.include_router(users.router) # the api endpnt related to the users are now here 
#structure of the db is managed by the alembic mmigrations nd the data inside the db is managed by the files that we have written hi 