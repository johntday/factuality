import os
import psycopg2
import json

DATABASE_URL = os.getenv('DATABASE_URL')


def update_to_database(tweet) -> None:
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE twitter_tweets
            SET 
                response_fact = %s, 
                gist_url = %s, 
                status = 'done' 
            WHERE id = %s
        """, (
            json.dumps(tweet['factuality'], indent=4),
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
