import yaml
import sys
import os
import mysql.connector

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

class ReminderLoop:

    async def checkReminders(self, bot):
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"]
        )
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute("SELECT * FROM dad.reminders WHERE remind_time <= NOW()")

        for m in mycursor.fetchall():
            print(m)
            for channel in bot.get_all_channels():
                try:
                    msg = await channel.fetch_message(m[2])
                except:
                    continue
                try:
                    await msg.reply("Reminded.")
                    break
                except:
                    pass
        
        # mycursor.execute("DELETE FROM dad.reminders WHERE remind_time <= NOW()")

        mydb.commit()
        mycursor.close()