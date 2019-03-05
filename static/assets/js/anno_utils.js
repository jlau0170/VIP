var annotations_map = new Object()

function generate_id(annotation) {
  var id = annotation.text.substring(0,1) + annotation.text.length;
  var randint = Math.floor(Math.random() * 10000);
  id += randint + annotation.text.substring(annotation.text.length - 1, annotation.text.length);
  return id;
}

function store_annotations() {
  for (var key in annotations_map) {
    var username = firebase.auth().currentUser.email.split('@')[0];
    firebase.database().ref('users/' + username + '/' + key).set(annotations_map[key]);
  }
}

function store_vid_annotations(timestamp, vid_anno) {
  // var time = document.getElementById("timestamp")
  // var vid_anno = document.getElementById("vid_anno")
  console.log(typeof(timestamp))
  console.log(vid_anno)
  if (!timestamp || /^\s*$/.test(timestamp)) {
    alert("Please input a time.")
  } else {
    // input into database
    alert("Your annotation has been recorded.")
  }
}

var mA = {
  src : 'http://127.0.0.1:5000/static/images/dog-park.jpg',
  text : 'My annotation',
  shapes : [{
      type : 'rect',
      geometry : { x : 0.1, y: 0.1, width : 0.4, height: 0.3 }
  }]
}

function populate(arr) {
  // arr = [populated_annos, points]
  // console.log(points1)
  populated_annos1 = arr[0]
  points1 = arr[1]
  console.log(arr[0])
  console.log(arr[1])

  // if (typeof populated_annos1 == 'undefined'):
  //   alert("There are no annotations to show.")
  //   return
  if (points1 >= 10) {
    var annotationBox = document.getElementById("annotationBox")
    annotationBox.style.display = "block"
    console.log(annotationBox.style.display)
    annotationBox.value = populated_annos1
  } else {
    alert("You don't have enough points.")
  }
  for (var i = 0; i < populated_annos1.length; i++) {
    var myAnno = {
      src : populated_annos1[i].src,
      text : populated_annos1[i].text,
      shapes : [{
        type : populated_annos1[i].shapes[0].type,
        geometry : populated_annos1[i].shapes[0].geometry
      }]
    }
    anno.addAnnotation(myAnno);
  }
}

function handle_data() {
  //anno.addAnnotation(myAnnotation)
  anno.addHandler('onAnnotationCreated', function(annotation) {
    var geometry = annotation.shapes[0].geometry;
    console.log(annotation);
    unique_id = generate_id(annotation);
    annotations_map[unique_id] = annotation;
    console.log(annotations_map);
  });
  anno.addHandler('onAnnotationRemoved', function(annotation) {
    var del_id = 0;
    var found = false;
    for (var key in annotations_map) {
      console.log(annotations_map);
      console.log(key);
      if (annotations_map[key].shapes[0].geometry == annotation.shapes[0].geometry) {
        found = true;
        del_id = i;
      }
    }
    if (del_id > -1 && found) {
      delete annotations_map[del_id];
    }
  });
  anno.addHandler('onAnnotationUpdated', function(annotation) {
    var update_id = 0;
    var found = false;
    for (var key in annotations_map) {
      if (annotations_map[key].shapes[0].geometry == annotation.shapes[0].geometry) {
        found = true;
        update_id = i;
      }
    }
    if (update_id > -1 && found) {
      annotations_map[update_id] = annotation;
    }
  });
}
