import asyncio
import aiopg
import time
import random
import subprocess
import json 

# List of SQL queries to be executed
sql_queries = [
    "SELECT * FROM gebieden_buurten_ligt_in_wijk LIMIT 10;",
    "SELECT * FROM hr_ves_email_adressen ORDER BY id DESC LIMIT 5;",
    "SELECT COUNT(*) FROM hr_ves_post_heeft_nummeraanduiding;"
]

def generate_db_token(environment):
    command = "az account get-access-token --resource-type oss-rdbms"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error generating token: {stderr.decode()}")
        return None, 0
    return json.loads(stdout.decode().strip())['accessToken']


# Asynchronous function to connect to the database and execute a random query
async def execute_query():
    try:
        # Establish an asynchronous connection to the PostgreSQL database
        async with aiopg.create_pool(**db_config) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Record the start time
                    start_time = time.time()
                    
                    # Randomly select a query from the list
                    sql_query = random.choice(sql_queries)
                    
                    # Execute the selected query asynchronously
                    await cursor.execute(sql_query)
                    
                    # Fetch the results (optional, depends on the need)
                    results = await cursor.fetchall()
                    
                    # Calculate the elapsed time
                    elapsed_time = time.time() - start_time
                    
                    return f"Executed query successfully, elapsed time: {elapsed_time} seconds"
    except Exception as e:
        return f"Error occurred: {str(e)}"


# Main coroutine to run the script asynchronously in a loop
async def main():
    try:
        # Number of concurrent tasks
        num_tasks = 10
        
        # Run indefinitely until interrupted
        while True:
            print("Starting a new batch of queries...")
            # Create a list of tasks
            tasks = [execute_query() for _ in range(num_tasks)]
            
            # Gather all tasks and execute them concurrently
            results = await asyncio.gather(*tasks)
            
            # Print the results from each task
            for result in results:
                print(result)
            
            # Optional: Add a delay between batches if needed
            await asyncio.sleep(1)  # Delay for 1 second before the next batch
    except KeyboardInterrupt:
        print("Stopped by the user.")


# Run the asyncio event loop
if __name__ == "__main__":

    environment = input("Environment (o or p): ")
    if environment == 'o':
        host = 'dev-bbn1-00-dbhost.postgres.database.azure.com'
        user = 'EM4W-DATA-databaseaadadmin-ont'
    elif environment == 'p':
        host = 'prd-bbn1-00-dbhost.postgres.database.azure.com'
        user = 'EM4W-DATA-databaseaadadmin-prd'
    else:
        raise ValueError('Environment must be one of o or p')

    # Database connection parameters
    db_config = {
        "dbname": "mdbdataservices",
        "user": user,
        "password": generate_db_token(environment),
        "host": host,
        "port": 5432
    }    

    asyncio.run(main())
