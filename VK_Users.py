import flatdict


def except_multiple_values(field, values, users_dict):
    results = []
    for user in users_dict:
        if user.get(field) not in values:
            results.append(user)
    return results


def make_flat(users_dict):
    results = []
    for user in users_dict:
        results.append(dict(flatdict.FlatDict(user)))
    return results


class Users:
    def __init__(self, request_result):
        self.all_users = make_flat(except_multiple_values('relation', [2, 3, 4], request_result))
        self.sorted_users = self.all_users
        self.last_user = 0

    def reset_sorted(self):
        self.sorted_users = self.all_users

    def get_next_5(self):
        next_5 = []
        users_left = len(self.sorted_users) - self.last_user
        if users_left > 5:
            step = 5
        else:
            step = users_left
        for i in range(self.last_user, self.last_user + step):
            next_5.append(self.sorted_users[i])
            self.last_user += 1
        return next_5

    def not_empty_field(self, field):
        sorted_by_field = []
        for user in self.sorted_users:
            if user.get(field):# is not None and user.get(field) != '':
                sorted_by_field.append(user)
        self.sorted_users = sorted_by_field

    def value_in_field(self, value, field):
        results = []
        for user in self.all_users:
            if user.get(field) == value:
                results.append(user)
        self.sorted_users = results




