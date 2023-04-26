from flask import Flask
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
engine = create_engine(
    "postgresql://postgres:ahRbK9ywMU88xuidBLlh@containers-us-west-42.railway.app:5809/railway")
metadata_obj = MetaData(bind=engine)
MetaData.reflect(metadata_obj)
sensors = metadata_obj.tables["sensor-data"]
wifi = metadata_obj.tables["wifi-data"]
locs = metadata_obj.tables["predicted-locations"]

app = Flask(__name__)
def insertInDb(user_name, chat_id, product_name, product_link, product_price, lowest_price, message_id, availability=False):
    with Session(engine) as session:
        insert_stmnt = prices.insert().values(user_name=user_name,
                                              chat_id=chat_id,
                                              product_name=product_name,
                                              product_link=product_link,
                                              product_price=product_price,
                                              lowest_price=lowest_price,
                                              availability=availability,
                                              message_id=message_id)
        session.execute(insert_stmnt)

        session.commit()
@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/sensor-reading' , methods = ['POST'])
def hello_world():
    if request.method == 'POST':
        ax = request.json.get('ax')
        ay= request.json.get('ay')
        az = request.json.get('az')
        gx = request.json.get('gx')
        gy = request.json.get('gy')
        gz = request.json.get('gz')
        mx = request.json.get('mx')
        my = request.json.get('my')
        mz = request.json.get('mz')
        mac1 =  request.json.get('mac1')
        mac2 =  request.json.get('mac2')
        mac3 =  request.json.get('mac3')
        lng =  request.json.get('long')
        lat =  request.json.get('lat')
        insertInDb()







if __name__ == '__main__':
   app.run(debug = True)