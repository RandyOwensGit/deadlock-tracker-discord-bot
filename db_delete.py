from database import engine, Base

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)