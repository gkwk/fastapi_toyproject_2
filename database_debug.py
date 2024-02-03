from models import User
from domain.user.user_schema import RequestUserCreate
from domain.user.user_crud import create_user
from datetime import datetime
from database import session_local

data_base = session_local()

try:
    data_base.query(User).delete()
    data_base.commit()

    limit = 50

    for i in range(limit):
        name = f"test{i}"
        email = f"test{i}@test.com"
        password = f"{i}"
        schema = RequestUserCreate(
            name=name, password1=password, password2=password, email=email
        )

        create_user(data_base=data_base, schema=schema)
        print(f"\rUser : {i+1}/{limit}", end="")
except:
    pass
data_base.commit()
data_base.close()
