from typing import Literal
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

# Função para obter os buckets disponíveis no cliente
def get_buckets(cliente):
    buckets_api = cliente.buckets_api()
    buckets = buckets_api.find_buckets().buckets
    result = []
    for bucket in buckets:
        bucket_dict = {
            "name": bucket.name,
            "id": bucket.id,
        }
        result.append(bucket_dict)

    return result

  
# Função para obter o esquema de um bucket específico        
def get_bucket_schema(bucket, schema: Literal['fieldKeys','tagKeys', 'measurements'], org, cliente):
    query = f"""
    import \"influxdata/influxdb/schema\"

    schema.{schema}(bucket: \"{bucket}\")
    """
    
    query_api = cliente.query_api()
    tables = query_api.query(query=query, org=org)
    result = [row.values["_value"] for table in tables for row in table]
    return result

# Função para obter o esquema de medições (measurements) de um bucket específico
def get_measurements_schema(bucket, measurements, schema: Literal['Tag','Field'], org, cliente):
    query = f"""import \"influxdata/influxdb/schema\"
                schema.measurement{schema}Keys(
                    bucket: "{bucket}",
                    measurement: "{measurements}",
                )
            """
    
    query_api = cliente.query_api()
    tables = query_api.query(query=query, org=org)
    result = [row.values["_value"] for table in tables for row in table]
    return result

# Função para obter os valores de tags de medições (measurements) de um bucket específico
def get_measurements_value(bucket, measurements, tag, org, cliente):
    query = f"""import \"influxdata/influxdb/schema\"
                schema.measurementTagValues(
                    bucket: "{bucket}",
                    measurement: "{measurements}",
                    tag: {tag},
                )
            """
    
    query_api = cliente.query_api()
    tables = query_api.query(query=query, org=org)
    result = [row.values["_value"] for table in tables for row in table]
    return result

# Função para obter os IDs únicos de um bucket e medição (measurement) específicos
def get_ids(bucket, measurements, org, cliente):
    query = f"""from(bucket: "{bucket}")
                |> range(start: -1m)
                |> filter(fn: (r) => r["_measurement"] == "{measurements}")
                |> keep(columns: ["id"])
            """
    
    result = cliente.query_api().query_data_frame(query, org=org)
    unique_ids = list(set(result['id'].tolist()))
    return unique_ids