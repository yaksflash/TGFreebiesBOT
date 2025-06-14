import logging
import asyncio

from handlers.start import startRouter
from handlers.profile import profileRouter
from handlers.activate_promocode import activatePromocodeRouter
from handlers.invite import inviteRouter
from handlers.folders import foldersRouter
from handlers.giveaways import giveawaysRouter
from handlers.admin.adm_folders import admFoldersRouter
from handlers.admin.adm_starsbank import starsbankRouter
from handlers.admin.folder_updated import admFolderUpdatedRouter
from handlers.admin.admin_givlist import adminGiveawaysRouter
from handlers.admin.adm_promocodes import admPromocodesRouter
from handlers.ai_manager import differentTextRouter
from handlers.startmess_buttons.sm_giveaways import smGiveawayRouter
from handlers.startmess_buttons.sm_profile import smProfileRouter
from handlers.startmess_buttons.sm_earnstars import smEarnStarsRouter
from handlers.startmess_buttons.back_to_main_menu import backToMenuRouter
from handlers.startmess_buttons.sm_withdrawstars import smWithdrawStarsRouter
from handlers.admin.withdraw_stars import admWithdrawStarsRouter
from handlers.startmess_buttons.sm_information import smInformationRouter
from handlers.startmess_buttons.sm_folders import smFoldersRouter
from loader import bot, dp
from do_folder_mall import time_checker
from folder_channel_mall import send_banner_if_20
from middlewares.sub_check import check_subscription
dp.message.middleware(check_subscription)
dp.callback_query.middleware(check_subscription)

from middlewares.antiflood import antiflood_middleware
# Подключаем как middleware
dp.message.middleware(antiflood_middleware)
dp.callback_query.middleware(antiflood_middleware)

async def main():
    routers = [startRouter, admPromocodesRouter, activatePromocodeRouter, admFolderUpdatedRouter, 
               adminGiveawaysRouter, starsbankRouter, smFoldersRouter, smInformationRouter, admWithdrawStarsRouter, 
               backToMenuRouter, smWithdrawStarsRouter, profileRouter, inviteRouter, foldersRouter, giveawaysRouter, 
               admFoldersRouter, smGiveawayRouter, smProfileRouter, smEarnStarsRouter, differentTextRouter]
    for router in routers:
        dp.include_router(router)
    
    asyncio.create_task(time_checker(bot))
    asyncio.create_task(send_banner_if_20(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    asyncio.run(main())