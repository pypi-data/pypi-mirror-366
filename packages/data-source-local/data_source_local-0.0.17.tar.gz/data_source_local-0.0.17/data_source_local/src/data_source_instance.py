from database_mysql_local.generic_crud_ml import IS_MAIN_COLUMN_NAME, GenericCRUDML

class DataSourceInstance(GenericCRUDML):
    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name = "data_source", 
            default_table_name = "data_source_instance_table", 
            default_view_table_name = "data_source_instance_view", 
            is_test_data = is_test_data)