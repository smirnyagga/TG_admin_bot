from loguru import logger

from pkg.db.department_func import get_all_departments
from pkg.db.project_func import get_all_projects


@logger.catch
async def is_department_available(name):
    logger.info(f'Вызов функции is_department_available со значением {name}')
    departments = await get_all_departments()
    department_list = [i_elem.department for i_elem in departments]
    return name in department_list


async def is_project_available(name):
    logger.info(f'Вызов функции is_project_available со значением {name}')
    projects = await get_all_projects()
    project_list = [i_elem.project_name for i_elem in projects]
    return name in project_list
