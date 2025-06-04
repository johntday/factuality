import os
import psycopg2
import json

DATABASE_URL = os.getenv('DATABASE_URL')

def format_tweet(row):
    return {
        'id': row[0],
        'user_screen_name': row[1],
        'full_text': row[2],
        'created_at': row[3],
    }

def fetch():
    results = []
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(f"""select id, user_screen_name, full_text, created_at_unix
        from twitter_tweets 
        where status = 'fact'
        order by created_at_unix desc 
        limit 10""")

        rows = cur.fetchall()
        for row in rows:
            results.append(format_tweet(row))

        # conn.commit()
        return results
    except Exception as e:
        print(f"Error with fetch: {e}")
        return results
    finally:
        try:
            if cur:
                cur.close()
        except Exception as e:
            pass
        try:
            if conn:
                conn.close()
        except Exception as e:
            pass
        return results


def update_db(tweet) -> None:
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE twitter_tweets
            SET 
                response_fact = %s, 
                tweet = %s,
                gist_url = %s, 
                status = 'done' 
            WHERE id = %s
        """, (
            json.dumps(tweet['factuality']),
            tweet['gist_url'],
            tweet['id'],
        ))
        connection.commit()
    except Exception as e:
        print(f"Error saving tweet to database: {e}")
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception as e:
            pass
        try:
            if connection:
                connection.close()
        except Exception as e:
            pass
