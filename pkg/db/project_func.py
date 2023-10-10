from typing import List

from loguru import logger
from pydantic import parse_obj_as, TypeAdapter

from pkg.db.db_connect import connect_to_db
from pkg.db.models.project import Project


@logger.catch
async def add_new_project(project_name: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на добавление нового проекта')
        await conn.execute(
            'INSERT INTO projects (project_name) '
            'VALUES ($1);',
            project_name
        )


@logger.catch
async def attach_tl_to_project(project_name: str, team_lead: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на определение тимлида на проект')
        await conn.execute(
            'UPDATE projects '
            'SET team_lead = $1 '
            'WHERE project_name = $2;',
            team_lead, project_name
        )


@logger.catch
async def get_all_projects() -> List[Project]:
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на получение всех проектов')
        rec = await conn.fetch(
            'SELECT '
            'project_id, project_name, team_lead '
            'FROM projects;'
        )
    # result = parse_obj_as(List[Project], rec)
    # return result
    if rec is None:
        return None
    rec_dict = [dict(i) for i in rec]
    data = TypeAdapter(List[Project]).validate_python(rec_dict)
    return data



@logger.catch
async def delete_project_by_name(project_name: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на удаление проекта через название')
        await conn.execute(
            'DELETE FROM projects '
            'WHERE project_name = $1;',
            project_name
        )


@logger.catch
async def update_project_name(old_name: str, new_name: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на изменение названия проекта')
        await conn.execute(
            'UPDATE projects '
            'SET project_name = $1 '
            'WHERE project_name = $2;',
            new_name,
            old_name
        )


if __name__ == '__main__':
    pass
