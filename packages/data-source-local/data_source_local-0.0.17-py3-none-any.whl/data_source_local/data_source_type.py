from database_mysql_local.generic_crud_ml import IS_MAIN_COLUMN_NAME, GenericCRUDML

class DataSourceType(GenericCRUDML):
    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name = "data_source", 
            default_table_name = "data_source_type_table", 
            default_view_table_name = "data_source_type_general_view", 
            default_ml_table_name = "data_source_type_ml_table", 
            default_ml_view_table_name = "data_source_type_ml_en_view", 
            is_test_data = is_test_data)