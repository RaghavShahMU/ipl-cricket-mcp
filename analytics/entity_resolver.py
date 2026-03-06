import duckdb


DB_PATH = "data/ipl.duckdb"


def get_all_players():

    con = duckdb.connect(DB_PATH)

    players = con.execute(
        """
        SELECT DISTINCT batter FROM balls
        UNION
        SELECT DISTINCT bowler FROM balls
        """
    ).fetchall()

    con.close()

    return [p[0] for p in players]


def get_all_teams():

    con = duckdb.connect(DB_PATH)

    teams = con.execute(
        """
        SELECT DISTINCT batting_team FROM balls
        UNION
        SELECT DISTINCT bowling_team FROM balls
        """
    ).fetchall()

    con.close()

    return [t[0] for t in teams]
