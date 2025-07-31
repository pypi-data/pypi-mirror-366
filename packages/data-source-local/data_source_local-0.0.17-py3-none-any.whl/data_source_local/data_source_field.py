from database_mysql_local.generic_mapping import GenericMapping


# TODO Tomorrow should be moved to data-source-type--field repo
class DataSourceTypeField(GenericMapping):
    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name="data_source_type__field",
            default_table_name="data_source_type__field_table",
            default_view_table_name="data_source_type__field_view",
            is_test_data = is_test_data)