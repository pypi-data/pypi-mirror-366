from pathlib import Path

from rosbags.highlevel import AnyReader

# Create reader instance and open for reading.
with AnyReader([Path('tests/demo.bag')]) as reader:
  connections = [x for x in reader.connections]
  start_time = reader.start_time      # 纳秒时间戳
  end_time = reader.end_time          # 纳秒时间戳  
  duration = reader.duration          # 持续时间(纳秒)
  message_count = reader.message_count # 总消息数
  
  print(f"Start time: {start_time}")
  print(f"End time: {end_time}")
  print(f"Duration: {duration}")
  print(f"Message count: {message_count}")
  # print(f"Connections: {connections}")
  print(reader.default_typestore)
  print(reader.typestore)
  # print(reader.typestore.get_type_info('std_msgs/Header'))
  
  connections = [x for x in reader.connections if x.topic == '/imu_raw/Imu']
  print(connections)
  for connection, timestamp, rawdata in reader.messages(connections=connections):
    msg = reader.deserialize(rawdata, connection.msgtype)
    print(connection.msgtype)
    # print(msg)

         