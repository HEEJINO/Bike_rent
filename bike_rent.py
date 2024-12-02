import pandas as pd
import tkinter as tk
from tkinter import messagebox
import folium
import osmnx as ox
import networkx as nx
import os
import webbrowser

# 사용자와 자전거 대여소 좌표
user_location = (37.448849, 127.127125)  # 서울 광장동

# CSV 파일에서 자전거 대여소 좌표 가져오기
def load_bike_stations(csv_path):
    bike_data = pd.read_csv(csv_path, encoding='cp949') # cp949는 한글 인코딩용 숫자
    return list(zip(bike_data['위도'], bike_data['경도']))

# 자전거 대여소 좌표를 CSV에서 불러오기
csv_file_path = '전국자전거대여소표준데이터.csv'
bike_stations = load_bike_stations(csv_file_path)

# 현재 디렉토리에 map.html 저장
map_file = os.path.join(os.getcwd(), "map.html")

def calculate_nearest_station(user_location, stations):
    graph = ox.graph_from_point(user_location, dist=5000, network_type='walk')  #최대 탐색 거리는 5000m로 설정
    user_node = ox.distance.nearest_nodes(graph, user_location[1], user_location[0])
    station_nodes = [ox.distance.nearest_nodes(graph, station[1], station[0]) for station in stations]

    distance, path = nx.single_source_bellman_ford(graph, user_node, weight='length')

    min_distance = float('inf')
    nearest_station_node = None
    shortest_path = None

    for station_node in station_nodes:
        if station_node in distance and distance[station_node] < min_distance:
            min_distance = distance[station_node]
            nearest_station_node = station_node
            shortest_path = path[station_node]

    return nearest_station_node, min_distance, shortest_path, graph

def show_map():
    nearest_station_node, min_distance, shortest_path, graph = calculate_nearest_station(user_location, bike_stations)
    shortest_path_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]
    nearest_station_coords = (graph.nodes[nearest_station_node]['y'], graph.nodes[nearest_station_node]['x'])

    print(f"가장 가까운 대여소 좌표: {nearest_station_coords}")
    print(f"가장 가까운 대여소까지의 거리: {min_distance:.2f}m")

    messagebox.showinfo(
        "가장 가까운 대여소 정보",
        f"대여소 위치 (위도, 경도): {nearest_station_coords}\n거리: {min_distance:.2f}m"
    )

    m = folium.Map(location=user_location, zoom_start=10)
    folium.Marker(user_location, popup="사용자 위치", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(nearest_station_coords, popup="가장 가까운 대여소", icon=folium.Icon(color="green")).add_to(m)
    folium.PolyLine(shortest_path_coords, color="red", weight=5, opacity=0.8, popup="최단 경로").add_to(m)
    
    m.save(map_file)
    webbrowser.open(f"file:///{os.path.normpath(map_file).replace(os.sep, '/')}")

root = tk.Tk()
root.title("자전거 대여소 찾기")

if not os.path.exists(os.path.dirname(map_file)):
    os.makedirs(os.path.dirname(map_file))

button = tk.Button(root, text="가장 가까운 대여소 찾기", command=show_map)
button.pack()

root.mainloop()
