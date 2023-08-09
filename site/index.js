//package com.mkyong;

//import java.io.IOException;
//import java.nio.file.Files;
//import java.nio.file.Paths;

 // Import the Scanner class to read text files
while(true)
    {
// Create root element
// https://www.amcharts.com/docs/v5/getting-started/#Root_element
var root = am5.Root.new("chartdiv");


// Set themes
// https://www.amcharts.com/docs/v5/concepts/themes/
root.setThemes([
  am5themes_Animated.new(root)
]);


// Create chart
// https://www.amcharts.com/docs/v5/charts/radar-chart/
var chart = root.container.children.push(am5radar.RadarChart.new(root, {
  panX: false,
  panY: false,
  wheelX: "panX",
  wheelY: "zoomX"
}));

// Add cursor
// https://www.amcharts.com/docs/v5/charts/radar-chart/#Cursor
var cursor = chart.set("cursor", am5radar.RadarCursor.new(root, {
  behavior: "zoomX"
}));

cursor.lineY.set("visible", false);


// Create axes and their renderers
// https://www.amcharts.com/docs/v5/charts/radar-chart/#Adding_axes
var xRenderer = am5radar.AxisRendererCircular.new(root, {});
xRenderer.labels.template.setAll({
  radius: 10
});

var xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
  maxDeviation: 0,
  categoryField: "category",
  renderer: xRenderer,
  tooltip: am5.Tooltip.new(root, {})
}));

var yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
  renderer: am5radar.AxisRendererRadial.new(root, {})
}));


// Create series
// https://www.amcharts.com/docs/v5/charts/radar-chart/#Adding_series
var series = chart.series.push(am5radar.RadarLineSeries.new(root, {
  name: "Series",
  xAxis: xAxis,
  yAxis: yAxis,
  valueYField: "value",
  categoryXField: "category",
  tooltip: am5.Tooltip.new(root, {
    labelText: "{valueY}"
  })
}));

series.bullets.push(function () {
  return am5.Bullet.new(root, {
    sprite: am5.Circle.new(root, {
      radius: 5,
      fill: series.get("fill")
    })
  });
});


// Add scrollbars
chart.set("scrollbarX", am5.Scrollbar.new(root, { orientation: "horizontal" }));
chart.set("scrollbarY", am5.Scrollbar.new(root, { orientation: "vertical" }));


// Generate and set data
// https://www.amcharts.com/docs/v5/charts/radar-chart/#Setting_data
var i = -1;
var value = 10;


function load() {
var request;

if (window.XMLHttpRequest) { // Firefox
	request = new XMLHttpRequest();
}
else if (window.ActiveXObject) { // IE
	request = new ActiveXObject("Microsoft.XMLHTTP");
}
else {
	return; // Non supporte
}	

request.open('GET', 'test.txt', false); // Synchro
request.send(null);

return request.responseText;
}


function generateData() {

    value = load();//"12345698"  //Math.round((Math.random() * 4 - 2) + 
    
    i++;
    
    var j=i;
    //while (value[j] != ',')
      //  {
        //    j++;
        //}
    
    //value[i]=parseInt(value[i])
    if (value[j] != ",")
    {
         return {
        category: "cat" + i,
        value: parseInt(value[i])//text[i]
        }
    }
    else
    {
        j=j+1
    }

  //};
}

function pausecomp(millis)
{
    var date = new Date();
    var curDate = null;
    do { curDate = new Date(); }
    while(curDate-date < millis);
}

function generateDatas(count) {
   //[1,1,2,3,3,3,3,4,4,4,6,7];

        f=load()
        var n =0;
        var sto=0;
        var data =[];
    for (var j = 0; j < f.length; j++)
        {



        if(f.slice(j,j+1) =="\n"){

        val=f.slice(sto,j);
        data.push({category: "" + n,
        value: parseInt(val)});
        //var data =[]
        n=n+1;
        sto=j+1
        }



        }
        series.data.setAll(data);
        xAxis.data.setAll(data);
  
}


generateDatas(360);
//location.reload();

series.appear(1000);
chart.appear(1000, 100);
        pausecomp(50)
}
// Animate chart and series in
// https://www.amcharts.com/docs/v5/concepts/animations/#Forcing_appearance_animation
        

