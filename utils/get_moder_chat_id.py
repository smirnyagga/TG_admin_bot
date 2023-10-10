from pkg.db.user_func import get_tg_id_if_moderator


# class ModeratorUtils:           # Что-то бесполезное
#     BLACK_LIST = []
#
#     @classmethod
#     async def get_random_moder(cls):
#         moderator_id_list = await get_tg_id_if_moderator()
#         for moderator_id in moderator_id_list:
#             if moderator_id not in cls.BLACK_LIST:
#                 cls.BLACK_LIST.append(moderator_id)
#                 if len(moderator_id_list) == len(cls.BLACK_LIST):
#                     cls.BLACK_LIST = []
#                 return moderator_id
