# import yaml
# import sys
# import os
# import mysql.connector

# if not os.path.isfile("config.yaml"):
#     sys.exit("'config.yaml' not found! Please add it and try again.")
# else:
#     with open("config.yaml") as file:
#         config = yaml.load(file, Loader=yaml.FullLoader)

# class ReminderLoop:
#     def __init__(self):
#         # self.mydb = mysql.connector.connect(
#         #     host=config["dbhost"],
#         #     user=config["dbuser"],
#         #     password=config["dbpassword"],
#         #     database=config["databasename"]
#         # )

#     # async def checkReminders(self, bot):
#     #     mycursor = self.mydb.cursor(buffered=True)

#     #     mycursor.execute("SELECT * FROM reminders WHERE remind_time <= NOW()")

#     #     for m in mycursor:
#     #         for channel in bot.get_all_channels():
#     #             try:
#     #                 msg = await channel.fetch_message(m[2])
#     #             except:
#     #                 continue
#     #             try:
#     #                 await msg.reply("Reminded.")
#     #                 break
#     #             except:
#     #                 pass
        
#     #     mycursor.execute("DELETE FROM reminders WHERE remind_time < NOW()")

#     #     self.mydb.commit()