// Animation

var planeRoute1 = JSON.parse('[{"lat":56.7584994,"lng":0.7277719},{"lat":43.000000,"lng":-75.000000}]');

var seqGroup = L.motion.seq([
    L.motion.seq([
        L.motion.polyline(planeRoute1, {
            color:"indigo"
        }, null, {
            removeOnEnd: false,
            icon: L.divIcon({html: "<i class='fa fa-plane fa-2x' aria-hidden='true' motion-base='-43'></i>", iconSize: L.point(19, 24)})
        }).motionDuration(5000),
    ])
]).addTo(map);

setTimeout(function () {
    seqGroup.motionStart();
}, 1000);
