var can, ctx, xScalar, yScalar, y;

function buildChart(sLog){
    // parse dates and temperatures
    
    var logs = sLog.split(","); 
    
    var dates = new Array();
    var temps = new Array();
    var c = 0;
    for (i = 0; i < logs.length; i += 2) {
        dates[c] = new Date(logs[i]);
        temps[c] = Number(logs[i + 1]);
        c += 1;
    }

    // set these values for your data
    var numSamples = temps.length;
    var minVal = 55
    var maxVal = 95;
    var stepSize = 5;
    var colFoot = 20
    var colHead = 20;
    var rowHead = 30;
    var xInterval = 1;
    can = document.getElementById("canvasChart");
    ctx = can.getContext("2d");
    // background
    ctx.fillStyle = "black";
    ctx.fillRect(0,0,can.width, can.height);
    ctx.fillStyle = "White";
    yScalar = (can.height - (colHead + colFoot)) / (maxVal-minVal);
    xScalar = (can.width - rowHead) / (numSamples);
    ctx.strokeStyle = "White"; 
    ctx.beginPath();
    // row header and draw horizontal grid lines
    ctx.font = "12pt Helvetica"
    var count = 0;
    // draw from top to bottom
    for (scale = maxVal; scale >= minVal; scale -= stepSize) {
        y = colHead + (yScalar * count * stepSize);
        if (scale > 80) {
            ctx.fillStyle = "PaleVioletRed";
        }
        else if (scale > 70) {
            ctx.fillStyle = "Aquamarine";
        }
        else if (scale > 55) {
            ctx.fillStyle = "PowderBlue";
        }
        else {
            ctx.fillStyle = "Transparent";
        }
        ctx.fillRect(rowHead - 10, y, can.width, yScalar * stepSize);
        ctx.fillStyle = "White";
        ctx.fillText(scale, 0, y + stepSize);
        ctx.moveTo(rowHead - 10, y);
        ctx.lineTo(can.width, y);
        count++;
    }
    ctx.stroke();
    // label samples
    ctx.font = "9pt Helvetica";
    ctx.textBaseline = "bottom";

    // translate to bottom of graph
    ctx.translate(rowHead, can.height);

    // draw labels
    for (i = 0; i < numSamples; i++) {
        calcY(temps[i] - minVal);
        if (i % xInterval == 0) {
            ctx.fillText((dates[i].getHours() < 10 ? '0' : '') + dates[i].getHours(), xScalar * (i), 0);
        }
    }
    // set a color and a shadow
    ctx.fillStyle = "Yellow";
    ctx.shadowColor = "Grey";
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;
    // translate to column footer of graph
    ctx.translate(0, -colFoot);
    //scale x,y to match data
    ctx.scale(xScalar, -1 * yScalar);
    // draw bars
    for (i = 0; i < numSamples; i++) {
        ctx.fillRect(i, 0, .5, temps[i] - minVal);
    }
}


function calcY(value) {
    y = can.height - value * yScalar;
}
