# TP N2: Software-Defined Networks
Introducción a los Sistemas Distribuidos (75.43)

* Stephanie Ingrid Izquierdo Osorio

* Valentina Laura Correa

* Pablo Salvador Dimartino

* Agustin Ariel Andrade

* Juan Sebastian Burgos

## Ejecucion

### Firewall

Para poder ejecutar el programa es necesario situarse dentro de \textbf{\textbackslash{TP2}} y correr el comando:

```
python3 pox/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning misc.controller
```

El cual no solo levanta la herramienta POX sino que además se le indica el nivel de log del programa y también se lo configura para que aprenda automaticamente
la topología seteada por properties.

### Topología

A su vez, en una nueva terminal y tambien desde la ruta \textbf{\textbackslash{TP2}}, deberemos correr:

```
sudo mn --custom ./topology.py --topo customTopo,switches=5  --mac --arp -x --switch ovsk --controller remote
```

En donde utilizando mininet (mn) podremos setear para nuestra topologia (customTopo) la cantidad de switches deseada (switches=n).

Se podrá visualizar que se abre una terminal xterm para cada host virtual, switches y el controlador. Se observara los eventos de alta de switches en el log del controlador pox.

### Testing

#### Bloqueo a cualquier host con puerto destino 80

Comenzamos levantando una conexion en el host 1 en el puerto 80 y a traves del protocolo udp. Una vez levantada esta, procedemos a probar su conexion con un cliente establecido desde el host 3

En la terminal del host 1:

```
iperf -s -p 80 -u
```

La salida esperada es:

```
------------------------------------------------------------
Server listening on UDP port 80
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
```

En la terminal del host 3:

```
iperf -c 10.0.0.1 -p 80 -u
```

Se espera una salida similar a la siguiente, indicando que el envio no fue posible. Esto demuestra que el filtro actua de manera correcta.

````
------------------------------------------------------------
Client connecting to 10.0.0.1, UDP port 80
Sending 1470 byte datagrams, IPG target: 11215.21 us (kalman adjust)
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
[  1] local 10.0.0.3 port 35221 connected with 10.0.0.1 port 80
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0153 sec  1.25 MBytes  1.05 Mbits/sec
[  1] Sent 896 datagrams
[  5] WARNING: did not receive ack of last datagram after 10 tries.

````

Veremos que la regla se aplicaya que no se logra establecer la comunicación. Podemos probar además con TCP removiendo el flag `-u` para demostrar que la regla aplica para ambos protocolos de transporte.

#### Bloqueo de paquetes UDP provenientes del host1 con puerto destino 5001

Iniciamos un servidor que responda a los mensajes UDP en el puerto 5501 en el host 3:

````
iperf -s -p 5001 -u`
````

Con una salida:

```
------------------------------------------------------------
Server listening on UDP port 5001
UDP buffer size:  208 KByte (default)
------------------------------------------------------------

```

Y luego nos intentamos conectar desde el host 1: 

````
iperf -u -c 10.0.0.1 -p 5001 -u
````

Se podra ver que ocurrió un timeout debido a que al intentar enviar paquetes que cumplen con los clientes filtros de la regla, estos nunca llegan a destino:

```
------------------------------------------------------------
Client connecting to 10.0.0.3, UDP port 5001
Sending 1470 byte datagrams, IPG target: 11215.21 us (kalman adjust)
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
[  1] local 10.0.0.1 port 47025 connected with 10.0.0.3 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0153 sec  1.25 MBytes  1.05 Mbits/sec
[  1] Sent 896 datagrams
[  5] WARNING: did not receive ack of last datagram after 10 tries.

```

#### Bloqueo de paquetes entre dos hosts elegidos arbitrariamente

En este trabajo practico decidimos bloquear la conexion entre el host 1 y el host 4, aunque al haber hecho esta configuracion a traves de un archivo de properties, el cambio de los mismos se puede realizar facilmente.

Al ejecutar `pingall` en la terminal de mininet, notamos como desde host_1 no se puede acceder a host_4  y viceversa.

En la consola de mininet ejecutar

````
pingall
````

La salida esperada es la siguiente, indicando que la comunicacion entre el host 1 y el host 4 no fue posible:

````
*** Ping: testing ping reachability
host_1 -> host_2 host_3 X 
host_2 -> host_1 host_3 host_4 
host_3 -> host_1 host_2 host_4 
host_4 -> X host_2 host_3 
*** Results: 16% dropped (10/12 received)

````
