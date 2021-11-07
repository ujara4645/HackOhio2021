var apiKey = 'AIzaSyBdKi-B515pg9hGVwZZaI_hBklCvpxGO-4';

var map;
var snappedData;
var current = 0;
var line;

function initMap() {
  var mapOptions = {
    zoom: 17,
    center: {lat: 40.0082672, lng: -83.0072693}
  };
  map = new google.maps.Map(document.getElementById("map"), mapOptions);
}

function main() {
  $("#submit").on("click", submit);
  $("#forward").on("click", nextPath);
  $("#backward").on("click", prevPath);
}

function nextPath() {
  line.setMap(null);
  current = (current + 1) % snappedData.length;
  setPath(snappedData[current]);
}

function prevPath() {
  line.setMap(null);
  current = (current - 1 + snappedData.length) % snappedData.length;
  setPath(snappedData[current]);
}

function setPath(data) {
  const result = processSnapToRoadResponse(data);
  line = drawSnappedPolyline(result.coords);
  line.setMap(map);
}

function apiHandler(result) {
  if(result['status'] != 200) {
    alert("error: " + result['message']);
  }

  snappedData = [];

  for(var i = 0; i < result.paths.length; i++) {
    const pathValues = [];
    for(var j = 0; j < result.paths[i][1].length; j++) {
      if (pathValues.length < 100) {
        pathValues.push(result.paths[i][1][j].house.lat + "," + result.paths[i][1][j].house.long)
      }
    }

    $.get('https://roads.googleapis.com/v1/snapToRoads', {
      interpolate: true,
      key: apiKey,
      path: pathValues.join('|')
    }, function(d) {
      snappedData.push(d)
    });
  }

  setTimeout(function() { 
    setPath(snappedData[0]);
  }, 1000);

}

function processSnapToRoadResponse(data) {
  const snappedCoordinates = [];
  const placeIdArray = [];
  for (var i = 0; i < data.snappedPoints.length; i++) {
    const latlng = new google.maps.LatLng(
      data.snappedPoints[i].location.latitude,
      data.snappedPoints[i].location.longitude,
    );
    snappedCoordinates.push(latlng);
    placeIdArray.push(data.snappedPoints[i].placeId);
  }
  return {coords: snappedCoordinates, places: placeIdArray};
}

function drawSnappedPolyline(coords) {
  const snappedPolyline = new google.maps.Polyline({
    path: coords,
    strokeColor: '#bb0000',
    strokeWeight: 4,
    strokeOpacity: 0.9,
  });

  return snappedPolyline;
}


function submit() {
  const loc = $('#address').val() + " " + $("#city").val()
  const radius = $('#radius').val() 
  const distance = $('#distance').val() 

  console.log("sending api request");

  $.get("/api/routes", {location: loc, radius: radius, distance: distance}, apiHandler);
}

window.addEventListener("load", main, false);
