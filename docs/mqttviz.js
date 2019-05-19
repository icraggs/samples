
function initGui() {
    var gui = new dat.GUI({ width: 280 });
    var api = { 'speed': 0.05, };
    var folder = gui.addFolder('menu');
    folder.add(api, 'speed', 0.01, 0.1, 0.01).onChange(function () {
        speed = api.speed;
    });
    folder.open();
    return gui;
}

function links(pointX, pointY) {
    console.log("mqttviz link");
    var material = new THREE.MeshLambertMaterial({ color: new THREE.Color("azure") });
    var direction = new THREE.Vector3().subVectors(pointY, pointX);
    var orientation = new THREE.Matrix4();
    orientation.lookAt(pointX, pointY, new THREE.Object3D().up);
    orientation.multiply(new THREE.Matrix4().set(1, 0, 0, 0,
        0, 0, 1, 0,
        0, -1, 0, 0,
        0, 0, 0, 1));
    var edgeGeometry = new THREE.CylinderGeometry(.1, .1, direction.length(), 8, 1);
    var edge = new THREE.Mesh(edgeGeometry, material);
    edge.applyMatrix(orientation);
    // position based on midpoints - there may be a better solution than this
    edge.position.x = (pointY.x + pointX.x) / 2;
    edge.position.y = (pointY.y + pointX.y) / 2;
    edge.position.z = (pointY.z + pointX.z) / 2;
    return edge;
}

function sphere(size = 1.5, color = new THREE.Color("skyblue")) {
    material = new THREE.MeshLambertMaterial({ color: color });

    const sphere = new THREE.Mesh(
        new THREE.IcosahedronBufferGeometry(size, 4), material);

    sphere.receiveShadow = true;
    return sphere;
}

function add_label(obj, text) {
    var div = document.createElement('div');
    div.className = 'label';
    div.textContent = text;
    div.style.marginTop = '-1em';
    var label = new THREE.CSS2DObject(div);
    label.position.set(0, 0.3, 0);
    obj.add(label);
    obj.label = label;
    obj.textContent = text;
}

function create_client(text, broker) {
    client = sphere(0.5, new THREE.Color("seagreen"));
    client.position.x = Math.random() * 10;
    client.position.y = Math.random() * 10;
    client.position.z = Math.random() * 10;
    add_label(client, text);
    scene.add(client);
    client.link = links(broker.position, client.position);
    scene.add(client.link);
    return client;
}

function create_broker(text) {
    var broker = sphere(0.8);
    /*broker.position.x = 0;
    broker.position.y = 0;
    broker.position.z = 0;*/
    console.log("broker position", broker.position);
    add_label(broker, text);
    scene.add(broker);
    return broker;
}

function create_packet(clientid, start, end, text = 'Publish') {
    var packet = sphere(0.3, new THREE.Color("pink"))
    add_label(packet, text);

    var direction = new THREE.Vector3().subVectors(end, start);
    packet.distance = start.distanceTo(end);
    packet.vector = direction.multiplyScalar(speed, speed, speed);
    packet.position.copy(start);
    packet.start = start.clone();
    packet.clientid = clientid;

    scene.add(packet);
    return packet;
}

function create_room() {
    var aroom = new THREE.LineSegments(
        new THREE.BoxLineGeometry(60, 60, 60, 10, 10, 10),
        new THREE.LineBasicMaterial({ color: 0x808080 })
    );
    //aroom.geometry.translate(0, 3, 0);
    scene.add(aroom);
    return aroom;
}

function controllers() {
    function onSelectStart() {
		this.userData.isSelecting = true;
	}
	function onSelectEnd() {
		this.userData.isSelecting = false;
	}
	controller1 = renderer.vr.getController( 0 );
	controller1.addEventListener( 'selectstart', onSelectStart );
	controller1.addEventListener( 'selectend', onSelectEnd );
	scene.add( controller1 );
	controller2 = renderer.vr.getController( 1 );
	controller2.addEventListener( 'selectstart', onSelectStart );
	controller2.addEventListener( 'selectend', onSelectEnd );
	scene.add( controller2 );
	// helpers
	var geometry = new THREE.BufferGeometry();
	geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( [ 0, 0, 0, 0, 0, - 1 ], 3 ) );
	geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( [ 0.5, 0.5, 0.5, 0, 0, 0 ], 3 ) );
	var material = new THREE.LineBasicMaterial( { vertexColors: true, blending: THREE.AdditiveBlending } );
	controller1.add( new THREE.Line( geometry, material ) );
	controller2.add( new THREE.Line( geometry, material ) );
}

function next_frame() {

    if (curpacket == null && message_queue.length == 0) {
        renderer.render(scene, camera);
        labelRenderer.render(scene, camera);
        return;
    }

    if (curpacket == null) {
        var obj = message_queue.shift();

        if (obj.clientid != "" && !Object.keys(clients).includes(obj.clientid)) {
            clients[obj.clientid] = create_client(obj.clientid, broker1);
        }
        var client = clients[obj.clientid];

        var text = obj.packet.fh.PacketType;
        var property_string = JSON.stringify(obj.packet.Properties)
        if (text == "Publishes") {
            //console.log(Object.keys(obj.packet));
            text += " " + obj.direction + " qos:" + obj.packet.fh.QoS + " " + obj.packet.Payload;
            if (property_string != '{}')
                text += " " + property_string;
        }
        else if (text == "Subscribes") {
            //console.log(Object.keys(obj.packet));
            text += " " + JSON.stringify(obj.packet.Data)/*[0][0]*/;
            if (property_string != '{}')
                text += " " + property_string;
        }
        if (obj.packet.PacketId != undefined) {
            text += " id:" + obj.packet.PacketId;
        }

        console.log(obj.clientid, text);
        if (obj.direction == "StoC") {
            curpacket = create_packet(obj.clientid, broker1.position, client.position, text);
        } else {
            curpacket = create_packet(obj.clientid, client.position, broker1.position, text);
        }
    }

    curpacket.position.x += curpacket.vector.x;
    curpacket.position.y += curpacket.vector.y;
    curpacket.position.z += curpacket.vector.z;

    if (curpacket.position.distanceTo(curpacket.start) >= curpacket.distance) {
        curpacket.remove(curpacket.label);
        scene.remove(curpacket);
        var clientid = curpacket.clientid;

        if (curpacket.textContent == "Disconnects" &&
            Object.keys(clients).includes(clientid)) {
            //console.log("removing client", clientid);
            client = clients[clientid];
            client.link.remove(client.link.label);
            scene.remove(client.link);
            client.remove(client.label);
            scene.remove(client);
            delete clients[clientid];
            //console.log("clients after delete of", clientid, ":", Object.keys(clients));
        }
        curpacket = null;
    }
    return curpacket;
}
