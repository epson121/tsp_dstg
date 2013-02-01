# Created by: Vizing
#
# This software has been tested on Ubuntu 12.04 x64 version
#
# To use this software you need to have the following prerequisites:
# googlemaps wrapper for python (http://sourceforge.net/projects/py-googlemaps/files/) or (easy_install googlemaps)
# networkx (easy_install networkx)




from __future__ import print_function

api_key = "AIzaSyBFtxCbh71ooDciJropvzvgcAWv84Ob2Bc"
from googlemaps import GoogleMaps
import math
import networkx as nx
import pylab
import time
import itertools

gmaps = GoogleMaps(api_key)


#pizza places addresses
P = ["Kolodvorska ulica 20 , Varazdin",	 "P"]
A = ["Zagrebacka ulica 40, Varazdin", 	 "A"]
B = ["Medimurska ulica 27, Varazdin",	 "B"]
C = ["Hallerova aleja 12, Varazdin",	 "C"]
D = ["Jalkovecka ulica 7, Varazdin",	 "D"]
E = ["Gospodarska ulica 13, Varazdin",	 "E"]
F = ["Zagrebacka ulica 203, Varazdin",	 "F"]
G = ["Optujska ulica 79, Varazdin",		 "G"]
H = ["Ulica Baruna Trenka 15, Varazdin", "H"]


pizza_places = [P, A, B, C, D, E, F, G, H]
pp_no_start = ["A", "B", "C", "D", "E", "F", "G", "H"]
gps_c = []
pizza_places_gps_coords = {}

#find gps coords (v1)
def find_gps_coords(places):
	gps_coords = []
	gps_coords_dictionary =  {}
	for elem in places:
		lat, lng = gmaps.address_to_latlng(elem[0])
		#{elem : [lat, lng]}
		gps_coords_dictionary[elem[1]]  = [lat, lng]

		# [elem, lat, lng]
		gps_coords.append([elem[1], lat, lng])
	return gps_coords_dictionary, gps_coords

#find gps coords (v2)
def find_gps(p1, p2):
	coords = []
	lat1, lng1 = gmaps.address_to_latlng(p1)
	time.sleep(0.9)
	lat2, lng2 = gmaps.address_to_latlng(p2)
	return [lat1, lng1], [lat2, lng2]

#calculate distance from 2 points
#point format [lat, lng]
def distance_on_unit_sphere(a, b):
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - a[0])*degrees_to_radians
    phi2 = (90.0 - b[0])*degrees_to_radians
        
    # theta = longitude
    theta1 = a[1]*degrees_to_radians
    theta2 = b[1]*degrees_to_radians
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    return arc * 6373;

#Draw a starting graph with edge labels
def create_starting_graph():
	G = nx.Graph()
	print('Adding nodes...')
	for elem in pizza_places:
		G.add_node(elem[1])
	print('Adding edges')
	counter = 1

	#add edges and weights (find_gps and distance_on_unit_sphere)
	for i in range(0, len(pizza_places)):
		j = i + 1;
		while (j < len(pizza_places)):
			gps1, gps2 = find_gps(pizza_places[i][0], pizza_places[j][0])
			distance = distance_on_unit_sphere(gps1, gps2) 
			G.add_edge(pizza_places[i][1], pizza_places[j][1], weight = distance)
			print("edge addded %d/36" % counter)
			j += 1
			counter += 1
	pos = nx.spring_layout(G)
	print("Finished")

	# specifiy edge labels explicitly
	pylab.figure(1)
	nx.draw(G,pos)
	edge_labels=dict([((u,v,), round(d['weight'],2))
	             for u,v,d in G.edges(data=True)])
	
	#save graph to image
	nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
	pylab.savefig("_starting_graph.png")
	print("Image saved as '_starting_graph.png'.")


def create_ending_graph(l, w):
	G = nx.Graph()
	for elem in l:
		G.add_node(elem)

	for i in range(0, len(l)-1):
		G.add_edge(l[i], l[i+1], weight = w[i])
	
	pos = nx.spring_layout(G)

	# specifiy edge labels explicitly
	pylab.figure(2)
	nx.draw(G,pos)
	edge_labels=dict([((u,v,), round(d['weight'],2))
	             for u,v,d in G.edges(data=True)])
	
	#save graph to image
	nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
	pylab.savefig("_ending_graph.png")
	print("Image saved as '_ending_graph.png'.")


