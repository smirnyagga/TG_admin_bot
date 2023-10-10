from typing import List

from loguru import logger
from pydantic import parse_obj_as, TypeAdapter

from pkg.db.db_connect import connect_to_db
from pkg.db.models.department import Department


@logger.catch
async def add_new_department(department: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на добавление нового департамента')
        await conn.execute(
            'INSERT INTO departments (department) '
            'VALUES ($1);',
            department
        )


@logger.catch
async def attach_tl_to_department(department: str, team_lead: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на определение тимлида в отдел')
        await conn.execute(
            'UPDATE departments SET team_lead = $1 '
            'WHERE department = $2;',
            team_lead,
            department
        )


@logger.catch
async def get_department_by_id(department_id: int) -> Department:
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на получение отдела через ID')
        rec = await conn.fetchrow(
            'SELECT '
            'department_id, department, team_lead '
            'FROM departments '
            'WHERE department_id = $1;',
            department_id
        )
    # data = parse_obj_as(Department, rec)
    # return data
    if rec is None:
        return None
    rec_dict = [dict(rec)]
    data = TypeAdapter(List[Department]).validate_python(rec_dict)
    return data[0]


@logger.catch
async def get_all_departments() -> List[Department]:
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на получение всех отделов')
        rec = await conn.fetch(
            'SELECT '
            'department_id, department, team_lead '
            'FROM departments;'
        )
    # result = parse_obj_as(List[Department], rec)
    # return result
    if rec is None:
        return None
    rec_dict = [dict(i) for i in rec]
    data = TypeAdapter(List[Department]).validate_python(rec_dict)
    return data


@logger.catch
async def delete_department_by_id(department_id: int):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на удаление отдела через ID')
        await conn.execute(
            'DELETE FROM departments '
            'WHERE department_id = $1;',
            department_id
        )


@logger.catch
async def delete_department_by_name(department_name: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на удаление отдела через название')
        await conn.execute(
            'DELETE FROM departments '
            'WHERE department = $1;',
            department_name
        )


@logger.catch
async def update_department_name(old_name: str, new_name: str):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на изменение названия отдела')
        await conn.execute(
            'UPDATE departments '
            'SET department = $1 '
            'WHERE department = $2;',
            new_name,
            old_name
        )


@logger.catch
async def update_department_by_id(department_id: int, data: Department):
    async with connect_to_db() as conn:
        logger.info('Запрос в БД на изменение названия и тимлида отдела')
        await conn.execute(
            'UPDATE departments '
            'SET department = $1, team_lead = $2 '
            'WHERE department_id = $3;',
            data.department,
            data.team_lead,
            department_id
        )


if __name__ == '__main__':
    pass
