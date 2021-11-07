var apiKey = 'AIzaSyBdKi-B515pg9hGVwZZaI_hBklCvpxGO-4';

var map;

function initMap() {
  var mapOptions = {
    zoom: 17,
    center: {lat: 40.0082672, lng: -83.0072693}
  };
  map = new google.maps.Map(document.getElementById("map"), mapOptions);
}

function main() {
  $("#button").on("click", submit);
}

function apiHandler(result) {
  if(result['status'] != 200) {
    alert("error: " + result['message']);
  }

  console.log(result);

  for(var i = 0; i < result.paths.length; i++) {
    const pathValues = [];
    for(var j = 0; j < result.paths[i][1].length; j++) {
      pathValues.push(result.paths[i][1][j].house.lat + "," + result.paths[i][1][j].house.long)
    }

    $.get('https://roads.googleapis.com/v1/snapToRoads', {
      interpolate: true,
      key: apiKey,
      path: pathValues.join('|')
    }, function(data) {
      console.log(data)
      const result = processSnapToRoadResponse(data);
      const line = drawSnappedPolyline(result.coords);
      line.setMap(map);
    });
  }
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
    strokeColor: '#add8e6',
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
