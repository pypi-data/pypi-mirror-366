"""
THIS LIBRARY IS FOR SHARING DATA BETWEEN TWO OR MORE THAN
TWO SCRIPTS WITH <<SQL>> DATABASE,
BUT YOU CAN USE <<pybridge>> AS A SIMPLE DATABASE LIBRARY
"""
#::::::::::::::::::::::::::::::::::::::::::::::::::::
import os
from sqlite3 import connect


class bridge:
    """MAIN CLASS FOR SEND, SETUP AND RECEIVING"""

    def __init__(self, bridge_name, bridge_path):  # SETUP BRIDGE AND MAIN CLASS

        self.bridge_name = bridge_name  # OUR BRIDGE NAME
        self.bridge_path = bridge_path  # PATH TO BRIDGE DIRACTORY

        if os.path.exists(f"{self.bridge_path}"):

            self.dat = connect(f"{self.bridge_path}\\{self.bridge_name}.db")
            self.manager = self.dat.cursor()

            self.manager.execute(
                """
            CREATE TABLE IF NOT EXISTS data(id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            valu TEXT)
            """
            )
            self.dat.commit()

        else:

            raise FileNotFoundError(
                f"cannot find file: {self.bridge_path}\\{self.bridge_name}.db"
            )

    def send_to_bridge(self, **kwargs):  # SEND AND SAVE TO CREATED BRIDGE OR DATABASE

        """THIS FUNCTION SEND DATA TO SELECTED BRIDGE
        args:

        YOU MUST GIVE RECORDS TO FUNCTION WITH <<KEY&WORD ARGS>> => KWARGS

        EXAMPLE:

        bridge.send_to_bridge(name = 'jake', flower = 'beautiful')

        KEYS:  name , flower
        VALUES: jake , beautiful

        """

        for key, valu in kwargs.items():  # SENDING....

            query = f"""INSERT INTO data (key, valu) VALUES(?, ?)"""

            self.manager.execute(query, (str(key), str(valu)))

            self.dat.commit()

        return "data sended to bridge: " + f"{self.bridge_path}\\{self.bridge_name}.db"

    def receive_from_bridge(
        self, all=True, find_key=None, on_delete=False
    ):  # RECEIVE DATA FROM SELECTED BRIDGE

        """THIS FUNCTION RETURNS DATA FROM SELECTED BRIDGE
        args:

        all : RETURNS ALL RECORDS
        find_key : YOU CAN FILTER RECORDS BASED ON THEIR KEYS
        on_delete : DELETES ALL FOUNDED RECORDS WHEN IT IS <<TRUE>>

        """

        if all == True:

            if find_key:

                query = """SELECT key, valu FROM data WHERE key = ?"""
                self.manager.execute(query, (str(find_key),))
                data = self.manager.fetchall()

                if on_delete == True:

                    self.manager.execute(
                        f"""DELETE  FROM data WHERE key = ?""", (str(find_key),)
                    )
                    self.dat.commit()

                return data

            else:

                query = """SELECT key, valu FROM data"""
                self.manager.execute(query)
                data = self.manager.fetchall()

                if on_delete == True:

                    self.manager.execute(f"""DELETE  FROM data""")
                    self.dat.commit()

                return data

        elif all == False:

            if find_key:

                query = """SELECT key, valu FROM data WHERE key = ?"""
                self.manager.execute(query, (str(find_key),))

                try:
                    data = self.manager.fetchall()[-1]
                except:
                    data = self.manager.fetchall()[-1]

                if on_delete == True:

                    self.manager.execute(
                        f"""DELETE  FROM data WHERE key = ?""", (str(find_key),)
                    )
                    self.dat.commit()

                return data

            else:

                raise AttributeError(
                    "cannot set parameter all = False and find_key = None"
                )

    def delete_bridge_data(
        self, find_key=None
    ):  # FOR DELETING DATAS FROM SELECTED BRIDGE

        if find_key:

            query = """DELETE FROM data WHERE key = ?"""
            self.manager.execute(query, (str(find_key),))
            self.dat.commit()

        else:

            self.manager.execute(f"""DELETE  FROM data""")
            self.dat.commit


"""
THIS PACAKGE IS DEVELOPED BY <<MRT>> => (MOHAMMAD REZA TAGHDIRI) A PERSIAN PROGRAMER.

I HOPE THAT <<pybridge>> MAKE SOME WORKS EASIER FOR YOU....

"""
