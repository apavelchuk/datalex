# Datalex

That app demonstrates use of Django/DjangoRestFramework/Postgres for dynamic creation of custom tables/models in runtime without a need for migrations.

## Installation
```
docker-compose up
```

## Usage
Once the container has started it serves Django's builtin webserver at your localhost:8000.

These endpoints are available:

### /api/table POST
Creating a new schema entry along with it's DB representaion (table).
Only "string", "number" and "boolean" are available as field types.
```
curl --location 'localhost:8000/api/table' \
--header 'Content-Type: application/json' \
--data '{
    "name": "first_table5",
    "fields": [{"name": "f1", "field_type": "boolean"}, {"name": "f2", "field_type": "number"}]
}'
```

### /api/table/<table_id> PUT
Updates your table sctructure entirely, i.e. you must provide your schema in full just as when you create a new schema.
*Note*: it completely relies on Postgres ability to alter fields.
**WARNING**: if you do not provide fields here that do exist on table at the moment of the request, they will be deleted with all respected data. Also, if you define new type for an existing field Postgres will do its best to convert it, but in case of e.g. string -> number an error will be thrown.
```
curl --location --request PUT 'localhost:8000/api/table/1' \
--header 'Content-Type: application/json' \
--data '{
    "name": "first_table",
    "fields": [{"name": "new_bool_field", "field_type": "boolean"}, {"name": "new_string_field", "field_type": "string"}]
}'
```


### /api/table/<table_id>/row POST
Creates a new row in the table specified.
```
curl --location 'localhost:8000/api/table/1/row' \
--header 'Content-Type: application/json' \
--data '{
    "new_bool_field": false,
    "new_string_field": "some longer string"
}'
```

### /api/table/<table_id>/rows GET
Returns the rows for the table specified.
```
curl --location 'localhost:8000/api/table/1/rows'
```
