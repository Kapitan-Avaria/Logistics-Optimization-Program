from flask import Flask
import os
import json

from source.data_operator import DataOperator
from source.adapters.database.database_sqlite import DatabaseSQLiteAdapter
from source.adapters.external_data.business_api_client import BusinessAPIClient


def configure_application(application: Flask) -> None:
    base_path = os.path.abspath(".")
    cfg_path = os.path.join(base_path, 'data/config.cfg')
    db_path = os.path.join(base_path, 'data/database.db')
    application.config.from_file(cfg_path, load=json.load)
    application.config['DATA_OPERATOR'] = DataOperator(
        db=DatabaseSQLiteAdapter(db_path),
        business_data=BusinessAPIClient(application.config["URL_BUSINESS_API"]),
        geo_data=,
        routing_data=
    )
