from datetime import date as DateType


def get_leaderboard(
    conn,
    user_id: str,
    scope: str,
    date_from: DateType | None,
    date_to: DateType | None,
) -> list:
    """Agreguje sume punktow per user, sortuje malejaco i nadaje rank.
    Punkty pochodza z meals_mealitem (1 kcal = 1 pkt, naliczane przy dodawaniu posilku).
    scope=global: wszyscy uzytkownicy
    scope=friends: zalogowany + ci, ktorych obserwuje
    """
    conditions = []
    params: list = []

    if scope == "friends":
        conditions.append(
            "le.user_id IN ("
            "  SELECT followed_id FROM users_follower WHERE follower_id = %s"
            "  UNION SELECT %s"
            ")"
        )
        params.extend([user_id, user_id])

    if date_from is not None:
        conditions.append("le.created_at >= %s")
        params.append(date_from)

    if date_to is not None:
        # do konca dnia
        conditions.append("le.created_at < (%s::date + INTERVAL '1 day')")
        params.append(date_to)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    sql = f"""
        SELECT u.id AS user_id, u.username,
               SUM(le.score)::int AS total_score,
               COUNT(le.id)::int AS entries_count,
               RANK() OVER (ORDER BY SUM(le.score) DESC)::int AS rank
        FROM leaderboard_entry le
        JOIN users_user u ON u.id = le.user_id
        {where_clause}
        GROUP BY u.id, u.username
        ORDER BY total_score DESC, u.username
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()
