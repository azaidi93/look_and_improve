from pymongo import MongoClient
from xml.dom import minidom
import xml.etree.ElementTree as ET


def upload_data():
    db = client.quiz
    tree = ET.parse('vocab.xml')
    root = tree.getroot()

    for child in root:
        word = child.tag
        level = child.text

        db.vocab.insert(
            {
                "word" : word,
                "level" : level

            }
        )

def create_user(db_client, username):
    db = db_client.quiz

    db.user.insert(
        {
            "name": username,
            "current_s": 0,
            "curr_word": "",
            "q_table": {
                "A1_b": 0,
                "A1_r": 1,
                "A1_f": 0,
                "A2_b": 0,
                "A2_r": 1,
                "A2_f": 0,
                "B1_b": 0,
                "B1_r": 1,
                "B1_f": 0,
                "B2_b": 0,
                "B2_r": 1,
                "B2_f": 0,
                "C1_b": 0,
                "C1_r": 1,
                "C1_f": 0,
                "C2_b": 0,
                "C2_r": 1,
                "C2_f": 0,
            },
            "vocab":{
                    "bike": {
                        "attempts": 0,
                        "incorrect": 0,
                        "correct": 0,
                        "current_s": 0,
                        "q_table":{
                            "active_r": 0.1,
                            "active_t": 0,
                            "i_active_r": 0,
                            "i_active_t": 0
                        }
                    },

            },


        }
    )

if __name__ == '__main__':
    client = MongoClient('mongodb://127.0.0.1:27017/')
    create_user(client, "Ahmed Zaidi")
