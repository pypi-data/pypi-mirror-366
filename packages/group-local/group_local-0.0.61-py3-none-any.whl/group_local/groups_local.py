from typing import Dict

# from database_mysql_local.generic_crud import GenericCRUD
from database_mysql_local.generic_mapping import GenericMapping
from database_mysql_local.generic_crud_ml import GenericCRUDML
from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger
from user_context_remote.user_context import UserContext
from job_local.jobs_local import JobsLocal
from contact_group_local.contact_group import ContactGroups


from .group_local_constants import GroupLocalConstants

user_context = UserContext()

DEFAULT_SCHEMA_NAME = "group"
DEFAULT_TABLE_NAME = "group_table"
DEFAULT_VIEW_TABLE_NAME = "group_view"
DEFAULT_COLUMN_NAME = "group_id"
DEFAULT_IS_MAIN_COLUMN_NAME = "is_main_title"


class GroupsLocal(GenericCRUDML, metaclass=MetaLogger,
                  object=GroupLocalConstants.GROUP_PYTHON_PACKAGE_CODE_LOGGER_OBJECT):

    def __init__(self, is_test_data: bool = False):
        super().__init__(default_schema_name=DEFAULT_SCHEMA_NAME, default_table_name=DEFAULT_TABLE_NAME,
                         default_column_name=DEFAULT_COLUMN_NAME,
                         is_main_column_name=DEFAULT_IS_MAIN_COLUMN_NAME,
                         is_test_data=is_test_data)
        # We changed it from GenricCrud to GenericMapping 
        self.group_group_type_generic_mapping = GenericMapping(default_schema_name='group')
        self.job_local = JobsLocal()

    def insert(  # noqa
            self, *, group_dict: Dict[str, any], ignore_duplicate: bool = False,
            lang_code: LangCode = None) -> tuple[int, int]:
        """
            Returns the new group_id
            group_dict has to include the following
            for group_ml_table:
            title: str, lang_code: str = None,
            is_main_title: bool = True,
            "description": None,
            is_title_approved: bool = None,
            is_description_approved: bool = None
            for group_table:
            name: str,
            hashtag: str = None,
            is_approved: bool = False,
            parent_group_id: str = None,
            is_interest: bool = None,
            non_members_visibility_id: int = 1, members_visibility_id: int = 1,
            created_user_id: int = 0
            example of group_dict:
            {
                "title": "title",
                "lang_code": "en",
                "name": "name",
                "hashtag": "hashtag",
                "is_approved": True,
                "parent_group_id": 1,
                "is_interest": True,
                "non_members_visibility_id": 1,
                "members_visibility_id": 1,
                "description": "description",
                "is_title_approved": True,
                "is_description_approved": True,
                "created_user_id": 1
            }
        """
        if group_dict.get("main_group_type_id") is None:
            self.logger.error("main_group_type_id is required", object={"group_dict": group_dict})
            raise Exception("main_group_type_id is required")

        group_data_dict = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved'),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
            "is_job_title": group_dict.get('is_job_title', False),
            "is_role": group_dict.get('is_role', False),
            "is_skill": group_dict.get('is_skill', False),
            "is_organization": group_dict.get('is_organization', False),
            "is_geo": group_dict.get('is_geo', False),
            "is_continent": group_dict.get('is_continent', False),
            "is_country": group_dict.get('is_country', False),
            "is_state": group_dict.get('is_state', False),
            "is_county": group_dict.get('is_county', False),
            "is_region": group_dict.get('is_region', False),
            "is_city": group_dict.get('is_city', False),
            "is_neighbourhood": group_dict.get('is_neighbourhood', False),
            "is_street": group_dict.get('is_street', False),
            "is_zip_code": group_dict.get('is_zip_code', False),
            "is_building": group_dict.get('is_building', False),
            "is_relationship": group_dict.get('is_relationship', False),
            "is_marital_status": group_dict.get('is_marital_status', False),
            "is_official": group_dict.get('is_official', False),
            "is_first_name": group_dict.get('is_first_name', False),
            "is_last_name": group_dict.get('is_last_name', False),
            "is_campaign": group_dict.get('is_campaign', False),
            "is_activity": group_dict.get('is_activity', False),
            "is_sport": group_dict.get('is_sport', False),
            "is_language": group_dict.get('is_language', False),
            "location_id": group_dict.get('location_id'),
            "location_list_id": group_dict.get('location_list_id'),
            "coordinate": group_dict.get('coordinate'),
            "group_category_id": group_dict.get('group_category_id'),
            "system_id": group_dict.get('system_id'),
            "profile_id": group_dict.get('profile_id'),
            "system_group_name": group_dict.get('system_group_name'),
            "main_group_type_id": group_dict.get('main_group_type_id'),
            "is_event": group_dict.get('is_event', False),
            "event_id": group_dict.get('event_id'),
            "visibility_id": group_dict.get('visibility_id', 1),
        }

        group_id = super().insert(data_dict=group_data_dict, ignore_duplicate=ignore_duplicate)

        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
            if lang_code != LangCode.ENGLISH and lang_code != LangCode.HEBREW:
                lang_code = LangCode.ENGLISH
        group_ml_data_dict = {
            "lang_code": lang_code.value,
            "group_id": group_id,
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', False),
            "description": group_dict.get('description'),
            "created_user_id": user_context.get_effective_user_id(),
            "created_real_user_id": user_context.get_real_user_id(),
            "created_effective_user_id": user_context.get_effective_user_id(),
            "created_effective_profile_id": user_context.get_effective_profile_id(),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved'),
            "is_description_approved": group_dict.get('is_description_approved')
        }
        group_ml_id = super().insert(table_name="group_ml_table", data_dict=group_ml_data_dict,
                                     ignore_duplicate=ignore_duplicate)

        # Link group to group types
        group_types_ids = group_dict.get('group_types_ids', [])
        if group_dict.get('main_group_type_id') not in group_types_ids:
            group_types_ids.append(group_dict.get('main_group_type_id'))
        # TODO Do we need the group_group_types_ids shall we comment it /* group_group_types_ids = */?
        group_group_types_ids = self.link_group_to_group_types(group_id=group_id, group_type_ids=group_types_ids)
        #TODO Do we need to return the group_ml_id? Does anyone use it?
        return group_id, group_ml_id

    def upsert(self, *,  # noqa
               group_dict: Dict[str, any], data_dict_compare: dict = None,
               lang_code: LangCode = None, order_by: str = None) -> dict:
        """
            Returns the new group_id
            group_dict has to include the following
            for group_ml_table:
            title: str, lang_code: str = None,
            is_main_title: bool = True,
            "description": None,
            is_title_approved: bool = False,
            is_description_approved: bool = False
            for group_table:
            name: str,
            hashtag: str = None,
            is_approved: bool = None,
            parent_group_id: str = None,
            is_interest: bool = None,
            non_members_visibility_id: int = 1, members_visibility_id: int = 1
            created_user_id: int = 0
            example of group_dict:
            {
                "title": "title",
                "lang_code": "en",
                "name": "name",
                "hashtag": "hashtag",
                "is_approved": True,
                "parent_group_id": 1,
                "is_interest": True,
                "non_members_visibility_id": 1,
                "members_visibility_id": 1,
                "description": "description",
                "is_title_approved": True,
                "is_description_approved": True,
                "created_user_id": 1
            }
        """
        if group_dict.get("main_group_type_id") is None:
            self.logger.error("main_group_type_id is required", object={"group_dict": group_dict})
            raise Exception("main_group_type_id is required")
        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
            if lang_code != LangCode.ENGLISH and lang_code != LangCode.HEBREW:
                lang_code = LangCode.ENGLISH
        if not data_dict_compare:
            data_dict_compare = {
                "name": group_dict.get('name'),
            }
        group_data_dict = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved'),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
            "is_job_title": group_dict.get('is_job_title', False),
            "is_role": group_dict.get('is_role', False),
            "is_skill": group_dict.get('is_skill', False),
            "is_organization": group_dict.get('is_organization', False),
            "is_geo": group_dict.get('is_geo', False),
            "is_continent": group_dict.get('is_continent', False),
            "is_country": group_dict.get('is_country', False),
            "is_state": group_dict.get('is_state', False),
            "is_county": group_dict.get('is_county', False),
            "is_region": group_dict.get('is_region', False),
            "is_city": group_dict.get('is_city', False),
            "is_neighbourhood": group_dict.get('is_neighbourhood', False),
            "is_street": group_dict.get('is_street', False),
            "is_zip_code": group_dict.get('is_zip_code', False),
            "is_building": group_dict.get('is_building', False),
            "is_relationship": group_dict.get('is_relationship', False),
            "is_marital_status": group_dict.get('is_marital_status', False),
            "is_official": group_dict.get('is_official', False),
            "is_first_name": group_dict.get('is_first_name', False),
            "is_last_name": group_dict.get('is_last_name', False),
            "is_campaign": group_dict.get('is_campaign', False),
            "is_activity": group_dict.get('is_activity', False),
            "is_sport": group_dict.get('is_sport', False),
            "is_language": group_dict.get('is_language', False),
            "location_id": group_dict.get('location_id'),
            "location_list_id": group_dict.get('location_list_id'),
            "coordinate": group_dict.get('coordinate'),
            "group_category_id": group_dict.get('group_category_id'),
            "system_id": group_dict.get('system_id'),
            "profile_id": group_dict.get('profile_id'),
            "system_group_name": group_dict.get('system_group_name'),
            "main_group_type_id": group_dict.get('main_group_type_id'),
            "is_event": group_dict.get('is_event', False),
            "event_id": group_dict.get('event_id'),
            "visibility_id": group_dict.get('visibility_id', 1),
        }

        group_ml_data_dict = {
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', False),
            "description": group_dict.get('description'),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved'),
            "is_description_approved": group_dict.get('is_description_approved')
        }
        if "(" and ")" in group_dict.get('title'):
            group_id, group_ml_ids_list = super().upsert_value_with_abbreviations(
                table_name="group_table", data_dict=group_data_dict,
                data_ml_dict=group_ml_data_dict,
                ml_table_name="group_ml_table",
                lang_code=lang_code,
                data_dict_compare=data_dict_compare,
                compare_view_name="group_ml_also_not_approved_view",
                order_by=order_by
            )
        else:
            group_id, group_ml_id = super().upsert_value(
                data_dict=group_data_dict, data_ml_dict=group_ml_data_dict,
                ml_table_name="group_ml_table", data_dict_compare=data_dict_compare,
                lang_code=lang_code, compare_view_name="group_ml_also_not_approved_view",
                order_by=order_by
            )
            group_ml_ids_list = [group_ml_id]

        # Link group to group types
        group_types_ids = group_dict.get('group_types_ids', [])
        if group_dict.get('main_group_type_id') not in group_types_ids:
            group_types_ids.append(group_dict.get('main_group_type_id'))
        group_group_types_ids = self.link_group_to_group_types(group_id=group_id, group_type_ids=group_types_ids)
        upsert_information = {
            "group_id": group_id,
            "group_ml_ids_list": group_ml_ids_list,
            "group_group_types_ids": group_group_types_ids,
        }
        if group_dict.get("is_job_title"):
            insert_link_job_result_dict = self.__insert_link_job_title(
                group_dict=group_dict, group_id=group_id, group_ml_ids_list=group_ml_ids_list)
            upsert_information.update(insert_link_job_result_dict)

        # TODO Shall we add upsert_informaiton to the 

        return upsert_information

    def update(self, *, group_id: int, group_dict: Dict[str, any], lang_code: LangCode = None) -> None:

        group_data_dict = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved'),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
            "is_job_title": group_dict.get('is_job_title', False),
            "is_role": group_dict.get('is_role', False),
            "is_skill": group_dict.get('is_skill', False),
            "is_organization": group_dict.get('is_organization', False),
            "is_geo": group_dict.get('is_geo', False),
            "is_continent": group_dict.get('is_continent', False),
            "is_country": group_dict.get('is_country', False),
            "is_state": group_dict.get('is_state', False),
            "is_county": group_dict.get('is_county', False),
            "is_region": group_dict.get('is_region', False),
            "is_city": group_dict.get('is_city', False),
            "is_neighbourhood": group_dict.get('is_neighbourhood', False),
            "is_street": group_dict.get('is_street', False),
            "is_zip_code": group_dict.get('is_zip_code', False),
            "is_building": group_dict.get('is_building', False),
            "is_relationship": group_dict.get('is_relationship', False),
            "is_marital_status": group_dict.get('is_marital_status', False),
            "is_official": group_dict.get('is_official', False),
            "is_first_name": group_dict.get('is_first_name', False),
            "is_last_name": group_dict.get('is_last_name', False),
            "is_campaign": group_dict.get('is_campaign', False),
            "is_activity": group_dict.get('is_activity', False),
            "is_sport": group_dict.get('is_sport', False),
            "is_language": group_dict.get('is_language', False),
            "location_id": group_dict.get('location_id'),
            "location_list_id": group_dict.get('location_list_id'),
            "coordinate": group_dict.get('coordinate'),
            "group_category_id": group_dict.get('group_category_id'),
            "system_id": group_dict.get('system_id'),
            "profile_id": group_dict.get('profile_id'),
            "system_group_name": group_dict.get('system_group_name'),
            "main_group_type_id": group_dict.get('main_group_type_id'),
            "is_event": group_dict.get('is_event', False),
            "event_id": group_dict.get('event_id'),
            "visibility_id": group_dict.get('visibility_id', 1),
        }
        super().update_by_column_and_value(column_value=group_id, data_dict=group_data_dict)
        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
            if lang_code != LangCode.ENGLISH and lang_code != LangCode.HEBREW:
                lang_code = LangCode.ENGLISH
        group_ml_data_dict = {
            "group_id": group_id,
            "lang_code": lang_code.value,
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', True),
            "description": group_dict.get('description'),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved'),
            "is_description_approved": group_dict.get('is_description_approved')
        }
        where_clause = "group_id = %s AND lang_code = %s"
        super().update_by_where(
            table_name="group_ml_table",
            where=where_clause, params=(group_id, lang_code.value),
            data_dict=group_ml_data_dict
        )

    def get_group_dict_by_group_id(
            self, *, group_id: int, group_ml_id: int = None, view_name: str = "group_view",
            ml_view_name: str = "group_ml_also_not_approved_view") -> Dict[str, any]:

        group_ml_dict = {}
        if group_ml_id:
            group_ml_dict = self.select_one_dict_by_column_and_value(view_table_name=ml_view_name,
                                                                     column_value=group_ml_id,
                                                                     column_name="group_ml_id")
        group_dict = self.select_one_dict_by_column_and_value(view_table_name=view_name, column_value=group_id,
                                                              column_name="group_id")

        return {**group_dict, **group_ml_dict}

    def delete_by_group_id(self, group_id: int, group_ml_id: int = None) -> None:
        # Delete from group_table
        self.delete_by_column_and_value(table_name="group_table", column_name="group_id", column_value=group_id)
        # Delete from group_ml_table
        if group_ml_id:
            self.delete_by_column_and_value(table_name="group_ml_table", column_name="group_ml_id",
                                            column_value=group_ml_id)

    def get_groups_by_group_title(self, group_title: str) -> list:

        groups = []
        group_ids_dicts_list = self.select_multi_dict_by_column_and_value(
            view_table_name="group_ml_also_not_approved_view", column_value=group_title, column_name="title",
            select_clause_value="group_id, group_ml_id")
        for group_ids_dict in group_ids_dicts_list:
            group_dict = self.get_group_dict_by_group_id(
                group_id=group_ids_dict.get('group_id'), group_ml_id=group_ids_dict.get('group_ml_id'))
            groups.append(group_dict)

        return groups

    def get_all_groups_names(self, view_table_name: str = "group_ml_also_not_approved_view") -> list[str]:
        if "ml" in view_table_name:
            select_clause_value = "title"
        else:
            select_clause_value = "name"
        groups_names = self.select_multi_value_by_where(
            view_table_name=view_table_name,
            distinct=True,
            select_clause_value=select_clause_value
        )
        return groups_names

    def link_group_to_group_types(self, *, group_id: int, group_type_ids: list[int]) -> list[int]:
        group_group_types_ids = []
        for group_type_id in group_type_ids:
            # TODO I'm not sure we need group_group_type_data_dict since we moved from Changing generic_crud.insert() to generic_mapping.insert_mapping_if_not_exists()
            #group_group_type_data_dict = {
            #    "group_id": group_id,
            #    "group_type_id": group_type_id
            #}
            # TODO Shall this be insert or upsert? What happens if exists. Changing generic_crud.insert() to generic_mapping.insert_mapping_if_not_exists()
            group_group_type_id = self.group_group_type_generic_mapping.insert_mapping_if_not_exists(
                entity_id1= group_id
                , entity_id2= group_type_id
                , entity_name1="group"
                , entity_name2="group_type"
                #, table_name="group_group_type_table" # This was the parameter from the generic_crud.insert()
                #, data_dict=group_group_type_data_dict
                #, ignore_duplicate=True # This is not relevant when migrating from generic_crud.insert() to generic_mappping.insert_mapping_if_not_exists()
                )
            group_group_types_ids.append(group_group_type_id)
        return group_group_types_ids


    # TODO I would expect this to be in group_job_title.py and tested in test_group_job_title.py
    # TODO Shall this method be private?
    def __insert_link_job_title(self, group_dict: dict, group_id: int, group_ml_ids_list: list[int]) -> dict:
        group_ml_id = group_ml_ids_list[0] if group_ml_ids_list else None
        # Insert job title
        job_title_dict = {
            "job_title.name": group_dict.get('name'),
            "job_title_ml.title": group_dict.get('title'),
            "job_title_ml.is_title_approved": group_dict.get('is_title_approved'),
        }
        insert_job_result = self.job_local.insert_job_title(job_title_dict=job_title_dict)
        if insert_job_result:
            job_title_id, job_title_ml_id = insert_job_result
            self.logger.info("job_title inserted",
                             object={"job_title_id": job_title_id, "job_title_ml_id": job_title_ml_id})
        else:
            result_dict = {}
            return result_dict

        # Link job group_id to job title_id
        # TODO: add group_ml_id to select_clause_value when we have it in group_job_title_view
        group_job_title_dict = super().select_one_dict_by_where(
            schema_name="group_job_title", view_table_name="group_job_title_view",
            select_clause_value="group_job_title_id, job_title_id, job_title_ml_id, group_id",
            where="group_id = %s AND job_title_id = %s", params=(group_id, job_title_id))
        if group_job_title_dict:
            group_job_title_id = group_job_title_dict.get('group_job_title_id')
            if group_job_title_dict.get('job_title_ml_id') is None and group_job_title_dict.get('group_ml_id') is None:
                # update group_job_title
                group_job_title_id = super().update_by_column_and_value(
                    schema_name="group_job_title", table_name="group_job_title_table",
                    column_name="group_job_title_id", column_value=group_job_title_dict.get('group_job_title_id'),
                    data_dict={"job_title_ml_id": job_title_ml_id, "group_ml_id": group_ml_id}
                )
            elif group_job_title_dict.get('job_title_ml_id') is None:
                # update group_job_title
                group_job_title_id = super().update_by_column_and_value(
                    schema_name="group_job_title", table_name="group_job_title_table",
                    column_name="group_job_title_id", column_value=group_job_title_dict.get('group_job_title_id'),
                    data_dict={"job_title_ml_id": job_title_ml_id}
                )
            elif group_job_title_dict.get('group_ml_id') is None:
                # update group_job_title
                group_job_title_id = super().update_by_column_and_value(
                    schema_name="group_job_title", table_name="group_job_title_table",
                    column_name="group_job_title_id", column_value=group_job_title_dict.get('group_job_title_id'),
                    data_dict={"group_ml_id": group_ml_id}
                )
            result_dict = {
                "job_title_id": job_title_id,
                "job_title_ml_id": job_title_ml_id,
                "group_id": group_id,
                "group_ml_id": group_ml_id,
                "group_job_title_id": group_job_title_id
            }

            return result_dict
        data_dict = {
            "group_id": group_id,
            "job_title_id": job_title_id,
            "job_title_ml_id": job_title_ml_id
        }
        group_job_title_id = super().insert(
            schema_name="group_job_title", table_name="group_job_title_table",
            data_dict=data_dict, ignore_duplicate=True
        )
        result_dict = {
            "job_title_id": job_title_id,
            "job_title_ml_id": job_title_ml_id,
            "group_id": group_id,
            "group_ml_id": group_ml_id,
            "group_job_title_id": group_job_title_id
        }
        return result_dict
    
    def add_update_group_and_link_to_contact(
        self, *,  # noqa 
        group_dict: Dict[str, any], 
        contact_id: int, 
        data_dict_compare: dict = None,
        lang_code: LangCode = None,
        order_by: str = None
    ) -> dict:
        if not contact_id:
            raise ValueError("contact_id is required for linking")
        object_start = {
            "group_name": group_dict.get('name'),
            "contact_id": contact_id,
            "group_types": {k: v for k, v in group_dict.items() if k.startswith('is_') and v}
        }
        self.logger.start("add_update_group_and_link_to_contact", object=object_start)
        upsert_result = self.upsert(
            group_dict=group_dict,
            data_dict_compare=data_dict_compare,
            lang_code=lang_code,
            order_by=order_by)
        
        group_id = upsert_result.get("group_id")
        group_ml_ids = upsert_result.get("group_ml_ids_list", [])
        contact_groups = ContactGroups(is_test_data=self.is_test_data)
        contact_group_id = contact_groups.link_contact_to_existing_group_id(
            contact_id=contact_id,
            group_id=group_id,
            group_ml_ids_list=group_ml_ids
        )

        result = {
            **upsert_result,
            "contact_id": contact_id,
            "contact_group_id": contact_group_id
        }
        return result