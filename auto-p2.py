#!/usr/bin/python

import sys
import json
import urllib
from urllib.request import urlopen
from subprocess import call
from lxml import etree

orden = sys.argv[1]

if orden == 'prepare':

	if len(sys.argv) == 3:
		aux = sys.argv[2]
	else:
		aux = '3'

	if aux > '5' or aux < '1':
		print('Parámetro incorrecto, por favor introduce un número entre 1-5')
		
	else:
		print ('Preparo '+aux+' VM')

		#Creamos el archivo json
		data = {}
		data['servers'] = []
		data['servers'].append({
			'num_serv': aux})
		with open('auto-p2.json', 'w') as file:
			json.dump(data, file, indent=4)

		#Creación de sistemas de ficheros COW para las MVs
		i = 1
		while i <= int(aux):
			call(['qemu-img', 'create', '-f', 'qcow2', '-b', 'cdps-vm-base-pc1.qcow2', 's'+str(i)+'.qcow2'])
			i = i+1
		call(['qemu-img', 'create', '-f', 'qcow2', '-b', 'cdps-vm-base-pc1.qcow2', 'lb.qcow2'])
		call(['qemu-img', 'create', '-f', 'qcow2', '-b', 'cdps-vm-base-pc1.qcow2', 'c1.qcow2'])

		#cambiamos archivos xml
		def pause(): 
	    		p = input("Press <ENTER> key to continue...") 

		n = 1
		while n <= int(aux):
			
			#cargamos el fichero xml
			tree = etree.parse('plantilla-vm-pc1.xml')

			#obtenemos el nodo raiz e imprimimos su nombre y el valor de atributo tipo
			root = tree.getroot()
			print(root.tag)
			print(root.get("type"))
			pause()
			
			#buscamos la etiqueta, imprimimos su nombre y su valor y luego lo cambiamos
			name = root.find("name")
			print(name.text)
			name.text = 's'+str(n)
			print(name.text)
			pause()

			source = root.find("./devices/disk/source")
			print(source.get("file"))
			source.set('file', '/home/daniel.sanz.sobrino/PracticaLibre1/s'+str(n)+'.qcow2')
			print(source.get("file"))
			pause()

			source_bridge = root.find("./devices/interface[@type='bridge']/source")
			print(source_bridge.get("bridge"))
			source_bridge.set("bridge", "LAN2")
			print(source_bridge.get("bridge"))
			pause()
			

			f = open('s'+str(n)+'.xml', 'w')
			f.write(etree.tounicode(tree, pretty_print=True))
			f.close()
			pause()
			n = n+1

		tree = etree.parse('plantilla-vm-pc1.xml')

		root = tree.getroot()
		print(root.tag)
		print(root.get("tipo"))
		pause()

		name = root.find("name")
		name.text = 'c1'
		print(name.text)
		pause()

		source = root.find("./devices/disk/source")
		print(source.get("file"))
		source.set('file', '/home/daniel.sanz.sobrino/PracticaLibre1/c1.qcow2')
		print(source.get("file"))
		pause()

		source_bridge = root.find("./devices/interface[@type='bridge']/source")
		print(source_bridge.get("bridge"))
		source_bridge.set("bridge", "LAN1")
		print(source_bridge.get("bridge"))
		pause()
		
		f = open('c1.xml', 'w')
		f.write(etree.tounicode(tree, pretty_print=True))
		f.close()
		pause()

		tree = etree.parse('plantilla-vm-pc1.xml')

		root = tree.getroot()
		print(root.tag)
		print(root.get("tipo"))
		pause()

		name = root.find("name")
		name.text = 'lb'
		print(name.text)
		pause()

		source = root.find("./devices/disk/source")
		print(source.get("file"))
		source.set("file", "/home/daniel.sanz.sobrino/PracticaLibre1/lb.qcow2")
		print(source.get("file"))
		pause()

		source_bridge = root.find("./devices/interface[@type='bridge']/source")
		print(source_bridge.get("bridge"))
		source_bridge.set("bridge", "LAN1")
		print(source_bridge.get("bridge"))
		pause()

		source_bridge1 = root.find("./devices")
		interface = etree.Element("interface")
		interface.set("type", "bridge")
		source = etree.Element("source")
		source.set("bridge", "LAN2")
		model = etree.Element("model")
		model.set("type","virtio")
		interface.append(source)
		interface.append(model)
		source_bridge1.append(interface)
		print('He metido interface')
		pause()
		
		f = open('lb.xml', 'w')
		f.write(etree.tounicode(tree, pretty_print=True))
		f.close()
		pause()

		#configuramos LANs
		call(['sudo','brctl','addbr','LAN1'])
		call(['sudo','brctl','addbr','LAN2'])
		call(['sudo','ifconfig','LAN1','up'])
		call(['sudo','ifconfig','LAN2','up'])

		#cambiamos hostname
		h = 1
		while h <= int(aux):
			f = open("hostname", 'w')
			f.write('s'+str(h)+' \n')
			f.close()
			call(['sudo','virt-copy-in', '-a', 's'+str(h)+'.qcow2', 'hostname', '/etc'])
			call(['sudo','virt-cat', '-a', 's'+str(h)+'.qcow2', '/etc/hostname'])
			call(['rm','hostname'])
			h = h+1

		f = open("hostname", 'w')
		f.write("c1 \n")
		f.close()
		call(['sudo','virt-copy-in', '-a', 'c1.qcow2', 'hostname', '/etc'])
		call(['sudo','virt-cat', '-a', 'c1.qcow2', '/etc/hostname'])

		call(['rm','hostname'])
		f = open("hostname", 'w')
		f.write("lb \n")
		f.close()
		call(['sudo','virt-copy-in', '-a', 'lb.qcow2', 'hostname', '/etc'])
		call(['sudo','virt-cat', '-a', 'lb.qcow2', '/etc/hostname'])
		call(['rm','hostname'])

		call(['sudo','virt-copy-out','-a','s1.qcow2','/etc/hosts','.'])
		call(['mv','hosts','hosts1'])
		p = 1
		
		while p <= int(aux):
			f1 = open("hosts1", 'r')
			f2 = open("hosts", 'w')
			for line in f1:
				if '127.0.1.1' in line:
					f2.write('127.0.1.1 s'+str(p)+' \n')
				else:
					f2.write(line)

			f1.close()
			f2.close()
			call(['sudo','virt-copy-in', '-a', 's'+str(p)+'.qcow2', 'hosts', '/etc'])
			call(['sudo','virt-cat', '-a', 's'+str(p)+'.qcow2', '/etc/hosts'])
			call(['rm','hosts'])
			p = p+1

		f1 = open("hosts1", 'r')
		f2 = open("hosts", 'w')
		for line in f1:
			if '127.0.1.1' in line:
				f2.write('127.0.1.1 c1 \n')
			else:
				f2.write(line)

		f1.close()
		f2.close()
		call(['sudo','virt-copy-in', '-a', 'c1.qcow2', 'hosts', '/etc'])
		call(['sudo','virt-cat', '-a', 'c1.qcow2', '/etc/hosts'])
		call(['rm','hosts'])
		



		f1 = open("hosts1", 'r')
		f2 = open("hosts", 'w')
		for line in f1:
			if '127.0.1.1' in line:
				f2.write('127.0.1.1 lb \n')
			else:
				f2.write(line)

		f1.close()
		f2.close()
		call(['sudo','virt-copy-in', '-a', 'lb.qcow2', 'hosts', '/etc'])
		call(['sudo','virt-cat', '-a', 'lb.qcow2', '/etc/hosts'])
		call(['rm','hosts'])
		

		#cambiar interfaces
		l = 1
		while l <= int(aux):
			f1 = open('interfaces','w')
			f1.write('\n auto lo \n iface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.0.2.1'+str(l)+' \n netmask 255.255.255.0 \n gateway 10.0.2.1 \n ')
			f1.close()
			call(['sudo','virt-copy-in', '-a', 's'+str(l)+'.qcow2', 'interfaces', '/etc/network'])
			call(['sudo','virt-cat', '-a', 's'+str(l)+'.qcow2', '/etc/network/interfaces'])
			call(['rm','interfaces'])
			l = l+1

		f1 = open('interfaces','w')
		f1.write('\n auto lo \n iface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.0.1.2 \n netmask 255.255.255.0 \n gateway 10.0.1.1 \n ')
		f1.close()
		call(['sudo','virt-copy-in', '-a', 'c1.qcow2', 'interfaces', '/etc/network'])
		call(['sudo','virt-cat', '-a', 'c1.qcow2', '/etc/network/interfaces'])
		call(['rm','interfaces'])


		f1 = open('interfaces','w')
		f1.write('\n auto lo \n iface lo inet loopback \n auto eth0 \n iface eth0 inet static \n address 10.0.1.1 \n netmask 255.255.255.0 \n auto eth1 \n iface eth1 inet static \n address 10.0.2.1 \n netmask 255.255.255.0 \n ')
		f1.close()
		call(['sudo','virt-copy-in', '-a', 'lb.qcow2', 'interfaces', '/etc/network'])
		call(['sudo','virt-cat', '-a', 'lb.qcow2', '/etc/network/interfaces'])
		call(['rm','interfaces'])

		call(['sudo','ifconfig','LAN1','10.0.1.3/24'])
		call(['sudo','ip','route','add','10.0.0.0/16','via','10.0.1.1'])

		#cambio ip_forward
		call(["sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'"], shell=True)

		#cambiar index.html		
		x = 1
		while x <= int(aux):
			f1 = open('index.html','w')
			f1.write('S'+str(x)+' \n')
			f1.close()
			call(['sudo','virt-copy-in', '-a', 's'+str(x)+'.qcow2', 'index.html', '/var/www/html'])
			call(['sudo','virt-cat', '-a', 's'+str(x)+'.qcow2', '/var/www/html/index.html'])
			call(['rm','index.html'])
			x = x+1

		d = 1
		while d <= int(aux):
			call(['sudo', 'virsh', 'define', 's'+str(d)+'.xml'])
			d = d+1
		call(['sudo', 'virsh', 'define', 'lb.xml'])
		call(['sudo', 'virsh', 'define', 'c1.xml'])

