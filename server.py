import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import sensor
import sqlite3
import time

#sensor initialization
sensor = sensor.sensor()

#database connection
conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()
 
 
print("test")

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('new connection')
      
    def on_message(self, message):
        print('message received:  %s' % message)
        message = message.split(",")
        
        if message[0] == "read_single": #Read a single temp/humidity pair
            print("Read Single")        
        
            t_alert = float(message[1])
            h_alert = float(message[2])

            #Read the sensor once
            now, temp, hum = sensor.read()
            
            #insert into sqlite3 database
            cmd = f"""INSERT INTO data ('timestamp', 'temperature', 'humidity') VALUES ('{now}', {temp}, {hum})"""
            cursor.execute(cmd)
            conn.commit()
            
            #Check for Temperature/humidity alerts    
            over_temp = False
            if temp >= t_alert:
                over_temp = True
                
            over_hum = False
            if hum >= h_alert:
                over_hum = True                
            
            self.write_message(f"read_single,{temp},{hum},{over_temp},{over_hum}")
            
        elif message[0] == "read_10x":  #Read a 10x temp/humidity pair @ 1 second apart
            for i in range(10):
                now, temp, hum = sensor.read()
                
                #insert into sqlite3 database
                cmd = f"""INSERT INTO data ('timestamp', 'temperature', 'humidity') VALUES ('{now}', {temp}, {hum})"""
                cursor.execute(cmd)

                t_alert = float(message[1])
                h_alert = float(message[2])


                #Check for Temperature/humidity alerts    
                over_temp = False
                if temp >= t_alert:
                    over_temp = True
                    
                over_hum = False
                if hum >= h_alert:
                    over_hum = True                    
                
                print(f"read_10x {i}")
                done = "done" if i == 9 else "next"
                self.write_message(f"read_10x,{i+1},{temp},{hum},{over_temp},{over_hum},{done}")                
                time.sleep(1)
                
                
            conn.commit()
            
        elif message[0] == "calculate_statistics": #calculate stats on the last 10 points in the database
        
            #fetch last 10 rows from the database
            cmd = "SELECT * from data ORDER BY id DESC LIMIT 10"
            result = cursor.execute(cmd).fetchall()
        
            temps = []
            humidities = []
        
            for row in result:
                temps.append(round(row[2], 2))
                humidities.append(round(row[3], 2))
                
                self.write_message(f"calculate_statistics,{min(temps)},{max(temps)},{round(sum(temps)/len(temps),2)},{min(humidities)},{max(humidities)},{round(sum(humidities)/len(humidities),2)}")        
        
        
            
        else:   
            print("unrecognized message", message)            
            
 
    def on_close(self):
        print('connection closed')
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()
