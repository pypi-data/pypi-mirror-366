from database_mysql_local.generic_crud_ml import GenericCRUDML
from language_remote.lang_code import LangCode


class DataSources(GenericCRUDML):

    def __init__(self):
        GenericCRUDML.__init__(self, default_schema_name='data_source',
                               default_table_name='data_source_type_table',
                               default_view_table_name='data_source_type_ml_en_view',
                               default_ml_view_table_name='data_source_type_ml_en_view')
        self.__all_external_field_names = None

    # TODO Why do we return two ints?
    # TODO insert_fields() per our Python Class methods naming conventions https://docs.google.com/document/d/1QtCVak8f9rOtZo9raRhYHf1-7-Sfs8rru_iv3HjTH6E/edit?usp=sharing
    def insert_data_source_type(self, data_source_type_name: str, lang_code: LangCode = LangCode.ENGLISH,
                                system_id: int = None, subsystem_id: int = None,
                                data_source_category_id: int = None) -> tuple[int, int]:
        # TODO Both are not needed if using the MetaLogger
        METHOD_NAME = 'insert_data_source_type'
        self.logger.start(METHOD_NAME, object={
            'data_source_type_name': data_source_type_name,
            'lang_code': lang_code})
        try:
            data_source_type_dict = {
                'name': data_source_type_name,
                'system_id': system_id,
                'subsystem_id': subsystem_id,
                'data_source_category_id': data_source_category_id
            }
            data_source_type_ml_dict = {
                'title': data_source_type_name,
            }
            data_source_type_id, data_source_type_ml_id = self.add_value(
                data_dict=data_source_type_dict,
                data_ml_dict=data_source_type_ml_dict,
                lang_code=lang_code,
                is_main=None,
                table_name='data_source_type_table',
                ml_table_name='data_source_type_ml_table'
            )
            # TODO Why do we need to return the data_source_ml_id?
            self.logger.end(METHOD_NAME, object={
                'data_source_type_id': data_source_type_id,
                'data_source_type_ml_id': data_source_type_ml_id})
            return data_source_type_id, data_source_type_ml_id

        except Exception as exception:
            self.logger.exception(
                log_message="faild to insert data_source " + METHOD_NAME + str(exception),
                object={"exception": exception})
            self.logger.end(METHOD_NAME, object={
                'data_source_name': data_source_type_name, 'lang_code': lang_code})
            raise exception

    '''
    # Old version
    # TODO Do we need to keep the old version?
    def get_data_source_type_id_by_name(self, data_source_type_name: str) -> int or None:
        METHOD_NAME = 'get_data_source_type_id_by_name'
        try:
            self.logger.start(log_message=METHOD_NAME, object={
                'data_source_type_name': data_source_type_name})
            data_source_type_id = self.select_one_value_by_id(
                select_clause_value='data_source_type_id',
                id_column_name='name',
                id_column_value=data_source_type_name)
            if data_source_type_id:
                self.logger.end(METHOD_NAME, object={
                    'data_source_type_id': data_source_type_id})
                return data_source_type_id
            else:
                self.logger.end(METHOD_NAME, object={
                    'data_source_type_id': data_source_type_id})
                return None
        except Exception as exception:
            self.logger.exception(
                log_message="faild to get data_source_type_id " + METHOD_NAME + str(exception), object={"exception": exception})
            self.logger.end(METHOD_NAME, object={
                'data_source_type_name': data_source_type_name})
            raise exception

    def get_data_source_type_name_by_id(self, data_source_type_id: int) -> str or None:
        METHOD_NAME = 'get_datasource_type_name_by_id'
        try:
            self.logger.start(log_message=METHOD_NAME, object={
                'data_source_type_id': data_source_type_id})
            data_source_type_name = self.select_one_value_by_id(
                view_table_name='data_source_type_ml_en_view',
                select_clause_value='name',
                id_column_name='data_source_type_id',
                id_column_value=data_source_type_id)
            if data_source_type_name:
                self.logger.end(METHOD_NAME, object={
                    'data_source_type_name': data_source_type_name})
                return data_source_type_name
            else:
                self.logger.end(METHOD_NAME, object={
                    'data_source_type_name': data_source_type_name})
                return None
        except Exception as exception:
            self.logger.exception(
                log_message="faild to get data_source_type_name " + METHOD_NAME + str(exception),
                object={"exception": exception})
            self.logger.end(METHOD_NAME, object={
                'data_source_type_id': data_source_type_id})
            raise exception
    '''

    def get_data_source_type_id_by_name(self, data_source_type_name: str) -> int or None:
        data_source_type_id = self.select_one_value_by_column_and_value(
            select_clause_value='data_source_type_id',
            column_name='name',
            column_value=data_source_type_name)
        return data_source_type_id

    def get_data_source_name_by_id(self, data_source_type_id: int) -> str or None:
        data_source_name = self.select_one_value_by_column_and_value(
            select_clause_value='name',
            column_name='data_source_type_id',
            column_value=data_source_type_id)
        return data_source_name

    def get_external_field_names(self, data_source_type_id: int, field_name: str) -> list[tuple]:
        if not self.__all_external_field_names:
            sql_query = """SELECT -- DISTINCT 
                        dsft.data_source_type_id, ft.name, dsft.external_field_name 
                        FROM data_source_field.data_source_field_table AS dsft 
                        JOIN field.field_table AS ft ON dsft.field_id = ft.field_id 
                        -- WHERE dsft.data_source_type_id = %s AND ft.name = %s;"""
            self.cursor.execute(sql_query, (data_source_type_id, field_name))
            self.__all_external_field_names = self.cursor.fetchall()  # list of tuples

        external_field_names = []
        for _data_source_type_id, name, external_field_name in self.__all_external_field_names:
            if (data_source_type_id == _data_source_type_id and name == field_name
                    and external_field_name not in external_field_names):
                external_field_names.append(external_field_name)
        return external_field_names

    # TODO Now that we use the same method also for Google Sheets, shall we remove the csv from the method name and update every place we use i.e. csv_import repo
    def get_external_csv_field_name(self, data_source_type_id: int, field_name: str, index: int = None) -> str or None:
        """
        Get the CSV field name by data source type ID and field name
        :param data_source_type_id: The data source ID
        :param field_name: The field name
        :param index: The index of the field
        :return: The CSV field name
        """

        external_csv_field_name = None
        external_field_names = self.get_external_field_names(data_source_type_id, field_name)
        if not external_field_names:
            return external_csv_field_name
        elif index is None or index == 1:
            external_csv_field_name = external_field_names[0]
        else:
            for name in external_field_names:
                # TODO: this is not working as we want for outlook csv, it add only 1 phone number, fix it
                # I think we should change Mobile phone to Phone Number in data_source_field_table
                # And add Phone Number 2 and Phone Number 3 to the table
                if str(index) in name:
                    external_csv_field_name = name
                    break

        return external_csv_field_name

    # TODO Which csv? LinkedIn? Facebook?
    # TODO This is not database table driven?
    # TODO As this method will also be used by Google Sheets, we can remove the csv from the method name
    def get_fields_name_from_csv(self, data_source_type_id: int) -> dict:
        # TODO Shall we bring this data from the DataSourceFields new class based on the data_source_field_table
        mapping = {
            'first_name': {"field_name": 'First Name'},
            'last_name': {"field_name": 'Last Name'},
            'name_prefix': {"field_name": 'Name Prefix'},
            'additional_name': {"field_name": 'Additional Name'},
            'name_suffix': {"field_name": 'Name Suffix'},
            'nickname': {"field_name": 'Nickname'},
            'full_name': {"field_name": 'Name'},
            'title': {"field_name": 'Education/University'},
            'phone1': {"field_name": 'Phone Number', "index": 1},
            'phone2': {"field_name": 'Phone Number', "index": 2},
            'phone3': {"field_name": 'Phone Number', "index": 3},
            'birthday': {"field_name": 'Birthday'},
            'hashtag': {"field_name": 'Hashtag'},
            'notes': {"field_name": 'Notes'},
            'email1': {"field_name": 'Email', "index": 1},
            'email2': {"field_name": 'Email', "index": 2},
            'email3': {"field_name": 'Email', "index": 3},
            'website1': {"field_name": 'Website', "index": 1},
            'website2': {"field_name": 'Website', "index": 2},
            'website3': {"field_name": 'Website', "index": 3},
            'url': {"field_name": 'URL'},
            # TODO Shall we call it added_timestamp as this is not standard in our system? Shall we use start_timestamp? created_timestamp?
            'added_timestamp': {"field_name": 'Connected On'},
            'groups': {"field_name": 'Groups'},
            'comment': {"field_name": 'Comment'},
            'display_as': {"field_name": 'Display As'},
            'job_title': {"field_name": 'Job Title'},
            'organization': {"field_name": 'Organization/Company'},
            'department': {"field_name": 'Department'},
            'handle': {"field_name": 'LinkedIn Profile ID'},
            'address1_street': {"field_name": 'Home Street'},
            'address1_city': {"field_name": 'City'},
            'address1_state': {"field_name": 'State'},
            'address1_postal_code': {"field_name": 'Home Postal Code'},
            'address1_country': {"field_name": 'Country'},
            'address2_street': {"field_name": 'Home Street 2'},
            'address2_city': {"field_name": 'Other City'},
            'address2_state': {"field_name": 'Other State'},
            'address2_postal_code': {"field_name": 'Other Postal Code'},
            'address2_country': {"field_name": 'Other Country/Region'},
        }
        '''
        # Old version
        contact_from_file_dict = {key: self.get_external_csv_field_name(
            data_source_type_id=data_source_type_id, field_name=value['field_name'], index=value.get('index'))
            for key, value in mapping.items()}
        '''
        contact_from_file_dict = {key: self.get_external_csv_field_name(
            data_source_type_id=data_source_type_id, field_name=value['field_name'], index=value.get('index'))
            for key, value in mapping.items()}

        return contact_from_file_dict