elif orden == 'launch' and len(sys.argv) == 2:

	#Sacamos el valor del json
	f = open('auto-p2.json', 'r')
	content = f.read()
	jsondecoded = json.loads(content)
	for server in jsondecoded['servers']:
		nserver = server['num_serv']
	print('El numero de servidores es '+nserver)

	n = 1
	while n <= int(nserver):
		call(['sudo','virsh','start','s' + str(n)])	
		call(['xterm -e "sudo virsh console s' +str(n)+ '" &'], shell=True)
		n = n+1
	call(['sudo','virsh','start','c1'])
	call(['sudo','virsh','start','lb'])
	call(['xterm -e "sudo virsh console c1" &'],shell=True)
	call(['xterm -e "sudo virsh console lb" &'],shell=True)
	


elif orden == 'stop' and len(sys.argv) == 2:

	#Sacamos el valor del json
	f = open('auto-p2.json', 'r')
	content = f.read()
	jsondecoded = json.loads(content)

	for server in jsondecoded['servers']:
		nserver = server['num_serv']
	print('El número de servidores es '+nserver)	

	n = 1
	while n <= int(nserver):	
		call(['sudo', 'virsh', 'shutdown', 's'+str(n)])
		n = n+1
	call(['sudo', 'virsh', 'shutdown', 'lb'])
	call(['sudo', 'virsh', 'shutdown', 'c1'])

	print('Servidores parados')