def bruteForce(lis):
	print('Starting bruteforce checking of permutations:')
	distances_from_P = {}
	s = 0
	#calculate distance from P to first element and from last element to P
	for elem in lis:
		g1 = pizza_places_gps_coords["P"]
		g2 = pizza_places_gps_coords[elem[0]]
		g3 = pizza_places_gps_coords[elem[-1]]
		first_distance = distance_on_unit_sphere(g1, g2)
		last_distance = distance_on_unit_sphere(g1, g3)
		distances_from_P[elem] = [first_distance, last_distance]
		

	#set some needed variables
	min_dist = 100
	min_list = []
	min_weights = []
	#loop through the permutations
	for elem in lis:
		distance = 0
		weights = []
		weights.append(distances_from_P[elem][0])

		#traverse a single permutation
		for i in range(0, len(elem)-1):
			d = distance_on_unit_sphere(pizza_places_gps_coords[elem[i]], pizza_places_gps_coords[elem[i+1]])
			distance += d
			weights.append(d)

		#calculate distance
		distance += distances_from_P[elem][0] + distances_from_P[elem][1]
		weights.append(distances_from_P[elem][1])
		if (distance < min_dist):
			min_dist = distance
			min_list = elem
			min_weights = weights
	print("Minimal distance achieved while traversing (start from P and end in P): ", min_list)
	print("Minimal distance is:", min_dist, "km")
	return [min_list, min_weights]

def main():
	global pizza_places_gps_coords
	print('Fetching GPS coordinates...')
	pizza_places_gps_coords, gps_c = find_gps_coords(pizza_places)
	permutations = list(itertools.permutations(pp_no_start))

	print('Creating starting_graph...This could take a while...')
	#create_starting_graph()

	res = bruteForce(permutations)
	
	r = list(res[0])
	r.insert(0, 'P')
	r.insert(len(r), 'P')

	w = list(res[1])

	print('Creating ending_graph')
	create_ending_graph(r, w)

	#check by hand the fastest route
	'''
	print("Distance from", gps_c[0][0], " and ", gps_c[2][0], " is:")
	distance1 = distance_on_unit_sphere([gps_c[0][1], gps_c[0][2]], [gps_c[2][1], gps_c[2][2]])
	print(distance1)
	print("Distance from", gps_c[2][0], " and ", gps_c[8][0], " is:")
	distance2 = distance_on_unit_sphere([gps_c[2][1], gps_c[2][2]], [gps_c[8][1], gps_c[8][2]])
	print(distance2)
	print("Distance from", gps_c[8][0], " and ", gps_c[7][0], " is:")
	distance3 = distance_on_unit_sphere([gps_c[8][1], gps_c[8][2]], [gps_c[7][1], gps_c[7][2]])
	print(distance3)
	print("Distance from", gps_c[7][0], " and ", gps_c[3][0], " is:")
	d4 = distance_on_unit_sphere([gps_c[7][1], gps_c[7][2]], [gps_c[3][1], gps_c[3][2]])
	print(d4)
	print("Distance from", gps_c[3][0], " and ", gps_c[4][0], " is:")
	d5 = distance_on_unit_sphere([gps_c[3][1], gps_c[3][2]], [gps_c[4][1], gps_c[4][2]])
	print(d5)
	print("Distance from", gps_c[4][0], " and ", gps_c[1][0], " is:")
	d6 = distance_on_unit_sphere([gps_c[4][1], gps_c[4][2]], [gps_c[1][1], gps_c[1][2]])
	print(d6)
	print("Distance from", gps_c[1][0], " and ", gps_c[5][0], " is:")
	d7 = distance_on_unit_sphere([gps_c[1][1], gps_c[1][2]], [gps_c[5][1], gps_c[5][2]])
	print(d7)
	print("Distance from", gps_c[5][0], " and ", gps_c[6][0], " is:")
	d8 = distance_on_unit_sphere([gps_c[5][1], gps_c[5][2]], [gps_c[6][1], gps_c[6][2]])
	print(d8)
	print("Distance from", gps_c[6][0], " and ", gps_c[0][0], " is:")
	d9 = distance_on_unit_sphere([gps_c[6][1], gps_c[6][2]], [gps_c[0][1], gps_c[0][2]])
	print(d9)
	d_total = distance1 + distance2 + distance3 + d4 + d5 + d6 + d7 + d8 + d9
	print("Total distance is : ", d_total)
	'''

if __name__ == "__main__":
    main()

