sql(t"select u.name, o.total from users u join orders o on u.id = o.user_id where u.active = {active} and o.total > {min_total}")
