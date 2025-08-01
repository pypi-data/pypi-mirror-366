import os
import json
import pytest
from dotenv import load_dotenv
from sqlalchemy.engine import create_engine
from TCLIService.ttypes import TOperationState

# Load environment variables from .env
load_dotenv(override=True)

def test_timbr_dialect():
  # Declare the connection variables
  hostname = os.getenv("HOSTNAME")
  port = os.getenv("PORT")
  protocol = os.getenv("PROTOCOL")
  ontology = os.getenv("ONTOLOGY")
  username = os.getenv("USERNAME")
  password = os.getenv("PASSWORD") 
  connect_args_data = os.getenv("CONNECT_ARGS")
  connect_args = json.loads(connect_args_data)

  assert hostname is not None, "Missing HOSTNAME"
  assert port is not None, "Missing PORT"
  assert protocol is not None, "Missing PROTOCOL"
  assert ontology is not None, "Missing ONTOLOGY"
  assert username is not None, "Missing USERNAME"
  assert password is not None, "Missing PASSWORD"

  # Create new sqlalchemy connection
  engine = create_engine(f"timbr+{protocol}://{username}@{ontology}:{password}@{hostname}:{port}")

  # Connect to the created engine
  conn = engine.connect()

  # Execute a query
  query = "SHOW CONCEPTS"
  res_obj = conn.execute(query)

  results_headers = res_obj.keys()
  results = res_obj.fetchall()

  # Display the results of the execution formatted as a table
  # Print the columns name
  print(f"index | {' | '.join(results_headers)}")
  # Print a separator line
  print("-" * ((len(results_headers)+1) * 10))
  # Print the results
  for res_index, result in enumerate(results, start=1):
    print(f"{res_index} | {' | '.join(map(str, result))}")


























if __name__ == '__main__':

  # Declare the connection variables
  hostname = os.getenv("HOSTNAME")
  port = os.getenv("PORT")
  protocol = os.getenv("PROTOCOL")
  ontology = os.getenv("ONTOLOGY")
  username = os.getenv("USERNAME")
  password = os.getenv("PASSWORD")
  password = os.getenv("PASSWORD")
  connect_args_data = os.getenv("CONNECT_ARGS")
  connect_args = json.load(dict(connect_args_data))



  # connection_args_file_path = os.getenv("CONNECT_ARGS_FILE")
  # if not connection_args_file_path:
  #   raise RuntimeError("Missing CONNECT_ARGS_FILE in .env")

  # print(f"Loading connection args from: {connection_args_file_path}")
  # try:
  #   with open(connection_args_file_path) as f:
  #     connect_args = dict(json.load(f))
  # except Exception as e:
  #   raise RuntimeError(f"Failed to load connect args JSON: {e}")
  # print(f"Loaded connect args: {connect_args}")
  assert hostname is not None, "Missing HOSTNAME"
  assert port is not None, "Missing PORT"
  assert protocol is not None, "Missing PROTOCOL"
  assert ontology is not None, "Missing ONTOLOGY"
  assert username is not None, "Missing USERNAME"
  assert password is not None, "Missing PASSWORD"

  # HTTPS example

  try:
    # example file
    print("RUNNING REGULAR QUERY: \n")
    # Create new sqlalchemy connection
    engine = create_engine(f"timbr+{protocol}://{username}@{ontology}:{password}@{hostname}:{port}")

    # Connect to the created engine
    conn = engine.connect()

    # Execute a query
    query = "SHOW CONCEPTS"
    res_obj = conn.execute(query)

    results_headers = res_obj.keys()
    results = res_obj.fetchall()

    # Display the results of the execution formatted as a table
    # Print the columns name
    print(f"index | {' | '.join(results_headers)}")
    # Print a separator line
    print("-" * ((len(results_headers)+1) * 10))
    # Print the results
    for res_index, result in enumerate(results, start=1):
      print(f"{res_index} | {' | '.join(map(str, result))}")

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    print("RUNNING ASYNC QUERY: \n")



    # async pyhive

    # Create new sqlalchemy connection
    engine = create_engine(f"hive+{protocol}://{username}@{ontology}:{password}@{hostname}:{port}", connect_args={'configuration': {'set:hiveconf:hiveMetadata': 'true'}})

    # Connect to the created engine
    conn = engine.connect()
    dbapi_conn = engine.raw_connection()
    cursor = dbapi_conn.cursor()

    # Execute a query
    query = "SHOW CONCEPTS"
    cursor.execute(query)

    # Check the status of this execution
    status = cursor.poll().operationState
    while status in (TOperationState.INITIALIZED_STATE, TOperationState.RUNNING_STATE):
      status = cursor.poll().operationState

    # Get the results of the execution
    results_headers = [(desc[0], desc[1]) for desc in cursor.description]
    results = cursor.fetchall()

    # Display the results of the execution
    # Print the columns name
    for name, col_type in results_headers:
      print(f"{name} - {col_type}")
    # Print the results
    for result in results:
      print(result)

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    print("RUNNING SYNC QUERY: \n")



    # sync pyhive

    # Create new sqlalchemy connection
    engine = create_engine(f"timbr+{protocol}://{username}@{ontology}:{password}@{hostname}:{port}", connect_args=connect_args)

    # Connect to the created engine
    conn = engine.connect()

    # Use the connection to execute a query
    query = "SHOW CONCEPTS"
    # query = "select sleep(20)"
    # query = "SHOW SCHEMAS"
    res_obj = conn.execute(query)
    results_headers = [(desc[0], desc[1]) for desc in res_obj.cursor.description]
    results = res_obj.fetchall()

    # Print the columns name
    for name, col_type in results_headers:
      print(f"{name} - {col_type}")
    # Print the results
    for result in results:
      print(result)


    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    
  except Exception as e:
    print(e)