import time


users = {}


LIMIT = 5
TIME = 5


def check_flood(user_id):

    now = time.time()


    if user_id not in users:
        users[user_id] = []



    users[user_id].append(now)


    users[user_id] = [
        t for t in users[user_id]
        if now - t < TIME
    ]


    if len(users[user_id]) >= LIMIT:
        return True


    return False