elif orden == 'release' and len(sys.argv) == 2:

	#Sacamos el valor del json
	f = open('auto-p2.json', 'r')
	content = f.read()
	jsondecoded = json.loads(content)

	for server in jsondecoded['servers']:
		nserver = server['num_serv']
	print('El número de servidores es '+nserver)	

	print('Destruyo'+nserver+' servidores')	

	n = 1
	while n <= int(nserver):	
		call(['sudo', 'virsh', 'destroy', 's'+str(n)])
		call(['sudo', 'virsh', 'undefine', 's'+str(n)])
		call(['rm','s'+str(n)+'.xml'])
		call(['rm','s'+str(n)+'.qcow2'])
		n = n+1
	call(['sudo', 'virsh', 'destroy', 'lb'])
	call(['sudo', 'virsh', 'undefine', 'lb'])
	call(['sudo', 'virsh', 'destroy', 'c1'])
	call(['sudo', 'virsh', 'undefine', 'c1'])
	call(['rm','lb.xml'])
	call(['rm','c1.xml'])
	call(['rm','lb.qcow2'])
	call(['rm','c1.qcow2'])
	call(['rm','hosts1'])
	call(['rm','auto-p2.json'])

	print('Espacio liberado y todos los ficheros se han borrado')

else:
	print('Por favor introduce un parámetro válido')
