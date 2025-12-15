import re

from database_utils import DatabaseUtils

class CommonUtils:
    _stream_pattern = re.compile(r"(//[a-zA-Z0-9.\-_]+/[a-zA-Z0-9.\-_]+)")

    @staticmethod
    def get_project_stream(project_name: str) -> str:
        stream_match = CommonUtils._stream_pattern.search(project_name)
        if stream_match is not None:
            return stream_match.group(1)
        return project_name

    @staticmethod
    async def find_or_add_project(project_name: str | None) -> int:
        if not isinstance(project_name, str) or len(project_name) == 0:
            return None

        sql = """
            INSERT INTO ugs_db.Projects (Name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE Id=LAST_INSERT_ID(Id)
        """

        return await DatabaseUtils.execute_sql(sql, (project_name,))

    @staticmethod
    async def find_or_add_user(user_name: str | None) -> int:
        if not isinstance(user_name, str) or len(user_name) == 0:
            return None

        sql = """
            INSERT INTO ugs_db.Users (Name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE Id=LAST_INSERT_ID(Id)
        """

        return await DatabaseUtils.execute_sql(sql, (user_name,))
