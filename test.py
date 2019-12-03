from app import db, User


def create_user():
    for i in range(100):
        if i < 10:
            user = User(username=f'u00{i}', password=f'pw00{i}')
        elif i >= 10 and i < 100:
            user = User(username=f'u0{i}', password=f'pw0{i}')
        elif i == 100:
            user = User(username=f'u{i}', password=f'pw{i}')
        db.session.add(user)

    db.session.commit()


if __name__ == '__main__':
    create_user()
